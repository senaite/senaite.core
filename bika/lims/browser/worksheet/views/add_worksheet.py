# coding=utf-8
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import PMF, logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import getUsers, tmpID
from bika.lims.utils import to_utf8 as _c
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone
import json
import zope


class AddWorksheetView(BrowserView):
    """ Handler for the "Add Worksheet" button in Worksheet Folder.
        If a template was selected, the worksheet is pre-populated here.
    """

    def __call__(self):

        # Validation
        form = self.request.form
        analyst = self.request.get('analyst', '')
        template = self.request.get('template', '')
        instrument = self.request.get('instrument', '')

        if not analyst:
            message = _("Analyst must be specified.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, "portal_workflow")
        pm = getToolByName(self.context, "portal_membership")

        ws = _createObjectByType("Worksheet", self.context, tmpID())
        ws.processForm()

        # Set analyst and instrument
        ws.setAnalyst(analyst)
        if instrument:
            ws.setInstrument(instrument)

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not template:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(template)
        ws.setWorksheetTemplate(wst)
        ws.applyWorksheetTemplate(wst)

        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            msg = _("No analyses were added")
            self.context.plone_utils.addPortalMessage(msg)
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
