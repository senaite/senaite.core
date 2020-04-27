# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections
import sys
import threading

from AccessControl.SecurityInfo import ModuleSecurityInfo
from bika.lims import PMF
from bika.lims import api
from bika.lims import logger
from bika.lims.browser import ulocalized_time
from bika.lims.decorators import synchronized
from bika.lims.interfaces import IActionHandlerPool, IGuardAdapter
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.jsonapi import get_include_fields
from bika.lims.utils import changeWorkflowState  # noqa
from bika.lims.utils import t
from bika.lims.workflow.indexes import ACTIONS_TO_INDEXES
from itertools import groupby
from Products.Archetypes.config import UID_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import getAdapters
from zope.interface import implements
from ZPublisher.HTTPRequest import HTTPRequest

security = ModuleSecurityInfo('bika.lims.workflow')
security.declarePublic('guard_handler')

_marker = object()


def skip(instance, action, peek=False, unskip=False):
    """Returns True if the transition is to be SKIPPED

        peek - True just checks the value, does not set.
        unskip - remove skip key (for manual overrides).

    called with only (instance, action_id), this will set the request variable
    preventing the cascade's from re-transitioning the object and return None.
    """

    uid = callable(instance.UID) and instance.UID() or instance.UID
    skipkey = "%s_%s" % (uid, action)
    if 'workflow_skiplist' not in instance.REQUEST:
        if not peek and not unskip:
            instance.REQUEST['workflow_skiplist'] = [skipkey, ]
    else:
        if skipkey in instance.REQUEST['workflow_skiplist']:
            if unskip:
                instance.REQUEST['workflow_skiplist'].remove(skipkey)
            else:
                return True
        else:
            if not peek and not unskip:
                instance.REQUEST["workflow_skiplist"].append(skipkey)


def doActionFor(instance, action_id, idxs=None):
    """Tries to perform the transition to the instance.
    Object is reindexed after the transition takes place, but only if succeeds.
    If idxs is set, only these indexes will be reindexed. Otherwise, will try
    to use the indexes defined in ACTIONS_TO_INDEX mapping if any.
    :param instance: Object to be transitioned
    :param action_id: transition id
    :param idxs: indexes to be reindexed after the transition
    :returns: True if the transition has been performed, together with message
    :rtype: tuple (bool,str)
    """
    if not instance:
        return False, ""

    if isinstance(instance, list):
        # TODO Workflow . Check if this is strictly necessary
        # This check is here because sometimes Plone creates a list
        # from submitted form elements.
        logger.warn("Got a list of obj in doActionFor!")
        if len(instance) > 1:
            logger.warn(
                "doActionFor is getting an instance parameter which is a list "
                "with more than one item. Instance: '{}', action_id: '{}'"
                .format(instance, action_id)
            )

        return doActionFor(
            instance=instance[0], action_id=action_id, idxs=idxs)

    # Since a given transition can cascade or promote to other objects, we want
    # to reindex all objects for which the transition succeed at once, at the
    # end of process. Otherwise, same object will be reindexed multiple times
    # unnecessarily.
    # Also, ActionsHandlerPool ensures the same transition is not applied twice
    # to the same object due to cascade/promote recursions.
    pool = ActionHandlerPool.get_instance()
    if pool.succeed(instance, action_id):
        return False, "Transition {} for {} already done"\
             .format(action_id, instance.getId())

    # Return False if transition is not permitted
    if not isTransitionAllowed(instance, action_id):
        return False, "Transition {} for {} is not allowed"\
            .format(action_id, instance.getId())

    # Add this batch process to the queue
    pool.queue_pool()
    succeed = False
    message = ""
    workflow = getToolByName(instance, "portal_workflow")
    try:
        workflow.doActionFor(instance, action_id)
        succeed = True
    except WorkflowException as e:
        message = str(e)
        curr_state = getCurrentState(instance)
        clazz_name = instance.__class__.__name__
        logger.warning(
            "Transition '{0}' not allowed: {1} '{2}' ({3})"
            .format(action_id, clazz_name, instance.getId(), curr_state))
        logger.error(message)

    # If no indexes to reindex have been defined, try to use those defined in
    # the ACTIONS_TO_INDEXES mapping. Reindexing only those indexes that might
    # be affected by the transition boosts the overall performance!.
    if idxs is None:
        portal_type = instance.portal_type
        idxs = ACTIONS_TO_INDEXES.get(portal_type, {}).get(action_id, [])

    # Add the current object to the pool and resume
    pool.push(instance, action_id, succeed, idxs=idxs)
    pool.resume()

    return succeed, message


