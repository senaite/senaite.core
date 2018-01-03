# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from Products.CMFCore.WorkflowCore import WorkflowException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.config import VERIFIED_STATES
from bika.lims.interfaces import IInvoiceView
from bika.lims.permissions import *
from bika.lims.utils import to_utf8, isAttributeHidden, encode_header
from bika.lims.workflow import doActionFor, getTransitionDate
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from decimal import Decimal

import plone, App

class InvoiceView(BrowserView):

    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/analysisrequest_invoice.pt")
    print_template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")
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
        self.datePublished = \
            self.ulocalized_time(getTransitionDate(context, 'publish'),
                                 long_format=1)
        # Collect received date
        dateReceived = context.getDateReceived()
        if dateReceived is not None:
            dateReceived = self.ulocalized_time(dateReceived, long_format=1)
        self.dateReceived = dateReceived
        # Collect general information
        self.reviewState = reviewState
        contact = context.getContact()
        self.contact = contact.Title() if contact else ""
        self.clientOrderNumber = context.getClientOrderNumber()
        self.clientReference = context.getClientReference()
        self.clientSampleId = sample.getClientSampleID()
        self.sampleType = sample.getSampleType().Title()
        self.samplePoint = samplePoint and samplePoint.Title()
        self.requestId = context.getId()
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

        analyses = []
        profiles = []
        # Retrieve required data from analyses collection
        all_analyses, all_profiles, analyses_from_profiles = context.getServicesAndProfiles()
        # Relating category with solo analysis
        for analysis in all_analyses:
            categoryName = analysis.getCategoryTitle()
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
        # Relating analysis services with their profiles
        # We'll take the analysis contained on each profile
        for profile in all_profiles:
            # If profile's checkbox "Use Analysis Profile Price" is enabled, only the profile price will be displayed.
            # Otherwise each analysis will display its own price.
            pservices = []
            if profile.getUseAnalysisProfilePrice():
                # We have to use the profiles price only
                for pservice in profile.getService():
                    pservices.append({
                               'title': pservice.Title(),
                               'price': None,
                               'priceVat': None,
                               'priceTotal': None,
                               })
                profiles.append({'name': profile.title,
                                 'price': profile.getAnalysisProfilePrice(),
                                 'priceVat': profile.getVATAmount(),
                                 'priceTotal': profile.getTotalPrice(),
                                 'analyses': pservices})
            else:
                # We need the analyses prices instead of profile price
                for pservice in profile.getService():
                    # We want the analysis instead of the service, because we want the price for the client
                    # (for instance the bulk price)
                    panalysis = self._getAnalysisForProfileService(pservice.getKeyword(), analyses_from_profiles)
                    pservices.append({
                                     'title': pservice.Title(),
                                     'price': panalysis.getPrice() if panalysis else pservice.getPrice(),
                                     'priceVat': "%.2f" % panalysis.getVATAmount() if panalysis
                                                                                   else pservice.getVATAmount(),
                                     'priceTotal': "%.2f" % panalysis.getTotalPrice() if panalysis
                                                                                   else pservice.getTotalPrice(),
                                     })
                profiles.append({'name': profile.title,
                                 'price': None,
                                 'priceVat': None,
                                 'priceTotal': None,
                                 'analyses': pservices})
        self.analyses = analyses
        self.profiles = profiles
        # Get subtotals
        self.subtotal = context.getSubtotal()
        self.subtotalVATAmount = "%.2f" % context.getSubtotalVATAmount()
        self.subtotalTotalPrice = "%.2f" % context.getSubtotalTotalPrice()
        # Get totals
        self.memberDiscount = Decimal(context.getDefaultMemberDiscount())
        self.discountAmount = context.getDiscountAmount()
        self.VATAmount = "%.2f" % context.getVATAmount()
        self.totalPrice = "%.2f" % context.getTotalPrice()
        # Render the template
        return self.template()

    def _getAnalysisForProfileService(self, service_keyword, analyses):
        """
        This function gets the analysis object from the analyses list using the keyword 'service_keyword'
        :service_keyword: a service keyword
        :analyses: a list of analyses
        """
        for analysis in analyses:
            if service_keyword == analysis.getKeyword():
                return analysis
        return None

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class InvoicePrintView(InvoiceView):

    template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)

class InvoiceCreate(InvoiceView):
    """
    It generates an invoice object with the proforma information in the AR/invoice.
    """
    security = ClassSecurityInfo()

    def __call__(self):
        # Create the invoice object and link it to the current AR.
        self.context.issueInvoice(RESPONSE=self.request.response)
        # Run the InvoiceView __call__ is necessary to fill out the template required fields.
        InvoiceView.__call__(self)
        # Get the invoice template in HTML format
        templateHTML = self.print_template()
        # Send emails with the invoice
        self.emailInvoice(templateHTML)
        # Reload the page to see the the new fields
        self.request.response.redirect(
            '%s/invoice' % self.aq_parent.absolute_url())

    security.declarePublic('printInvoice')

    def emailInvoice(self, templateHTML, to=[]):
        """
        Send the invoice via email.
        :param templateHTML: The invoice template in HTML, ready to be send.
        :param to: A list with the addresses to send the invoice.
        """
        ar = self.aq_parent
        # SMTP errors are silently ignored if server is in debug mode
        debug_mode = App.config.getConfiguration().debug_mode
        # Useful variables
        lab = ar.bika_setup.laboratory
        # Compose and send email.
        subject = t(_('Invoice')) + ' ' + ar.getInvoice().getId()
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = subject
        mime_msg['From'] = formataddr(
            (encode_header(lab.getName()), lab.getEmailAddress()))
        mime_msg.preamble = 'This is a multi-part MIME message.'
        msg_txt_t = MIMEText(templateHTML.encode('utf-8'), _subtype='html')
        mime_msg.attach(msg_txt_t)

        # Build the responsible's addresses
        mngrs = ar.getResponsible()
        for mngrid in mngrs['ids']:
            name = mngrs['dict'][mngrid].get('name', '')
            email = mngrs['dict'][mngrid].get('email', '')
            if (email != ''):
                to.append(formataddr((encode_header(name), email)))
        # Build the client's address
        caddress = ar.aq_parent.getEmailAddress()
        cname = ar.aq_parent.getName()
        if (caddress != ''):
                to.append(formataddr((encode_header(cname), caddress)))
        if len(to) > 0:
            # Send the emails
            mime_msg['To'] = ','.join(to)
            try:
                host = getToolByName(ar, 'MailHost')
                host.send(mime_msg.as_string(), immediate=True)
            except SMTPServerDisconnected as msg:
                pass
                if not debug_mode:
                    raise SMTPServerDisconnected(msg)
            except SMTPRecipientsRefused as msg:
                raise WorkflowException(str(msg))
