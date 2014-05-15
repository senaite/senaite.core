from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import sys, traceback

class AnalysisRequestPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_publish.pt")
    _ars = []
    _current_ar_index = 0

    def getAvailableFormats(self):
        return [ {'id': 'A4_default.pt',
                  'title': 'A4 Default' },
                 {'id': 'A4_custom_01.pt',
                  'title': 'A4 Custom' } ]

    def __call__(self):
        self._ars = [self.context, self.context]
        return self.template()

    def getAnalysisRequestsCount(self):
        return len(self._ars);

    def getAnalysisRequest(self):
        return self._ar_data(self._ars[self._current_ar_index])

    def _nextAnalysisRequest(self):
        if self._current_ar_index < len(self._ars):
            self._current_ar_index += 1

    def getReportTemplate(self):
        embedt = self.request.get('template', 'A4_default.pt')
        embed = ViewPageTemplateFile("templates/reports/%s" % embedt);
        try:
            return embed(self)
        except:
            tbex = traceback.format_exc()
            return "<div class='error'>%s '%s':<pre>%s</pre></div>" % (_("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequest()


    def _ar_data(self, ar):
        data = {'obj': ar,
                'id': ar.getRequestID(),
                'client_order_num': ar.getClientOrderNumber(),
                'client_reference': ar.getClientReference(),
                'client_sampleid': ar.getClientSampleID(),
                'adhoc': ar.getAdHoc(),
                'composite': ar.getComposite(),
                'report_drymatter': ar.getReportDryMatter(),
                'invoice_exclude': ar.getInvoiceExclude(),
                'date_received': ar.getDateReceived(),
                'remarks': ar.getRemarks(),
                'member_discount': ar.getMemberDiscount(),
                'date_sampled': ar.getDateSampled(),
                'invoiced': ar.getInvoiced(),
                'late': ar.getLate(),
                'subtotal': ar.getSubtotal(),
                'vat_amount': ar.getVATAmount(),
                'totalprice': ar.getTotalPrice(),
                'invalid': ar.isInvalid(),
                'url': ar.absolute_url(),
                'child_analysisrequest': None,
                'parent_analysisrequest': None}

        # Sub-objects
        if ar.getParentAnalysisRequest():
            data['parent_analysisrequest'] = self._artodict(ar.getParentAnalysisRequest())
        if ar.getChildAnalysisRequest():
            data['child_analysisrequest'] = self._artodict(ar.getChildAnalysisRequest())

        data['contact'] = self._contact_data(ar)
        data['client'] = self._client_data(ar)
        data['sample'] = self._sample_data(ar.getSample())
        data['batch'] = self._batch_data(ar.getBatch())

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()

        return data

    def _batch_data(self, batch=None):
        if not batch:
            return {}
        data = {'obj': batch,
                'id': batch.id,
                'title': batch.Title(),
                'date': batch.getBatchDate(),
                'client_batchid': batch.getClientBatchID(),
                'remarks': batch.getRemarks()}
        return data

    def _sample_data(self, sample):
        data = {'obj': sample,
                'id': sample.id,
                'url': sample.absolute_url(),
                'client_sampleid': sample.getClientSampleID(),
                'date_sampled': sample.getDateSampled(),
                'sampling_date': sample.getSamplingDate(),
                'sampler': sample.getSampler(),
                'date_received': sample.getDateReceived(),
                'composite': sample.getComposite(),
                'date_expired': sample.getDateExpired(),
                'date_disposal': sample.getDisposalDate(),
                'date_disposed': sample.getDateDisposed(),
                'adhoc': sample.getAdHoc(),
                'remarks': sample.getRemarks() }

        data['sample_type'] = self._sample_type(sample.getSampleType())
        data['sample_point'] = self._sample_point(sample.getSamplePoint())
        return data

    def _sample_type(self, sampletype=None):
        if not sampletype:
            return {}
        data = {'obj': sampletype,
                'id': sampletype.id,
                'title': sampletype.Title(),
                'url': sampletype.absolute_url()}
        return data

    def _sample_point(self, samplepoint=None):
        if not samplepoint:
            return {}
        data = {'obj': samplepoint,
                'id': samplepoint.id,
                'title': samplepoint.Title(),
                'url': samplepoint.absolute_url()}
        return data

    def _lab_data(self):
        portal = self.context.portal_url.getPortalObject()
        lab = self.context.bika_setup.laboratory
        lab_address = lab.getPostalAddress() \
                        or lab.getBillingAddress() \
                        or lab.getPhysicalAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % lab_address.get(v) for v in _keys
                     if lab_address.get(v)]
            lab_address = "".join(_list)
        else:
            lab_address = ''

        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'address': to_utf8(lab_address),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'logo': "%s/logo_print.jpg" % portal.absolute_url()}

    def _contact_data(self, ar):
        data = {'obj': None,
                'fullname': '',
                'email': '',
                'pubpref': '',}

        contact = ar.getContact()
        if contact:
            data['obj'] = contact
            data['fullname'] = to_utf8(contact.getFullname())
            data['email'] = to_utf8(contact.getEmailAddress())
            data['pubpref'] = contact.getPublicationPreference()

        return data

    def _client_data(self, ar):
        data = {'obj': None,
                'id': '',
                'url': '',
                'name': '',
                'phone': '',
                'fax': '',
                'address': '',}

        client = ar.aq_parent
        if client:
            data['obj'] = client
            data['id'] = client.id
            data['url'] = client.absolute_url()
            data['name'] = to_utf8(client.getName())
            data['phone'] = to_utf8(client.getPhone())
            data['fax'] = to_utf8(client.getFax())

            client_address = client.getPostalAddress()
            if not client_address:
                # Data from the first contact
                contact = self.getAnalysisRequest().getContact()
                if contact and contact.getBillingAddress():
                    client_address = contact.getBillingAddress()
                elif contact and contact.getPhysicalAddress():
                    client_address = contact.getPhysicalAddress()

            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>" % client_address.get(v) for v in _keys
                         if client_address.get(v)]
                client_address = "".join(_list)
            else:
                client_address = ''
            data['address'] = to_utf8(client_address)

        return data
