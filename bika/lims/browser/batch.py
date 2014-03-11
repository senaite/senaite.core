from AccessControl import getSecurityManager
from bika.lims import PMF, logger, bikaMessageFactory as _, deprecated
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction, AnalysisRequestsView, AnalysisRequestAddView
from bika.lims.browser.bika_listing import BikaListingView, WorkflowAction
from bika.lims.browser.client import ClientAnalysisRequestsView, ClientSamplesView
from bika.lims.browser.sample import SamplesView
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import IContacts
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.permissions import *
from bika.lims.subscribers import doActionFor, skip
from bika.lims.utils import isActive
from bika.lims.utils import createPdf
from bika.lims.vocabularies import CatalogVocabulary
from cStringIO import StringIO
from DateTime import DateTime
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.indexer.decorator import indexer
from Products.AdvancedQuery import Or, MatchRegexp, Between
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements
from Products.CMFPlone.utils import safe_unicode

import App
import Globals
import json
import os
import plone
from bika.lims.workflow import getCurrentState, StateFlow, InactiveState


class BatchAnalysisRequestsView(AnalysisRequestsView, AnalysisRequestAddView):
    template = ViewPageTemplateFile("templates/analysisrequests.pt")
    ar_add = ViewPageTemplateFile("templates/ar_add.pt")

    def __init__(self, context, request):
        super(BatchAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getBatchUID'] = self.context.UID()

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # Client contact required (if client is associated)
            client = self.context.getClient()
            if hasattr(client, 'getContacts') and client.getContacts():
                self.context_actions[self.context.translate(_('Add new'))] = {
                    'url': self.context.absolute_url() + "/portal_factory/"
                    "AnalysisRequest/Request new analyses/ar_add?col_count=1",
                    'icon': '++resource++bika.lims.images/add.png'}
            # else:
            #     msg = _("Client contact required before request may be submitted")
            #     addPortalMessage(self.context.translate(msg))
        return super(BatchAnalysisRequestsView, self).__call__()

    def getMemberDiscountApplies(self):
        client = self.context.getClient()
        return client and client.getMemberDiscountApplies() or False

    def getRestrictedCategories(self):
        client = self.context.getClient()
        return client and client.getRestrictedCategories() or []

    def getDefaultCategories(self):
        client = self.context.getClient()
        return client and client.getDefaultCategories() or []


class BatchSamplesView(SamplesView):

    def __init__(self, context, request):
        super(BatchSamplesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/samples"
        if 'path' in self.contentFilter:
            del(self.contentFilter['path'])

    def contentsMethod(self, contentFilter):
        tool = getToolByName(self.context, self.catalog)
        state = [x for x in self.review_states if x['id'] == self.review_state][0]
        for k,v in state['contentFilter'].items():
            self.contentFilter[k] = v
        tool_samples = tool(contentFilter)
        samples = {}
        for sample in (p.getObject() for p in tool_samples):
            for ar in sample.getAnalysisRequests():
                if ar.getBatchUID() == self.context.UID():
                    samples[sample.getId()] = sample
        return samples.values()


class BatchPublishView(BrowserView):
    """Publish a single Batch.
    """

    template = ViewPageTemplateFile("../browser/templates/batch_publish.pt")

    def __call__(self):

        pc = self.portal_catalog
        bc = self.bika_catalog
        bsc = self.bika_setup_catalog
        self.checkPermission = self.context.portal_membership.checkPermission
        self.now = DateTime()
        self.SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        # Client details (if client is associated)
        self.client = None
        client_uid = hasattr(self.context, 'getClientUID') and self.context.getClientUID()
        if client_uid:
            proxies = pc(portal_type='Client', UID=client_uid)
        if proxies:
            self.client = proxies[0].getObject()
            client_address = self.client.getPostalAddress() \
                or self.contact.getBillingAddress() \
                or self.contact.getPhysicalAddress()
            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = [client_address.get(v) for v in _keys if client_address.get(v)]
                self.client_address = "<br/>".join(_list).replace("\n", "<br/>")
                if self.client_address.endswith("<br/>"):
                    self.client_address = self.client_address[:-5]
            else:
                self.client_address = None

        # Reporter
        self.member = self.context.portal_membership.getAuthenticatedMember()
        self.username = self.member.getUserName()
        self.reporter = self.user_fullname(self.username)
        self.reporter_email = self.user_email(self.username)
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == self.username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        # laboratory
        self.laboratory = self.context.bika_setup.laboratory
        self.accredited = self.laboratory.getLaboratoryAccredited()
        lab_address = self.laboratory.getPrintAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = [lab_address.get(v) for v in _keys if lab_address.get(v)]
            self.lab_address = "<br/>".join(_list).replace("\n", "<br/>")
            if self.lab_address.endswith("<br/>"):
                self.lab_address = self.lab_address[:-5]
        else:
            self.lab_address = None

        # Analysis Request results
        self.ars = []
        self.ar_headers = [_("Request ID"),
                           _("Date Requested"),
                           _("Sample Type"),
                           _("Sample Point")]
        self.analysis_headers = [_("Analysis Service"),
                                 _("Method"),
                                 _("Result"),
                                 _("Analyst")]
        for ar in self.context.getAnalysisRequests():
            datecreated = ar.created()
            datereceived = ar.getDateReceived()
            datepublished = ar.getDatePublished()
            datalines = []
            for analysis in ar.getAnalyses(full_objects=True):
                service = analysis.getService()
                method = service.getMethod()
                sample = ar.getSample()
                result = analysis.getResult()
                try:
                    precision = service.getPrecision() and service.getPrecision() or "2"
                    result = float(result)
                    formatted_result = str("%." + precision + "f")%result
                except:
                    precision = "2"
                    formatted_result = result
                datalines.append({_("Analysis Service"): analysis.getService().Title(),
                                  _("Method"): method and method.Title() or "",
                                  _("Result"): formatted_result,
                                  _("Analyst"): self.user_fullname(analysis.getAnalyst()),
                                  _("Remarks"): analysis.getRemarks()})
            self.ars.append({
                        _("Request ID"): ar.getRequestID(),
                                _("Date Requested"): self.ulocalized_time(datecreated), # requested->created
                        _("Sample Type"): sample.getSampleType() and sample.getSampleType().Title() or '',
                                _("Sample Point"): sample.getSamplePoint() and sample.getSamplePoint().Title() or '',
                        _("datalines"): datalines,
                        })

        # Create Report
        fn = self.context.Title() + " " + self.ulocalized_time(self.now)
        report_html = self.template()

        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            open(os.path.join(Globals.INSTANCE_HOME,'var', fn + ".html"),
                 "w").write(report_html)

        ramdisk = StringIO()
        pdf = createPdf(report_html, ramdisk)
        pdf_data = ramdisk.getvalue()
        ramdisk.close()

        if debug_mode:
            open(os.path.join(Globals.INSTANCE_HOME,'var', fn + ".pdf"),
                 "wb").write(pdf_data)

        # Email to who?

        # Send PDF to browser
        if not pdf.err:
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            setheader("Content-Disposition", "attachment;filename=\"%s\""%fn)
            self.request.RESPONSE.write(pdf_data)


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact'
        )