def call_workflow_event(instance, event, after=True):
    """Calls the instance's workflow event
    """
    if not event.transition:
        return False

    portal_type = instance.portal_type
    wf_module = _load_wf_module('{}.events'.format(portal_type.lower()))
    if not wf_module:
        return False

    # Inspect if event_<transition_id> function exists in the module
    prefix = after and "after" or "before"
    func_name = "{}_{}".format(prefix, event.transition.id)
    func = getattr(wf_module, func_name, False)
    if not func:
        return False

    logger.info('WF event: {0}.events.{1}'
                .format(portal_type.lower(), func_name))
    func(instance)
    return True


def BeforeTransitionEventHandler(instance, event):
    """ This event is executed before each transition and delegates further
    actions to 'workflow.<portal_type>.events.before_<transition_id> function
    if exists for the instance passed in.
    :param instance: the instance to be transitioned
    :type instance: ATContentType
    :param event: event that holds the transition to be performed
    :type event: IObjectEvent
    """
    call_workflow_event(instance, event, after=False)


def AfterTransitionEventHandler(instance, event):
    """ This event is executed after each transition and delegates further
    actions to 'workflow.<portal_type>.events.after_<transition_id> function
    if exists for the instance passed in.
    :param instance: the instance that has been transitioned
    :type instance: ATContentType
    :param event: event that holds the transition performed
    :type event: IObjectEvent
    """
    if call_workflow_event(instance, event, after=True):
        return

    # Try with old AfterTransitionHandler dance...
    # TODO REMOVE AFTER PORTING workflow_script_*/*_transition_event
    if not event.transition:
        return
    # Set the request variable preventing cascade's from re-transitioning.
    if skip(instance, event.transition.id):
        return
    # Because at this point, the object has been transitioned already, but
    # further actions are probably needed still, so be sure is reindexed
    # before going forward.
    instance.reindexObject()
    key = 'after_{0}_transition_event'.format(event.transition.id)
    after_event = getattr(instance, key, False)
    if not after_event:
        # TODO Workflow. this conditional is only for backwards compatibility,
        # to be removed when all workflow_script_* methods in contents are
        # replaced by the more explicity signature 'after_*_transition_event'
        key = 'workflow_script_' + event.transition.id
        after_event = getattr(instance, key, False)
    if not after_event:
        return
    after_event()


def get_workflow_actions(obj):
    """ Compile a list of possible workflow transitions for this object
    """

    def translate(id):
        return t(PMF(id + "_transition_title"))

    transids = getAllowedTransitions(obj)
    actions = [{'id': it, 'title': translate(it)} for it in transids]
    return actions


def isTransitionAllowed(instance, transition_id):
    """Checks if the object can perform the transition passed in.
    :returns: True if transition can be performed
    :rtype: bool
    """
    wf_tool = getToolByName(instance, "portal_workflow")
    for wf_id in wf_tool.getChainFor(instance):
        wf = wf_tool.getWorkflowById(wf_id)
        if wf and wf.isActionSupported(instance, transition_id):
            return True

    return False


def getAllowedTransitions(instance):
    """Returns a list with the transition ids that can be performed against
    the instance passed in.
    :param instance: A content object
    :type instance: ATContentType
    :returns: A list of transition/action ids
    :rtype: list
    """
    wftool = getToolByName(instance, "portal_workflow")
    transitions = wftool.getTransitionsFor(instance)
    return [trans['id'] for trans in transitions]


def get_review_history_statuses(instance, reverse=False):
    """Returns a list with the statuses of the instance from the review_history
    """
    review_history = getReviewHistory(instance, reverse=reverse)
    return map(lambda event: event["review_state"], review_history)


def get_prev_status_from_history(instance, status=None):
    """Returns the previous status of the object. If status is set, returns the
    previous status before the object reached the status passed in.
    If instance has reached the status passed in more than once, only the last
    one is considered.
    """
    target = status or api.get_workflow_status_of(instance)
    history = getReviewHistory(instance, reverse=True)
    history = map(lambda event: event["review_state"], history)
    # Remove consecutive duplicates
    history = map(lambda i: i[0], groupby(history))

    if target not in history or history.index(target) == len(history)-1:
        return None
    return history[history.index(target)+1]


def getReviewHistory(instance, reverse=True):
    """Returns the review history for the instance
    :returns: the list of historic events as dicts
    """
    return api.get_review_history(instance, rev=reverse)


def getCurrentState(obj, stateflowid='review_state'):
    """ The current state of the object for the state flow id specified
        Return empty if there's no workflow state for the object and flow id
    """
    return api.get_workflow_status_of(obj, stateflowid)


def in_state(obj, states, stateflowid='review_state'):
    """ Returns if the object passed matches with the states passed in
    """
    if not states:
        return False
    obj_state = getCurrentState(obj, stateflowid=stateflowid)
    return obj_state in states


