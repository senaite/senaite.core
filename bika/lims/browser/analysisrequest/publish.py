from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import to_utf8, encode_header, createPdf, attachPdf
from os.path import join
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters
import glob, os, sys, traceback
import App
import Globals

class AnalysisRequestPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_publish.pt")
    _ars = []
    _current_ar_index = 0
    _DEFAULT_TEMPLATE = 'default.pt'
    _publish = False

    def __init__(self, context, request, publish=False):
        super(AnalysisRequestPublishView, self).__init__(context, request)
        self._publish = publish
        self._ars = [self.context]

    def __call__(self):
        if self.context.portal_type == 'AnalysisRequest':
            self._ars = [self.context]
        elif self.context.portal_type == 'AnalysisRequestsFolder' \
            and self.request.get('items',''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._ars = [obj.getObject() for obj in uc(UID=uids)]
        else:
            #Do nothing
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Do publish?
        if self.request.get('pub', '0') == '1' or self._publish:
            self.publish()
        else:
            return self.template()

    def showOptions(self):
        return self.request.get('pub', '1') == '1';

    def publish(self):
        if len(self._ars) > 1:
            for ar in self._ars:
                arpub = AnalysisRequestPublishView(ar, self.request, publish=True)
                arpub.publish()
            return

        # Only one AR, create the report
        ar = self._ars[0]
        # SMTP errors are silently ignored if server is in debug mode
        debug_mode = App.config.getConfiguration().debug_mode
        # PDF and HTML files are written to disk if server is in debug mode
        out_path = join(Globals.INSTANCE_HOME, 'var') if debug_mode \
            else None
        out_fn = to_utf8(ar.Title())

        results_html = safe_unicode(self.template()).encode('utf-8')
        if out_path:
            open(join(out_path, out_fn + ".html"), "w").write(results_html)

        # Create the pdf report (will always be attached to the AR)
        pdf_outfile = join(out_path, out_fn + ".pdf") if out_path else None
        pdf_report = createPdf(results_html, pdf_outfile)


    def getAvailableFormats(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, 'templates/reports')
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        return out

    def getAnalysisRequests(self):
        return self._ars;

    def getAnalysisRequestsCount(self):
        return len(self._ars);

    def getAnalysisRequestObj(self):
        return self._ars[self._current_ar_index]

    def getAnalysisRequest(self):
        return self._ar_data(self._ars[self._current_ar_index])

    def _nextAnalysisRequest(self):
        if self._current_ar_index < len(self._ars):
            self._current_ar_index += 1

    def getReportTemplate(self):
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        embed = ViewPageTemplateFile("templates/reports/%s" % embedt);
        try:
            return embed(self)
        except:
            tbex = traceback.format_exc()
            return "<div class='error'>%s '%s':<pre>%s</pre></div>" % (_("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequest()

    def getReportStyle(self):
        template = self.request.get('template', self._DEFAULT_TEMPLATE)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, 'templates/reports/')
        path = '%s/%s.css' % (templates_dir, template[:-3])
        content = ''
        with open(path, 'r') as content_file:
            content = content_file.read()
        return content;

    def isQCAnalysesVisible(self):
        return self.request.get('qcvisible', '0').lower() in ['true', '1']

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
                'date_received': self.ulocalized_time(ar.getDateReceived(), long_format=1),
                'remarks': ar.getRemarks(),
                'member_discount': ar.getMemberDiscount(),
                'date_sampled': self.ulocalized_time(ar.getDateSampled(), long_format=1),
                'date_published': self.ulocalized_time(ar.getDatePublished(), long_format=1),
                'invoiced': ar.getInvoiced(),
                'late': ar.getLate(),
                'subtotal': ar.getSubtotal(),
                'vat_amount': ar.getVATAmount(),
                'totalprice': ar.getTotalPrice(),
                'invalid': ar.isInvalid(),
                'url': ar.absolute_url(),
                'remarks': to_utf8(ar.getRemarks()),
                'footer': to_utf8(self.context.bika_setup.getResultFooter()),
                'child_analysisrequest': None,
                'parent_analysisrequest': None}

        # Sub-objects
        if ar.getParentAnalysisRequest():
            data['parent_analysisrequest'] = self._artodict(ar.getParentAnalysisRequest())
        if ar.getChildAnalysisRequest():
            data['child_analysisrequest'] = self._artodict(ar.getChildAnalysisRequest())

        data['contact'] = self._contact_data(ar)
        data['client'] = self._client_data(ar)
        data['sample'] = self._sample_data(ar)
        data['batch'] = self._batch_data(ar)
        data['specifications'] = self._specs_data(ar)
        data['analyses'] = self._analyses_data(ar, ['verified', 'published'])
        data['qcanalyses'] = self._qcanalyses_data(ar, ['verified', 'published'])
        data['points_of_capture'] = sorted(set([an['point_of_capture'] for an in data['analyses']]))
        data['categories'] = sorted(set([an['category'] for an in data['analyses']]))
        data['haspreviousresults'] = len([an['previous_results'] for an in data['analyses'] if an['previous_results']]) > 0
        data['hasblanks'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'b']) > 0
        data['hascontrols'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'c']) > 0
        data['hasduplicates'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'd']) > 0

        # Categorize analyses
        data['categorized_analyses'] = {}
        for an in data['analyses']:
            poc = an['point_of_capture']
            cat = an['category']
            pocdict = data['categorized_analyses'].get(poc, {})
            catlist = pocdict.get(cat, [])
            catlist.append(an)
            pocdict[cat] = catlist
            data['categorized_analyses'][poc] = pocdict

        # Categorize qcanalyses
        data['categorized_qcanalyses'] = {}
        for an in data['qcanalyses']:
            qct = an['reftype']
            poc = an['point_of_capture']
            cat = an['category']
            qcdict = data['categorized_qcanalyses'].get(qct, {})
            pocdict = qcdict.get(poc, {})
            catlist = pocdict.get(cat, [])
            catlist.append(an)
            pocdict[cat] = catlist
            qcdict[poc] = pocdict
            data['categorized_qcanalyses'][qct] = qcdict
        data['reporter'] = self._reporter_data(ar)

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()

        return data

    def _batch_data(self, ar):
        data = {}
        batch = ar.getBatch()
        if batch:
            data = {'obj': batch,
                    'id': batch.id,
                    'title': to_utf8(batch.Title()),
                    'date': batch.getBatchDate(),
                    'client_batchid': to_utf8(batch.getClientBatchID()),
                    'remarks': to_utf8(batch.getRemarks())}

            uids = batch.getBatchLabels()
            uc = getToolByName(self.context, 'uid_catalog')
            data['labels'] = [to_utf8(p.getObject().Title()) for p in uc(UID=uids)]

        return data

    def _sample_data(self, ar):
        data = {}
        sample = ar.getSample()
        if sample:
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

            data['sample_type'] = self._sample_type(sample)
            data['sample_point'] = self._sample_point(sample)
        return data

    def _sample_type(self, sample=None):
        data = {}
        sampletype = sample.getSampleType() if sample else None
        if sampletype:
            data = {'obj': sampletype,
                    'id': sampletype.id,
                    'title': sampletype.Title(),
                    'url': sampletype.absolute_url()}
        return data

    def _sample_point(self, sample=None):
        samplepoint = sample.getSamplePoint() if sample else None
        data = {}
        if samplepoint:
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
                'confidence': lab.getConfidence(),
                'accredited': lab.getLaboratoryAccredited(),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'accreditation_logo': lab.getAccreditationBodyLogo(),
                'logo': "%s/logo_print.jpg" % portal.absolute_url()}

    def _contact_data(self, ar):
        data = {}
        contact = ar.getContact()
        if contact:
            data = {'obj': contact,
                    'fullname': to_utf8(contact.getFullname()),
                    'email': to_utf8(contact.getEmailAddress()),
                    'pubpref': contact.getPublicationPreference()}
        return data

    def _client_data(self, ar):
        data = {}
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

    def _specs_data(self, ar):
        data = {}
        specs = ar.getPublicationSpecification()
        if not specs:
            specs = ar.getSpecification()

        if specs:
            data['obj'] = specs
            data['id'] = specs.id
            data['url'] = specs.absolute_url()
            data['title'] = to_utf8(specs.Title())
            data['resultsrange'] = specs.getResultsRangeDict()

        return data

    def _analyses_data(self, ar, analysis_states=['verified', 'published']):
        analyses = []
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        for an in ar.getAnalyses(full_objects=True,
                                 review_state=analysis_states):

            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""
            if batch:
                keyword = an.getKeyword()
                bars = [bar for bar in batch.getAnalysisRequests() \
                            if an.aq_parent.UID() != bar.UID() \
                            and keyword in bar]
                for bar in bars:
                    pan = bar[keyword]
                    pan_state = workflow.getInfoFor(pan, 'review_state')
                    if pan.getResult() and pan_state in analysis_states:
                        pandict = self._analysis_data(pan)
                        andict['previous'].append(pandict)

                andict['previous'] = sorted(andict['previous'], key=itemgetter("capture_date"))
                andict['previous_results'] = ", ".join([p['formatted_result'] for p in andict['previous'][-5:]])

            analyses.append(andict)
        analyses.sort(lambda x, y: cmp(x.get('title').lower(), y.get('title').lower()))
        return analyses

    def _analysis_data(self, analysis):
        keyword = analysis.getKeyword()
        service = analysis.getService()
        andict = {'obj': analysis,
                  'id': analysis.id,
                  'title': analysis.Title(),
                  'keyword': keyword,
                  'accredited': service.getAccredited(),
                  'point_of_capture': to_utf8(POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())),
                  'category': to_utf8(service.getCategoryTitle()),
                  'result': analysis.getResult(),
                  'unit': to_utf8(service.getUnit()),
                  'capture_date': analysis.getResultCaptureDate(),
                  'request_id': analysis.aq_parent.getId(),
                  'formatted_result': '',
                  'uncertainty': analysis.getUncertainty(),
                  'retested': analysis.getRetested(),
                  'remarks': to_utf8(analysis.getRemarks()),
                  'resultdm': to_utf8(analysis.getResultDM()),
                  'outofrange': False,
                  'type': analysis.portal_type,
                  'reftype': analysis.getReferenceType() \
                            if hasattr(analysis, 'getReferenceType')
                            else None,
                  'worksheet': None,
                  'specs': {},
                  'formatted_specs': ''}

        if analysis.portal_type == 'DuplicateAnalysis':
            andict['reftype'] = 'd'

        ws = analysis.getBackReferences('WorksheetAnalysis')
        andict['worksheet'] = ws[0].id if ws and len(ws) > 0 else None
        andict['worksheet_url'] = ws[0].absolute_url if ws and len(ws) > 0 else None
        andict['refsample'] = analysis.getSample().id \
                            if analysis.portal_type == 'Analysis' \
                            else '%s - %s' % (analysis.aq_parent.id, analysis.aq_parent.Title())

        # Which analysis specs must be used?
        # Try first with those defined at AR Publish Specs level
        if analysis.portal_type == 'ReferenceAnalysis':
            # The analysis is a Control or Blank. We might use the
            # reference results instead other specs
            uid = analysis.getServiceUID()
            specs = analysis.aq_parent.getResultsRangeDict().get(uid, {})

        elif analysis.portal_type == 'DuplicateAnalysis':
            specs = analysis.getAnalysisSpecs();

        else:
            ar = analysis.aq_parent
            specs = ar.getPublicationSpecification()
            if not specs or keyword not in specs.getResultsRangeDict():
                specs = analysis.getAnalysisSpecs()
            specs = specs.getResultsRangeDict().get(keyword, {}) \
                    if specs else {}

        andict['specs'] = specs
        andict['formatted_result'] = analysis.getFormattedResult(specs)

        if specs.get('min', None) and specs.get('max', None):
            andict['formatted_specs'] = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            andict['formatted_specs'] = '> %s' % specs['min']
        elif specs.get('max', None):
            andict['formatted_specs'] = '< %s' % specs['max']

        # Out of range?
        if specs:
            adapters = getAdapters((analysis, ), IResultOutOfRange)
            bsc = getToolByName(self.context, "bika_setup_catalog")
            for name, adapter in adapters:
                ret = adapter(specification=specs)
                if ret and ret['out_of_range']:
                    andict['outofrange'] = True
                    break
        return andict

    def _qcanalyses_data(self, ar, analysis_states=['verified', 'published']):
        analyses = []
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        for an in ar.getQCAnalyses(review_state=analysis_states):

            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""

            analyses.append(andict)
        analyses.sort(lambda x, y: cmp(x.get('title').lower(), y.get('title').lower()))
        return analyses

    def _reporter_data(self, ar):
        data = {}
        member = self.context.portal_membership.getAuthenticatedMember()
        if member:
            username = member.getUserName()
            data['username'] = username
            data['fullname'] = to_utf8(self.user_fullname(username))
            data['email'] = to_utf8(self.user_email(username))

            c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
                 if x.getObject().getUsername() == username]
            if c:
                sf = c[0].getObject().getSignature()
                if sf:
                    data['signature'] = sf.absolute_url() + "/Signature"

        return data
