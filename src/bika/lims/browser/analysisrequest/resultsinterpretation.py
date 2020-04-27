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
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.permissions import FieldEditResultsInterpretation
from plone import protect
from plone.app.textfield import RichTextValue
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import event


class ARResultsInterpretationView(BrowserView):
    """ Renders the view for ResultsInterpration per Department
    """
    template = ViewPageTemplateFile(
        "templates/analysisrequest_results_interpretation.pt")

    def __init__(self, context, request, **kwargs):
        super(ARResultsInterpretationView, self).__init__(context, request)
        self.request = request
        self.context = context

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_form_submit()
        return self.template()

    def handle_form_submit(self):
        """Handle form submission
        """
        protect.CheckAuthenticator(self.request)
        logger.info("Handle ResultsInterpration Submit")
        # Save the results interpretation
        res = self.request.form.get("ResultsInterpretationDepts", [])
        self.context.setResultsInterpretationDepts(res)
        self.add_status_message(_("Changes Saved"), level="info")
        # reindex the object after save to update all catalog metadata
        self.context.reindexObject()
        # notify object edited event
        event.notify(ObjectEditedEvent(self.context))
        return self.request.response.redirect(api.get_url(self.context))

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(FieldEditResultsInterpretation, self.context)

    def get_text(self, department, mode="raw"):
        """Returns the text saved for the selected department
        """
        row = self.context.getResultsInterpretationByDepartment(department)
        rt = RichTextValue(row.get("richtext", ""), "text/plain", "text/html")
        if mode == "output":
            return rt.output
        return rt.raw
