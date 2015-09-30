import tempfile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.utils import t, formatDecimalMark
from bika.lims.utils.analysis import format_uncertainty, format_numeric_result
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
from bika.lims.utils import createPdf
from bika.lims.utils import to_utf8
from bika.lims.vocabularies import CatalogVocabulary
from cStringIO import StringIO
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from Products.CMFPlone.utils import safe_unicode

import App
import Globals
import os
import plone


class PublishView(BrowserView):
    """Publish a single Batch.
    """

    template = ViewPageTemplateFile("../templates/batch_publish.pt")

    def __call__(self):

        pc = self.portal_catalog
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
            client_address = self.client.getPostalAddress()
            if self.contact and not client_address:
                client_address = self.contact.getBillingAddress()
                if not client_address:
                    client_address = self.contact.getPhysicalAddress()
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
            # datereceived = ar.getDateReceived()
            # datepublished = ar.getDatePublished()
            datalines = []
            for analysis in ar.getAnalyses(full_objects=True):
                service = analysis.getService()
                method = service.getMethod()
                sample = ar.getSample()
                result = analysis.getResult()
                formatted_result = format_numeric_result(analysis, result)
                datalines.append({_("Analysis Service"): analysis.getService().Title(),
                                  _("Method"): method and method.Title() or "",
                                  _("Result"): formatted_result,
                                  _("Analyst"): self.user_fullname(analysis.getAnalyst()),
                                  _("Remarks"): analysis.getRemarks()})
            self.ars.append({
                        _("Request ID"): ar.getRequestID(),
                                _("Date Requested"): self.ulocalized_time(datecreated),  # requested->created
                        _("Sample Type"): sample.getSampleType() and sample.getSampleType().Title() or '',
                                _("Sample Point"): sample.getSamplePoint() and sample.getSamplePoint().Title() or '',
                        _("datalines"): datalines,
                        })

        # Create Report
        fn = self.context.Title() + " " + self.ulocalized_time(self.now)
        report_html = self.template()

        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fd, tmp_fn = tempfile.mkstemp(suffix=".html")
            logger.debug("Writing HTML for %s to %s" % (self.context, tmp_fn))
            tmp_fd.write(report_html)
            tmp_fd.close()

        pdf_fd, pdf_fn = tempfile.mkstemp(suffix="pdf")
        pdf_fd.close()
        pdf = createPdf(report_html, outfile=pdf_fn)
        if debug_mode:
            logger.debug("Wrote PDF for %s to %s" % (self.context, pdf_fn))
        else:
            os.remove(pdf_fn)

        # XXX Email published batches to who?

        # Send PDF to browser
        if not pdf.err:
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            setheader("Content-Disposition", "attachment;filename=\"%s\"" % fn)
            self.request.RESPONSE.write(pdf)

