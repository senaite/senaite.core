# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import enum
from bika.lims import PMF
from bika.lims.browser import ulocalized_time
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.jsonapi import get_include_fields
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import t
from bika.lims import logger
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IWorkflowChain
from Products.CMFPlone.workflow import ToolWorkflowChain
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
import traceback


def skip(instance, action, peek=False, unskip=False):
    """Returns True if the transition is to be SKIPPED

        peek - True just checks the value, does not set.
        unskip - remove skip key (for manual overrides).

    called with only (instance, action_id), this will set the request variable preventing the
    cascade's from re-transitioning the object and return None.
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


def doActionFor(instance, action_id):
    """Performs the transition (action_id) to the instance.

    The transition will only be triggered if the current state of the object
    allows the action_id passed in (delegate to isTransitionAllowed) and the
    instance hasn't been flagged as to be skipped previously

    :param instance: Object to be transitioned
    :param action_id: transition id
    :returns: true if the transition has been performed and message
    :rtype: list
    """
    actionperformed = False
    message = ''
    workflow = getToolByName(instance, "portal_workflow")
    if not skip(instance, action_id, peek=True) \
        and isTransitionAllowed(instance, action_id):
        try:
            workflow.doActionFor(instance, action_id)
            actionperformed = True
        except WorkflowException as e:
            message = str(e)
    return actionperformed, message


def BeforeTransitionEventHandler(instance, event):
    """ This event is executed before each transition and delegates further
    actions to 'before_x_transition_event' function if exists in the instance
    passed in, where 'x' is the id of the event's transition.

    If the passed in instance has not a function with the abovementioned
    signature, or if there is no transition for the state change (like the
    'creation' state, then the function does nothing.

    :param instance: the instance to be transitioned
    :type instance: ATContentType
    :param event: event that holds the transition to be performed
    :type event: IObjectEvent
    """
    # there is no transition for the state change (creation doesn't have a
    # 'transition')
    if not event.transition:
        return

    clazzname = instance.__class__.__name__
    msg = "Starting transtion {0} for object {1} with id {2}".format(
        event.transition.id,  clazzname, instance.getId())
    logger.debug(msg)

    key = 'before_{0}_transition_event'.format(event.transition.id)
    before_event = getattr(instance, key, False)
    if not before_event:
        # TODO: this conditional is only for backwards compatibility, to be
        # removed when all workflow_before_* methods in contents are replaced
        # by the more explicity signature 'before_*_transition_event'
        key = 'workflow_before_' + event.transition.id
        before_event = getattr(instance, key, False)

    if not before_event:
        return

    msg = "Calling BeforeTransitionEvent function '{0}' from {1}".format(
        key, clazzname)
    logger.debug(msg)
    before_event()


def AfterTransitionEventHandler(instance, event):
    """ This event is executed after each transition and delegates further
    actions to 'after_x_transition_event' function if exists in the instance
    passed in, where 'x' is the id of the event's transition.

    If the passed in instance has not a function with the abovementioned
    signature, or if there is no transition for the state change (like the
    'creation' state) or the same transition has already been run for the
    the passed in instance during the current server request, then the
    function does nothing.

    :param instance: the instance that has been transitioned
    :type instance: ATContentType
    :param event: event that holds the transition performed
    :type event: IObjectEvent
    """
    # there is no transition for the state change (creation doesn't have a
    # 'transition')
    if not event.transition:
        return

    # Set the request variable preventing cascade's from re-transitioning.
    if skip(instance, event.transition.id):
        return

    clazzname = instance.__class__.__name__
    msg = "Transition {0} performed for object {1} with id {2}".format(
        event.transition.id,  clazzname, instance.getId())
    logger.debug(msg)

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

    msg = "Calling AfterTransitionEvent function '{0}' from {1}".format(
        key, clazzname)
    logger.debug(msg)
    after_event()

def get_workflow_actions(obj):
    """ Compile a list of possible workflow transitions for this object
    """

    def translate(id):
        return t(PMF(id + "_transition_title"))

    workflow = getToolByName(obj, 'portal_workflow')
    actions = [{"id": it["id"],
                "title": translate(it["id"])}
               for it in workflow.getTransitionsFor(obj)]

    return actions


def isBasicTransitionAllowed(context, permission=None):
    """Most transition guards need to check the same conditions:

    - Is the object active (cancelled or inactive objects can't transition)
    - Has the user a certain permission, required for transition.  This should
    normally be set in the guard_permission in workflow definition.

    """
    workflow = getToolByName(context, "portal_workflow")
    mtool = getToolByName(context, "portal_membership")
    if workflow.getInfoFor(context, "cancellation_state", "") == "cancelled" \
            or workflow.getInfoFor(context, "inactive_state", "") == "inactive" \
            or (permission and mtool.checkPermission(permission, context)):
        return False
    return True

def isTransitionAllowed(instance, transition_id):
    wftool = getToolByName(instance, "portal_workflow")
    transitions = wftool.getTransitionsFor(instance)
    trans = [trans for trans in transitions if trans.id == transition_id]
    return len(trans) >= 1

def getCurrentState(obj, stateflowid='review_state'):
    """ The current state of the object for the state flow id specified
        Return empty if there's no workflow state for the object and flow id
    """
    wf = getToolByName(obj, 'portal_workflow')
    return wf.getInfoFor(obj, stateflowid, '')


def getTransitionDate(obj, action_id, not_as_string=False):
    """
    Returns date of action for object. Sometimes we need this date in Datetime
    format and that's why added not_as_string param.
    """
    workflow = getToolByName(obj, 'portal_workflow')
    try:
        # https://jira.bikalabs.com/browse/LIMS-2242:
        # Sometimes the workflow history is inexplicably missing!
        review_history = list(workflow.getInfoFor(obj, 'review_history'))
    except WorkflowException:
        logger.error(
            "workflow history is inexplicably missing."
            " https://jira.bikalabs.com/browse/LIMS-2242")
        return None
    # invert the list, so we always see the most recent matching event
    review_history.reverse()
    for event in review_history:
        if event['action'] == action_id:
            if not_as_string:
                return event['time']
            value = ulocalized_time(event['time'], long_format=True,
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

# Enumeration of the available status flows
StateFlow = enum(review='review_state',
                 inactive='inactive_state',
                 cancellation='cancellation_state')

# Enumeration of the different available states from the inactive flow
InactiveState = enum(active='active')

# Enumeration of the different states can have a batch
BatchState = enum(open='open',
                  closed='closed',
                  cancelled='cancelled')

BatchTransitions = enum(open='open',
                        close='close')

CancellationState = enum(active='active',
                         cancelled='cancelled')

CancellationTransitions = enum(cancel='cancel',
                               reinstate='reinstate')


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



@implementer(IWorkflowChain)
def SamplePrepWorkflowChain(ob, wftool):
    """Responsible for inserting the optional sampling preparation workflow
    into the workflow chain for objects with ISamplePrepWorkflow

    This is only done if the object is in 'sample_prep' state in the
    primary workflow (review_state).
    """
    # use catalog to retrieve review_state: getInfoFor causes recursion loop
    chain = list(ToolWorkflowChain(ob, wftool))
    try:
        bc = getToolByName(ob, 'bika_catalog')
    except AttributeError:
        logger.error(traceback.format_exc())
        logger.error(
            "Error getting 'bika_catalog' using 'getToolByName' with '{0}'"
            " as context.".format(ob))
        return chain
    proxies = bc(UID=ob.UID())
    if not proxies or proxies[0].review_state != 'sample_prep':
        return chain
    sampleprep_workflow = ob.getPreparationWorkflow()
    if sampleprep_workflow:
        chain.append(sampleprep_workflow)
    return tuple(chain)


def SamplePrepTransitionEventHandler(instance, event):
    """Sample preparation is considered complete when the sampleprep workflow
    reaches a state which has no exit transitions.

    If the stateis state's ID is the same as any AnalysisRequest primary
    workflow ID, then the AnalysisRequest will be sent directly to that state.

    If the final state's ID is not found in the AR workflow, the AR will be
    transitioned to 'sample_received'.
    """
    if not event.transition:
        # creation doesn't have a 'transition'
        return

    if not event.new_state.getTransitions():
        # Is this the final (No exit transitions) state?
        wftool = getToolByName(instance, 'portal_workflow')
        primary_wf_name = list(ToolWorkflowChain(instance, wftool))[0]
        primary_wf = wftool.getWorkflowById(primary_wf_name)
        primary_wf_states = primary_wf.states.keys()
        if event.new_state.id in primary_wf_states:
            # final state name matches review_state in primary workflow:
            dst_state = event.new_state.id
        else:
            # fallback state:
            dst_state = 'sample_received'
        changeWorkflowState(instance, primary_wf_name, dst_state)
