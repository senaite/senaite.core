# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.permissions import FieldEditResultsInterpretation
from plone import protect
from plone.app.layout.viewlets import ViewletBase
from plone.app.textfield import RichTextValue
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import event


class ResultsInterpretationViewlet(ViewletBase):
    """Viewlet for results interpretation field
    """
    index = ViewPageTemplateFile("templates/resultsinterpretation.pt")

    title = _("Results interpretation")
    icon_name = "resultsinterpretation"

    def available(self):
        return True

    def update(self):
        if self.request.form.get("submitted", False):
            return self.handle_form_submit()
        return self.index()

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

    def get_interpretation_templates(self):
        """Return a list of datainfo dicts representing interpretation templates
        """
        query = {"portal_type": "InterpretationTemplate",
                 "review_state": "active"}

        def get_data_info(item):
            return {
                "uid": api.get_uid(item),
                "title": api.get_title(item)
            }

        brains = api.search(query, SETUP_CATALOG)
        return map(get_data_info, brains)