def getTransitionActor(obj, action_id):
    """Returns the actor that performed a given transition. If transition has
    not been perormed, or current user has no privileges, returns None
    :return: the username of the user that performed the transition passed-in
    :type: string
    """
    review_history = getReviewHistory(obj)
    for event in review_history:
        if event.get('action') == action_id:
            return event.get('actor')
    return None


def getTransitionDate(obj, action_id, return_as_datetime=False):
    """
    Returns date of action for object. Sometimes we need this date in Datetime
    format and that's why added return_as_datetime param.
    """
    review_history = getReviewHistory(obj)
    for event in review_history:
        if event.get('action') == action_id:
            evtime = event.get('time')
            if return_as_datetime:
                return evtime
            if evtime:
                value = ulocalized_time(evtime, long_format=True,
                                        time_only=False, context=obj)
                return value
    return None


def getTransitionUsers(obj, action_id, last_user=False):
    """
    This function returns a list with the users who have done the transition.
    :action_id: a sring as the transition id.
    :last_user: a boolean to return only the last user triggering the
        transition or all of them.
    :returns: a list of user ids.
    """
    workflow = getToolByName(obj, 'portal_workflow')
    users = []
    try:
        # https://jira.bikalabs.com/browse/LIMS-2242:
        # Sometimes the workflow history is inexplicably missing!
        review_history = list(workflow.getInfoFor(obj, 'review_history'))
    except WorkflowException:
        logger.error(
            "workflow history is inexplicably missing."
            " https://jira.bikalabs.com/browse/LIMS-2242")
        return users
    # invert the list, so we always see the most recent matching event
    review_history.reverse()
    for event in review_history:
        if event.get('action', '') == action_id:
            value = event.get('actor', '')
            users.append(value)
            if last_user:
                return users
    return users


def guard_handler(instance, transition_id):
    """Generic workflow guard handler that returns true if the transition_id
    passed in can be performed to the instance passed in.

    This function is called automatically by a Script (Python) located at
    bika/lims/skins/guard_handler.py, which in turn is fired by Zope when an
    expression like "python:here.guard_handler('<transition_id>')" is set to
    any given guard (used by default in all bika's DC Workflow guards).

    Walks through bika.lims.workflow.<obj_type>.guards and looks for a function
    that matches with 'guard_<transition_id>'. If found, calls the function and
    returns its value (true or false). If not found, returns True by default.

    :param instance: the object for which the transition_id has to be evaluated
    :param transition_id: the id of the transition
    :type instance: ATContentType
    :type transition_id: string
    :return: true if the transition can be performed to the passed in instance
    :rtype: bool
    """
    if not instance:
        return True

    # If adapters are found, core's guard will only be evaluated if, and only
    # if, ALL "pre-guards" return True
    for name, ad in getAdapters((instance,), IGuardAdapter):
        if ad.guard(transition_id) is False:
            return False

    clazz_name = instance.portal_type
    # Inspect if bika.lims.workflow.<clazzname>.<guards> module exists
    wf_module = _load_wf_module('{0}.guards'.format(clazz_name.lower()))
    if not wf_module:
        return True

    # Inspect if guard_<transition_id> function exists in the above module
    key = 'guard_{0}'.format(transition_id)
    guard = getattr(wf_module, key, False)
    if not guard:
        return True

    return guard(instance)


def _load_wf_module(module_relative_name):
    """Loads a python module based on the module relative name passed in.

    At first, tries to get the module from sys.modules. If not found there, the
    function tries to load it by using importlib. Returns None if no module
    found or importlib is unable to load it because of errors.
    Eg:
        _load_wf_module('sample.events')

    will try to load the module 'bika.lims.workflow.sample.events'

    :param modrelname: relative name of the module to be loaded
    :type modrelname: string
    :return: the module
    :rtype: module
    """
    if not module_relative_name:
        return None
    if not isinstance(module_relative_name, basestring):
        return None

    rootmodname = __name__
    modulekey = '{0}.{1}'.format(rootmodname, module_relative_name)
    if modulekey in sys.modules:
        return sys.modules.get(modulekey, None)

    # Try to load the module recursively
    modname = None
    tokens = module_relative_name.split('.')
    for part in tokens:
        modname = '.'.join([modname, part]) if modname else part
        import importlib
        try:
            _module = importlib.import_module('.'+modname, package=rootmodname)
            if not _module:
                return None
        except Exception:
            return None
    return sys.modules.get(modulekey, None)


