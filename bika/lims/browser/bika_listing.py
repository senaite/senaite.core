# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api import get_object_by_uid
from bika.lims.workflow import ActionHandlerPool
from bika.lims.workflow import doActionFor
from senaite.core.listing import ListingView


class WorkflowAction:
    """Workflow actions taken in any Bika contextAnalysisRequest context

    This function provides the default behaviour for workflow actions
    invoked from bika_listing tables.

    Some actions (eg, AR copy_to_new) can be invoked from multiple contexts.
    In that case, I will begin to register their handlers here.
    XXX WorkflowAction handlers should be simple adapters.
    """

    def __init__(self, context, request):
        self.destination_url = ""
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()
        # Save context UID for benefit of event subscribers.
        self.request['context_uid'] = hasattr(self.context, 'UID') and \
            self.context.UID() or ''
        self.portal = api.get_portal()
        self.addPortalMessage = self.context.plone_utils.addPortalMessage

    def _get_form_workflow_action(self):
        """Retrieve the workflow action from the submitted form
            - "workflow_action" is the edit border transition
            - "workflow_action_button" is the bika_listing table buttons
        """
        request = self.request
        form = request.form
        came_from = "workflow_action"
        action = form.get(came_from, '')

        if not action:
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    url = self.context.absolute_url()
                    self.destination_url = request.get_header("referer", url)
                request.response.redirect(self.destination_url)
                return None, None

        # A condition in the form causes Plone to sometimes send two actions
        if type(action) in (list, tuple):
            action = action[0]

        return action, came_from

    def get_selected_uids(self):
        """Returns a list of selected form uids"""
        return self.request.form.get('uids', None) or list()

    def _get_selected_items(self, filter_active=False, permissions=list()):
        """return a list of selected form objects
           full_objects defaults to True
        """
        uids = self.get_selected_uids()
        selected_items = collections.OrderedDict()
        checkPermission = self.context.portal_membership.checkPermission
        for uid in uids:
            obj = get_object_by_uid(uid)
            if not obj:
                continue
            if filter_active and not api.is_active(obj):
                continue
            if permissions:
                for permission in permissions:
                    if not checkPermission(permission, obj):
                        continue
            selected_items[uid] = obj
        return selected_items

    def get_form_value(self, form_key, object_uid, default=None):
        form = self.request.form
        val = form.get(form_key, None) or [{}]
        val = val[0] or {}
        return val.get(object_uid, default)

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def workflow_action_default(self, action, came_from):
        if came_from in ['workflow_action', 'edit']:
            # If a single item was acted on we will create the item list
            # manually from this item itself.  Otherwise, bika_listing will
            # pass a list of selected items in the requyest.
            items = [self.context, ]
        else:
            # normal bika_listing.
            items = self._get_selected_items().values()

        if items:
            trans, dest = self.submitTransition(action, came_from, items)
            if trans:
                message = PMF('Changes saved.')
                self.addPortalMessage(message, 'info')
            if dest:
                self.request.response.redirect(dest)
                return
        else:
            message = _('No items selected')
            self.addPortalMessage(message, 'warn')
        self.request.response.redirect(self.destination_url)
        return

    def workflow_action_copy_to_new(self):
        """Invoke the ar_add form in the current context, passing the UIDs of
        the source ARs as request parameters.
        """
        objects = self._get_selected_items()
        if not objects:
            message = self.context.translate(
                _("No analyses have been selected"))
            self.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url() + "/batchbook"
            self.request.response.redirect(self.destination_url)
            return

        url = self.context.absolute_url() + "/ar_add" + \
            "?ar_count={0}".format(len(objects)) + \
            "&copy_from={0}".format(",".join(objects.keys()))

        self.request.response.redirect(url)
        return

    def workflow_action_print_stickers(self):
        """Invoked from AR or Sample listings in the current context, passing
        the uids of the selected items and default sticker template as request
        parameters to the stickers rendering machinery, that generates the PDF
        """
        uids = self.request.form.get("uids", [])
        if not uids:
            message = self.context.translate(
                _("No Samples have been selected"))
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
            return

        url = '{0}/sticker?template={1}&items={2}'.format(
            self.context.absolute_url(),
            self.portal.bika_setup.getAutoStickerTemplate(),
            ','.join(uids)
        )
        self.destination_url = url
        self.request.response.redirect(url)

    def __call__(self):
        request = self.request

        if self.destination_url == "":
            self.destination_url = request.get_header(
                "referer", self.context.absolute_url())

        action, came_from = self._get_form_workflow_action()

        if action:
            # bika_listing sometimes gives us a list of items?
            if type(action) == list:
                action = action[0]
            # Call out to the workflow action method
            # Use default bika_listing.py/WorkflowAction for other transitions
            method_name = 'workflow_action_' + action
            method = getattr(self, method_name, False)
            if method and not callable(method):
                raise Exception("Shouldn't Happen: %s.%s not callable." %
                                (self, method_name))
            if method:
                method()
            else:
                self.workflow_action_default(action, came_from)
        else:
            # Do nothing
            self.request.response.redirect(self.destination_url)
            return

    # noinspection PyUnusedLocal
    def submitTransition(self, action, came_from, items):
        """Performs the action's transition for the specified items

        Returns (numtransitions, destination), where:
        - numtransitions: the number of objects successfully transitioned.
            If no objects have been successfully transitioned, gets 0 value
        - destination: the destination url to be loaded immediately
        """
        transitioned = []
        actions = ActionHandlerPool.get_instance()
        actions.queue_pool()
        for item in items:
            success, message = doActionFor(item, action)
            if success:
                transitioned.append(item.UID())
            else:
                self.addPortalMessage(message, 'error')
        actions.resume()

        # automatic label printing
        dest = None
        auto_stickers_action = self.portal.bika_setup.getAutoPrintStickers()
        if transitioned and action == auto_stickers_action:
            self.request.form['uids'] = transitioned
            self.workflow_action_print_stickers()
            dest = self.destination_url

        return len(transitioned), dest


class BikaListingView(ListingView):
    """BBB: Base View for Table Listings

    Please use `senaite.core.listing.ListingView` instead
    https://github.com/senaite/senaite.core/pull/1226
    """
