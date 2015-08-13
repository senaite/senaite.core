# coding=utf-8
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referencesample import ReferenceSamplesView
from bika.lims.exportimport import instruments
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import to_utf8
from bika.lims.utils import getUsers, isActive, tmpID
from DateTime import DateTime
from DocumentTemplate import sequence
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time
from bika.lims.utils import to_utf8 as _c

import plone
import plone.protect
import json

class ExportView(BrowserView):
    """
    """
    def __call__(self):

        translate = self.context.translate

        instrument = self.context.getInstrument()
        if not instrument:
            self.context.plone_utils.addPortalMessage(
                _("You must select an instrument"), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instrument.getDataInterface()
        if not exim:
            self.context.plone_utils.addPortalMessage(
                _("Instrument has no data interface selected"), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # exim refers to filename in instruments/
        if type(exim) == list:
            exim = exim[0]
        exim = exim.lower()

        # search instruments module for 'exim' module
        if not hasattr(instruments, exim):
            self.context.plone_utils.addPortalMessage(
                _("Instrument exporter not found"), 'error')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = getattr(instruments, exim)
        exporter = exim.Export(self.context, self.request)
        data = exporter(self.context.getAnalyses())
        pass