class JSONReadExtender(object):

    """- Adds the list of possible transitions to each object, if 'transitions'
    is specified in the include_fields.
    """

    implements(IJSONReadExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        include_fields = get_include_fields(request)
        if not include_fields or "transitions" in include_fields:
            data['transitions'] = get_workflow_actions(self.context)


class ActionHandlerPool(object):
    """Singleton to handle concurrent transitions
    """
    implements(IActionHandlerPool)

    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        """Returns the current instance of ActionHandlerPool

        TODO: Refactor to global utility
        """
        if ActionHandlerPool.__instance is None:
            # Thread-safe
            with ActionHandlerPool.__lock:
                if ActionHandlerPool.__instance is None:
                    ActionHandlerPool()
        return ActionHandlerPool.__instance

    def __init__(self):
        if ActionHandlerPool.__instance is not None:
            raise Exception("Use ActionHandlerPool.get_instance()")
        ActionHandlerPool.__instance = self

    def __len__(self):
        """Number of objects in the pool
        """
        return len(self.objects)

    def __repr__(self):
        """Better repr
        """
        return "<ActionHandlerPool for UIDs:[{}]>".format(
            ",".join(map(api.get_uid, self.objects)))

    def flush(self):
        self.objects = collections.OrderedDict()
        self.num_calls = 0

    @property
    def request(self):
        request = api.get_request()
        if not isinstance(request, HTTPRequest):
            return None
        return request

    @property
    def request_ahp(self):
        data = {
            "objects": collections.OrderedDict(),
            "num_calls": 0
        }

        request = self.request
        if request is None:
            # Maybe this is called by a non-request script
            return data

        if "__action_handler_pool" not in request:
            request["__action_handler_pool"] = data
        return request["__action_handler_pool"]

    @property
    def objects(self):
        return self.request_ahp["objects"]

    @objects.setter
    def objects(self, value):
        self.request_ahp["objects"] = value

    @property
    def num_calls(self):
        return self.request_ahp["num_calls"]

    @num_calls.setter
    def num_calls(self, value):
        self.request_ahp["num_calls"] = value

    @synchronized(max_connections=1)
    def queue_pool(self):
        """Notifies that a new batch of jobs is about to begin
        """
        self.num_calls += 1

    @synchronized(max_connections=1)
    def push(self, instance, action, success, idxs=_marker):
        """Adds an instance into the pool, to be reindexed on resume
        """
        if self.request is None:
            # This is called by a non-request script
            instance.reindexObject()
            return

        uid = api.get_uid(instance)
        info = self.objects.get(uid, {})
        idx = [] if idxs is _marker else idxs
        info[action] = {"success": success, "idxs": idx}
        self.objects[uid] = info

    def succeed(self, instance, action):
        """Returns if the task for the instance took place successfully
        """
        uid = api.get_uid(instance)
        return self.objects.get(uid, {}).get(action, {}).get("success", False)

    @synchronized(max_connections=1)
    def resume(self):
        """Resumes the pool and reindex all objects processed
        """
        # do not decrease the counter below 0
        if self.num_calls > 0:
            self.num_calls -= 1

        # postpone for pending calls
        if self.num_calls > 0:
            return

        # return immediately if there are no objects in the queue
        count = len(self)
        if count == 0:
            return

        logger.info("Resume actions for {} objects".format(count))

        # Fetch the objects from the pool
        processed = list()
        for brain in api.search(dict(UID=self.objects.keys()), UID_CATALOG):
            uid = api.get_uid(brain)
            if uid in processed:
                # This object has been processed already, do nothing
                continue

            # Reindex the object
            obj = api.get_object(brain)
            idxs = self.get_indexes(uid)
            idxs_str = idxs and ", ".join(idxs) or "-- All indexes --"
            logger.info("Reindexing {}: {}".format(obj.getId(), idxs_str))
            obj.reindexObject(idxs=idxs)
            processed.append(uid)

        # Cleanup the pool
        logger.info("Objects processed: {}".format(len(processed)))
        self.flush()

    def get_indexes(self, uid):
        """Returns the names of the indexes to be reindexed for the object with
        the uid passed in. If no indexes for this object have been specified
        within the action pool job, returns an empty list (reindex all).
        Otherwise, return all the indexes that have been specified for the
        object within the action pool job.
        """
        idxs = []
        info = self.objects.get(uid, {})
        for action_id, value in info.items():
            obj_idxs = value.get('idxs', None)
            if obj_idxs is None:
                # Don't reindex!
                continue
            elif len(obj_idxs) == 0:
                # Reindex all indexes!
                return []
            idxs.extend(obj_idxs)
        # Always reindex review_state and is_active
        idxs.extend(["review_state", "is_active"])
        return list(set(idxs))


def push_reindex_to_actions_pool(obj, idxs=None):
    """Push a reindex job to the actions handler pool
    """
    indexes = idxs and idxs or []
    pool = ActionHandlerPool.get_instance()
    pool.push(obj, "reindex", success=True, idxs=indexes)
