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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import six

from bika.lims import FieldEditAnalysisResult
from bika.lims import SampleAddAttachment
from bika.lims import SampleDeleteAttachment
from bika.lims import SampleEditAttachment
from bika.lims import api
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from bika.lims.api import security
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS
from bika.lims.interfaces.analysis import IRequestAnalysis
from BTrees.OOBTree import OOBTree
from plone import protect
from plone.memoize import view
from Products.Five.browser import BrowserView
from senaite.core.p3compat import cmp
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

ATTACHMENTS_STORAGE = "bika.lims.browser.attachment"


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

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def action_update(self):
        """Form action endpoint to update the attachments
        """

        order = []
        deleted = 0
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
                deleted += 1
                continue

            # remember the order
            order.append(uid)

            # update the attachment with the given data
            obj.update(**values)
            obj.reindexObject()

        # add update notification
        if not deleted:
            self.add_status_message(_("Attachment(s) updated"))
        # set the attachments order to the annotation storage
        self.set_attachments_order(order)
        # redirect back to the default view
        return self.request.response.redirect(self.context.absolute_url())

    def action_add_to_ws(self):
        """Form action to add a new attachment in a worksheet
        """

        ws = self.context
        form = self.request.form
        attachment_file = form.get("AttachmentFile_file", None)
        analysis_uid = self.request.get("analysis_uid", None)
        service_uid = self.request.get("Service", None)
        attachment_type = form.get("AttachmentType", "")
        attachment_keys = form.get("AttachmentKeys", "")
        report_option = form.get("ReportOption", "r")

        # nothing to do if the attachment file is missing
        if attachment_file is None:
            logger.warn("AttachmentView.action_add_attachment: "
                        "Attachment file is missing")
            return

        if analysis_uid:
            rc = api.get_tool("reference_catalog")
            analysis = rc.lookupObject(analysis_uid)

            # create attachment
            attachment = self.create_attachment(
                ws,
                attachment_file,
                AttachmentType=attachment_type,
                AttachmentKeys=attachment_keys,
                ReportOption=report_option)

            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            title = api.safe_unicode(api.get_title(analysis))
            self.add_status_message(
                _(u"Attachment added to analysis '{}'".format(title)))

        if service_uid:
            attached = 0
            service = api.get_object_by_uid(service_uid)

            for analysis in self.context.getAnalyses():
                if not IRequestAnalysis.providedBy(analysis):
                    continue
                if not self.is_editable(analysis):
                    continue
                if analysis.getKeyword() != service.getKeyword():
                    continue

                # create attachment
                attachment = self.create_attachment(
                    ws,
                    attachment_file,
                    AttachmentType=attachment_type,
                    AttachmentKeys=attachment_keys,
                    ReportOption=report_option)

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)
                attached += 1

            service_title = api.safe_unicode(api.get_title(service))
            if attached > 0:
                self.add_status_message(
                    _(u"Attachment added to all '{}' analyses"
                      .format(service_title)))
            else:
                self.add_status_message(
                    _(u"No analysis found for service '{}'"
                      .format(service_title)), level="warning")

        if not any([analysis_uid, service_uid]):
            self.add_status_message(
                _("Please select an analysis or service for the attachment"),
                level="warning")

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
        attachment_file = form.get("AttachmentFile_file", None)
        attachment_type = form.get("AttachmentType", "")
        attachment_keys = form.get("AttachmentKeys", "")
        report_option = form.get("ReportOption", "r")

        # nothing to do if the attachment file is missing
        if attachment_file is None:
            logger.warn("AttachmentView.action_add_attachment: "
                        "Attachment file is missing")
            return

        # create attachment
        attachment = self.create_attachment(
            parent,
            attachment_file,
            AttachmentType=attachment_type,
            AttachmentKeys=attachment_keys,
            ReportOption=report_option)

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
            title = api.safe_unicode(api.get_title(analysis))
            self.add_status_message(
                _(u"Attachment added to analysis '{}'".format(title)))
        else:
            others = self.context.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.context.setAttachment(attachments)
            self.add_status_message(
                _("Attachment added to the current sample"))

        if self.request["HTTP_REFERER"].endswith("manage_results"):
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
            self.add_status_message(_("Attachment(s) deleted"))

    def get_attachment_size(self, attachment):
        """Get the human readable size of the attachment
        """
        fsize = 0
        file = attachment.getAttachmentFile()
        if file:
            fsize = file.get_size()
        if fsize < 1024:
            fsize = "%s b" % fsize
        else:
            fsize = "%s Kb" % (fsize / 1024)
        return fsize

    def get_attachment_info(self, attachment):
        """Returns a dictionary of attachment information
        """
        attachment_uid = api.get_uid(attachment)
        attachment_file = attachment.getAttachmentFile()
        attachment_type = attachment.getAttachmentType()
        report_option = attachment.getReportOption()
        report_option_value = ATTACHMENT_REPORT_OPTIONS.getValue(report_option)

        return {
            "keywords": attachment.getAttachmentKeys(),
            "size": self.get_attachment_size(attachment),
            "name": attachment_file.filename,
            "type_uid": api.get_uid(attachment_type) if attachment_type else "",
            "type": api.get_title(attachment_type) if attachment_type else "",
            "absolute_url": attachment.absolute_url(),
            "UID": attachment_uid,
            "report_option": report_option,
            "report_option_value": report_option_value,
            "analysis": "",
        }

    @view.memoize
    def get_attachments(self):
        """Returns a list of attachments info dictionaries
        """
        attachments = []

        # process AR attachments
        for attachment in self.context.getAttachment():
            attachment_info = self.get_attachment_info(attachment)
            attachment_info["can_edit"] = self.can_edit_attachments()
            attachments.append(attachment_info)

        # process analyses attachments
        skip = ["cancelled", "retracted", "rejected"]
        for analysis in self.context.getAnalyses(full_objects=True):
            if api.get_review_status(analysis) in skip:
                # Do not display attachments from invalid analyses in the
                # attachments viewlet, user can download them from the analysis
                # listing anyways
                continue

            can_edit = self.is_editable(analysis)
            for attachment in analysis.getAttachment():
                attachment_info = self.get_attachment_info(attachment)
                attachment_info["analysis"] = api.get_title(analysis)
                attachment_info["analysis_uid"] = api.get_uid(analysis)
                attachment_info["can_edit"] = can_edit
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

    @view.memoize
    def get_attachment_types(self):
        """Returns a list of available attachment types
        """
        query = {
            "portal_type": "AttachmentType",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }
        return api.search(query, SETUP_CATALOG)

    def get_attachment_report_options(self):
        """Returns the valid attachment report options
        """
        return ATTACHMENT_REPORT_OPTIONS.items()

    @view.memoize
    def get_analyses(self):
        """Returns the list of analyses for which the current user has
        privileges granted to add/edit/remove attachments
        """
        analyses = self.context.getAnalyses(full_objects=True)
        return filter(self.is_editable, analyses)

    @view.memoize
    def can_add_attachments(self):
        """Returns whether the current user is allowed to add attachments to
        current context, but not necessarily to analyses
        """
        return security.check_permission(SampleAddAttachment, self.context)

    @view.memoize
    def can_edit_attachments(self):
        """Returns whether the current user is allowed to edit attachments
        from current context, but not necessarily from analyses
        """
        return security.check_permission(SampleEditAttachment, self.context)

    @view.memoize
    def can_delete_attachments(self):
        """Returns whether the current user is allowed to delete attachments
        from current context, but not necessarily from analyses
        """
        return security.check_permission(SampleDeleteAttachment, self.context)

    def is_editable(self, analysis):
        """Returns whether the current user has privileges for the edition
        of the analysis passed in
        """
        return security.check_permission(FieldEditAnalysisResult, analysis)

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
        if isinstance(order, six.string_types):
            new_order = self.storage.get("order", [])
            new_order.append(order)
            order = new_order
        self.storage.update({"order": order})

    def get_attachments_order(self):
        """Returns a list of UIDs for sorting purposes.

        The order should be in the same order like the rows of the attachment
        listing viewlet.
        """
        return self.storage.get("order", [])
