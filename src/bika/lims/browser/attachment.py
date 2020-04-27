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

from bika.lims import api
from bika.lims import logger
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS
from bika.lims.decorators import returns_json
from bika.lims.permissions import AddAttachment
from bika.lims.permissions import EditFieldResults
from bika.lims.permissions import EditResults
from BTrees.OOBTree import OOBTree
from plone import protect
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


ATTACHMENTS_STORAGE = "bika.lims.browser.attachment"

EDITABLE_STATES = [
    'to_be_sampled',
    'to_be_preserved',
    'sample_due',
    'sample_received',
    'to_be_verified',
]


class AttachmentsView(BrowserView):
    """Attachments manage view

    This view is used in the Attachments viewlet displayed in ARs and WSs, but
    can be used as a general purpose multi-adapter for ARs and WSs to manage
    attachments.
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """get called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def __call__(self):
        """Endpoint for form actions etc.
        """
        protect.CheckAuthenticator(self.request.form)

        url = self.context.absolute_url()

        # only proceed if the form was POSTed
        if not self.request.form.get("submitted", False):
            return self.request.response.redirect(url)

        # only handle one additional path segment to route to a form action
        if len(self.traverse_subpath) != 1:
            return self.request.response.redirect(url)

        # the first path segment is used to determine the endpoint
        func_name = self.traverse_subpath[0]
        action_name = "action_{}".format(func_name)
        action = getattr(self, action_name, None)

        if action is None:
            logger.warn("AttachmentsView.__call__: Unknown action name '{}'"
                        .format(func_name))
            return self.request.response.redirect(url)
        # call the endpoint
        return action()

    def action_update(self):
        """Form action enpoint to update the attachments
        """

        order = []
        form = self.request.form
        attachments = form.get("attachments", [])

        for attachment in attachments:
            # attachment is a form mapping, not a dictionary -> convert
            values = dict(attachment)

            uid = values.pop("UID")
            obj = api.get_object_by_uid(uid)

            # delete the attachment if the delete flag is true
            if values.pop("delete", False):
                self.delete_attachment(obj)
                continue

            # remember the order
            order.append(uid)

            # update the attachment with the given data
            obj.update(**values)
            obj.reindexObject()

        # set the attachments order to the annotation storage
        self.set_attachments_order(order)

        # redirect back to the default view
        return self.request.response.redirect(self.context.absolute_url())

    def action_add_to_ws(self):
        """Form action to add a new attachment in a worksheet
        """

        ws = self.context
        form = self.request.form
        attachment_file = form.get('AttachmentFile_file', None)
        analysis_uid = self.request.get('analysis_uid', None)
        service_uid = self.request.get('Service', None)
        AttachmentType = form.get('AttachmentType', '')
        AttachmentKeys = form.get('AttachmentKeys', '')
        ReportOption = form.get('ReportOption', 'r')

        # nothing to do if the attachment file is missing
        if attachment_file is None:
            logger.warn("AttachmentView.action_add_attachment: Attachment file is missing")
            return

        if analysis_uid:
            rc = api.get_tool("reference_catalog")
            analysis = rc.lookupObject(analysis_uid)

            # create attachment
            attachment = self.create_attachment(
                ws,
                attachment_file,
                AttachmentType=AttachmentType,
                AttachmentKeys=AttachmentKeys,
                ReportOption=ReportOption)

            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)

            # The metadata for getAttachmentUIDs need to get updated,
            # otherwise the attachments are not displayed
            # https://github.com/senaite/bika.lims/issues/521
            analysis.reindexObject()

        if service_uid:
            workflow = api.get_tool('portal_workflow')

            # XXX: refactor out dependency to this view.
            view = api.get_view("manage_results", context=self.context, request=self.request)
            analyses = self.context.getAnalyses()
            allowed_states = ["assigned", "unassigned", "to_be_verified"]
            for analysis in analyses:
                if analysis.portal_type not in ('Analysis', 'DuplicateAnalysis'):
                    continue
                if not analysis.getServiceUID() == service_uid:
                    continue
                review_state = workflow.getInfoFor(analysis, 'review_state', '')
                if review_state not in allowed_states:
                    continue

                # create attachment
                attachment = self.create_attachment(
                    ws,
                    attachment_file,
                    AttachmentType=AttachmentType,
                    AttachmentKeys=AttachmentKeys,
                    ReportOption=ReportOption)

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)

                # The metadata for getAttachmentUIDs need to get updated,
                # otherwise the attachments are not displayed
                # https://github.com/senaite/bika.lims/issues/521
                analysis.reindexObject()

        if self.request['HTTP_REFERER'].endswith('manage_results'):
            self.request.response.redirect('{}/manage_results'.format(
                self.context.absolute_url()))
        else:
            self.request.response.redirect(self.context.absolute_url())

    def action_add(self):
        """Form action to add a new attachment

        Code taken from bika.lims.content.addARAttachment.
        """

        form = self.request.form
        parent = api.get_parent(self.context)
        attachment_file = form.get('AttachmentFile_file', None)
        AttachmentType = form.get('AttachmentType', '')
        AttachmentKeys = form.get('AttachmentKeys', '')
        ReportOption = form.get('ReportOption', 'r')

        # nothing to do if the attachment file is missing
        if attachment_file is None:
            logger.warn("AttachmentView.action_add_attachment: Attachment file is missing")
            return

        # create attachment
        attachment = self.create_attachment(
            parent,
            attachment_file,
            AttachmentType=AttachmentType,
            AttachmentKeys=AttachmentKeys,
            ReportOption=ReportOption)

        # append the new UID to the end of the current order
        self.set_attachments_order(api.get_uid(attachment))

        # handle analysis attachment
        analysis_uid = form.get("Analysis", None)
        if analysis_uid:
            analysis = api.get_object_by_uid(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            # The metadata for getAttachmentUIDs need to get updated,
            # otherwise the attachments are not displayed
            # https://github.com/senaite/bika.lims/issues/521
            analysis.reindexObject()

        else:
            others = self.context.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.context.setAttachment(attachments)

        if self.request['HTTP_REFERER'].endswith('manage_results'):
            self.request.response.redirect('{}/manage_results'.format(
                self.context.absolute_url()))
        else:
            self.request.response.redirect(self.context.absolute_url())

    def create_attachment(self, container, attachment_file, **kw):
        """Create an Attachment object in the given container
        """
        filename = getattr(attachment_file, "filename", "Attachment")
        attachment = api.create(container, "Attachment", title=filename)
        attachment.edit(AttachmentFile=attachment_file, **kw)
        attachment.processForm()
        attachment.reindexObject()
        logger.info("Created new Attachment {} in {}".format(
            repr(attachment), repr(container)))
        return attachment

    def delete_attachment(self, attachment):
        """Delete attachment from the AR or Analysis

        The attachment will be only deleted if it is not further referenced by
        another AR/Analysis.
        """

        # Get the holding parent of this attachment
        parent = None
        if attachment.getLinkedRequests():
            # Holding parent is an AR
            parent = attachment.getRequest()
        elif attachment.getLinkedAnalyses():
            # Holding parent is an Analysis
            parent = attachment.getAnalysis()

        if parent is None:
            logger.warn(
                "Attachment {} is nowhere assigned. This should never happen!"
                .format(repr(attachment)))
            return False

        # Get the other attachments of the holding parent
        attachments = parent.getAttachment()

        # New attachments to set
        if attachment in attachments:
            attachments.remove(attachment)

        # Set the attachments w/o the current attachments
        parent.setAttachment(attachments)

        retain = False

        # Attachment is referenced by another Analysis
        if attachment.getLinkedAnalyses():
            holder = attachment.getAnalysis()
            logger.info("Attachment {} referenced by {} -> RETAIN"
                        .format(repr(attachment), repr(holder)))
            retain = True

        # Attachment is referenced by another AR
        if attachment.getLinkedRequests():
            holder = attachment.getRequest()
            logger.info("Attachment {} referenced by {} -> RETAIN"
                        .format(repr(attachment), repr(holder)))
            retain = True

        # Delete attachment finally
        if retain is False:
            client = api.get_parent(attachment)
            client.manage_delObjects([attachment.getId(), ])

    def global_attachments_allowed(self):
        """Checks Bika Setup if Attachments are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getAttachmentsPermitted()

    def global_ar_attachments_allowed(self):
        """Checks Bika Setup if AR Attachments are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getARAttachmentsPermitted()

    def global_analysis_attachments_allowed(self):
        """Checks Bika Setup if Attachments for Analyses are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getAnalysisAttachmentsPermitted()

    def get_attachment_size(self, attachment):
        """Get the human readable size of the attachment
        """
        fsize = 0
        file = attachment.getAttachmentFile()
        if file:
            fsize = file.get_size()
        if fsize < 1024:
            fsize = '%s b' % fsize
        else:
            fsize = '%s Kb' % (fsize / 1024)
        return fsize

    def get_attachment_info(self, attachment):
        """Returns a dictionary of attachment information
        """

        attachment_uid = api.get_uid(attachment)
        attachment_file = attachment.getAttachmentFile()
        attachment_type = attachment.getAttachmentType()
        attachment_icon = attachment_file.icon

        if callable(attachment_icon):
            attachment_icon = attachment_icon()

        return {
            'keywords': attachment.getAttachmentKeys(),
            'size': self.get_attachment_size(attachment),
            'name': attachment_file.filename,
            'Icon': attachment_icon,
            'type': api.get_uid(attachment_type) if attachment_type else '',
            'absolute_url': attachment.absolute_url(),
            'UID': attachment_uid,
            'report_option': attachment.getReportOption(),
            'analysis': '',
        }

    def get_attachments(self):
        """Returns a list of attachments info dictionaries

        Original code taken from bika.lims.analysisrequest.view
        """

        attachments = []

        # process AR attachments
        for attachment in self.context.getAttachment():
            attachment_info = self.get_attachment_info(attachment)
            attachments.append(attachment_info)

        # process analyses attachments
        for analysis in self.context.getAnalyses(full_objects=True):
            for attachment in analysis.getAttachment():
                attachment_info = self.get_attachment_info(attachment)
                attachment_info["analysis"] = analysis.Title()
                attachment_info["analysis_uid"] = api.get_uid(analysis)
                attachments.append(attachment_info)

        return attachments

    def get_sorted_attachments(self):
        """Returns a sorted list of analysis info dictionaries
        """
        inf = float("inf")
        order = self.get_attachments_order()
        attachments = self.get_attachments()

        def att_cmp(att1, att2):
            _n1 = att1.get('UID')
            _n2 = att2.get('UID')
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        sorted_attachments = sorted(attachments, cmp=att_cmp)
        return sorted_attachments

    def get_attachment_types(self):
        """Returns a list of available attachment types
        """
        bika_setup_catalog = api.get_tool("bika_setup_catalog")
        attachment_types = bika_setup_catalog(portal_type='AttachmentType',
                                              is_active=True,
                                              sort_on="sortable_title",
                                              sort_order="ascending")
        return attachment_types

    def get_attachment_report_options(self):
        """Returns the valid attachment report options
        """
        return ATTACHMENT_REPORT_OPTIONS.items()

    def get_analyses(self):
        """Returns a list of analyses from the AR
        """
        analyses = self.context.getAnalyses(full_objects=True)
        return filter(self.is_analysis_attachment_allowed, analyses)

    def is_analysis_attachment_allowed(self, analysis):
        """Checks if the analysis
        """
        if analysis.getAttachmentOption() not in ["p", "r"]:
            return False
        if api.get_workflow_status_of(analysis) in ["retracted"]:
            return False
        return True

    def user_can_add_attachments(self):
        """Checks if the current logged in user is allowed to add attachments
        """
        if not self.global_attachments_allowed():
            return False
        context = self.context
        pm = api.get_tool("portal_membership")
        return pm.checkPermission(AddAttachment, context)

    def user_can_update_attachments(self):
        """Checks if the current logged in user is allowed to update attachments
        """
        context = self.context
        pm = api.get_tool("portal_membership")
        return pm.checkPermission(EditResults, context) or \
            pm.checkPermission(EditFieldResults, context)

    def user_can_delete_attachments(self):
        """Checks if the current logged in user is allowed to delete attachments
        """
        context = self.context
        user = api.get_current_user()
        if not self.is_ar_editable():
            return False
        return (self.user_can_add_attachments() and
                not user.allowed(context, ["Client"])) or \
            self.user_can_update_attachments()

    def is_ar_editable(self):
        """Checks if the AR is in a review_state that allows to update the attachments.
        """
        state = api.get_workflow_status_of(self.context)
        return state in EDITABLE_STATES

    # ANNOTATION HANDLING

    def get_annotation(self):
        """Get the annotation adapter
        """
        return IAnnotations(self.context)

    @property
    def storage(self):
        """A storage which keeps configuration settings for attachments
        """
        annotation = self.get_annotation()
        if annotation.get(ATTACHMENTS_STORAGE) is None:
            annotation[ATTACHMENTS_STORAGE] = OOBTree()
        return annotation[ATTACHMENTS_STORAGE]

    def flush(self):
        """Remove the whole storage
        """
        annotation = self.get_annotation()
        if annotation.get(ATTACHMENTS_STORAGE) is not None:
            del annotation[ATTACHMENTS_STORAGE]

    def set_attachments_order(self, order):
        """Remember the attachments order
        """
        # append single uids to the order
        if isinstance(order, basestring):
            new_order = self.storage.get("order", [])
            new_order.append(order)
            order = new_order
        self.storage.update({"order": order})

    def get_attachments_order(self):
        """Retunrs a list of UIDs for sorting purposes.

        The order should be in the same order like the rows of the attachment
        listing viewlet.
        """
        return self.storage.get("order", [])


class ajaxAttachmentsView(AttachmentsView):
    """Ajax helpers for attachments
    """

    def __init__(self, context, request):
        super(ajaxAttachmentsView, self).__init__(context, request)

    @returns_json
    def __call__(self):
        protect.CheckAuthenticator(self.request.form)

        if len(self.traverse_subpath) != 1:
            return self.error("Not found", status=404)
        func_name = "ajax_{}".format(self.traverse_subpath[0])
        func = getattr(self, func_name, None)
        if func is None:
            return self.error("Invalid function", status=400)
        return func()

    def error(self, message, status=500, **kw):
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message}
        result.update(kw)
        return result

    def ajax_delete_analysis_attachment(self):
        """Endpoint for attachment delete in WS
        """
        form = self.request.form
        attachment_uid = form.get("attachment_uid", None)

        if not attachment_uid:
            return "error"

        attachment = api.get_object_by_uid(attachment_uid, None)
        if attachment is None:
            return "Could not resolve attachment UID {}".format(attachment_uid)

        # handle delete via the AttachmentsView
        view = self.context.restrictedTraverse("@@attachments_view")
        view.delete_attachment(attachment)

        return "success"
