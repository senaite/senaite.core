from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.config import VERIFIED_STATES
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.interfaces import IInvoiceView
from bika.lims.permissions import *
from bika.lims.utils import to_utf8, isAttributeHidden
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

import plone

class InvoiceView(BrowserView):

    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/analysisrequest_invoice.pt")
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")
    title = _('Invoice')
    description = ''

    def __call__(self):
        context = self.context
        workflow = getToolByName(context, 'portal_workflow')
        # Collect related data and objects
        invoice = context.getInvoice()
        sample = context.getSample()
        samplePoint = sample.getSamplePoint()
        reviewState = workflow.getInfoFor(context, 'review_state')
        # Collection invoice information
        if invoice:
            self.invoiceId = invoice.getId()
        else:
            self.invoiceId = _('Proforma (Not yet invoiced)')
        # Collect verified invoice information
        verified = reviewState in VERIFIED_STATES
        if verified:
            self.verifiedBy = context.getVerifier()
        self.verified = verified
        self.request['verified'] = verified
        # Collect published date
        datePublished = context.getDatePublished()
        if datePublished is not None:
            datePublished = self.ulocalized_time(
                datePublished, long_format=1
            )
        self.datePublished = datePublished
        # Collect received date
        dateReceived = context.getDateReceived()
        if dateReceived is not None:
            dateReceived = self.ulocalized_time(dateReceived, long_format=1)
        self.dateReceived = dateReceived
        # Collect general information
        self.reviewState = reviewState
        contact = self.getContact()
        self.contact = context.getContact().Title() if contact else ""
        self.clientOrderNumber = context.getClientOrderNumber()
        self.clientReference = context.getClientReference()
        self.clientSampleId = sample.getClientSampleID()
        self.sampleType = sample.getSampleType().Title()
        self.samplePoint = samplePoint and samplePoint.Title()
        self.requestId = context.getRequestID()
        self.headers = [
            {'title': 'Invoice ID', 'value': self.invoiceId},
            {'title': 'Client Reference', 
                'value': self.clientReference },
            {'title': 'Sample Type', 'value': self.sampleType},
            {'title': 'Request ID', 'value': self.requestId},
            {'title': 'Date Received', 'value': self.dateReceived},
        ]
        if not isAttributeHidden('AnalysisRequest', 'ClientOrderNumber'):
            self.headers.append({'title': 'Client Sample Id', 
                                 'value': self.clientOrderNumber})
        if not isAttributeHidden('AnalysisRequest', 'SamplePoint'):
            self.headers.append(
                {'title': 'Sample Point', 'value': self.samplePoint})
        if self.verified:
            self.headers.append(
                {'title': 'Verified By', 'value': self.verifiedBy})
            if self.datePublished:
                self.headers.append(
                    {'title': 'datePublished', 'value': self.datePublished})

		#	<tal:published tal:condition="view/datePublished">
		#		<th i18n:translate="">Date Published</th>
		#		<td tal:content="view/datePublished"></td>
		#	</tal:published>
		#</tr>

        # Retrieve required data from analyses collection
        analyses = []
        for analysis in context.getRequestedAnalyses():
            service = analysis.getService()
            categoryName = service.getCategory().Title()
            # Find the category
            try:
                category = (
                    o for o in analyses if o['name'] == categoryName
                ).next()
            except:
                category = {'name': categoryName, 'analyses': []}
                analyses.append(category)
            # Append the analysis to the category
            category['analyses'].append({
                'title': analysis.Title(),
                'price': analysis.getPrice(),
                'priceVat': "%.2f" % analysis.getVATAmount(),
                'priceTotal': "%.2f" % analysis.getTotalPrice(),
            })
        self.analyses = analyses
        # Get totals
        self.subtotal = context.getSubtotal()
        self.vatTotal = "%.2f" % context.getVATTotal()
        self.totalPrice = "%.2f" % context.getTotalPrice()
        # Render the template
        return self.template()


class InvoicePrintView(InvoiceView):

    template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)
