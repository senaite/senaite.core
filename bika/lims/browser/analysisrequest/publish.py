from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from bika.lims import bikaMessageFactory as _, t
from bika.lims.utils import to_utf8, formatDecimalMark
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import to_utf8, encode_header, createPdf, attachPdf
from DateTime import DateTime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from operator import itemgetter
from os.path import join
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
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
        if self.request.form.get('publish', '0') == '1':
            self.publishFromPOST()
        else:
            return self.template()

    def showOptions(self):
        """ Returns true if the options top panel will be displayed
            in the template
        """
        return self.request.get('pub', '1') == '1';

    def getAvailableFormats(self):
        """ Returns the available formats found in templates/reports
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, 'templates/reports')
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        return out

    def getAnalysisRequests(self):
        """ Returns a dict with the analysis requests to manage
        """
        return self._ars;

    def getAnalysisRequestsCount(self):
        """ Returns the number of analysis requests to manage
        """
        return len(self._ars);

    def getAnalysisRequestObj(self):
        """ Returns the analysis request objects to be managed
        """
        return self._ars[self._current_ar_index]

    def getAnalysisRequest(self):
        """ Returns the dict for the currently managed analysis request
        """
        return self._ar_data(self._ars[self._current_ar_index])

    def _nextAnalysisRequest(self):
        """ Move to the next analysis request
        """
        if self._current_ar_index < len(self._ars):
            self._current_ar_index += 1

    def getReportTemplate(self):
        """ Returns the html template for the current ar and moves to
            the next ar to be processed. Uses the selected template
            specified in the request ('template' parameter)
        """
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        embed = ViewPageTemplateFile("templates/reports/%s" % embedt);
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            arid = self._ars[self._current_ar_index].id
            reptemplate = "<div class='error-report'>%s - %s '%s':<pre>%s</pre></div>" % (arid, _("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequest()
        return reptemplate

    def getReportStyle(self):
        """ Returns the css style to be used for the current template.
            If the selected template is 'default.pt', this method will
            return the content from 'default.css'. If no css file found
            for the current template, returns empty string
        """
        template = self.request.get('template', self._DEFAULT_TEMPLATE)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, 'templates/reports/')
        path = '%s/%s.css' % (templates_dir, template[:-3])
        content = ''
        with open(path, 'r') as content_file:
            content = content_file.read()
        return content;

    def isQCAnalysesVisible(self):
        """ Returns if the QC Analyses must be displayed
        """
        return self.request.get('qcvisible', '0').lower() in ['true', '1']

    def _ar_data(self, ar, excludearuids=[]):
        """ Creates an ar dict, accessible from the view and from each
            specific template.
        """
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
                'prepublish': False,
                'child_analysisrequest': None,
                'parent_analysisrequest': None}

        # Sub-objects
        excludearuids.append(ar.UID())
        puid = ar.getRawParentAnalysisRequest()
        if puid and puid not in excludearuids:
            data['parent_analysisrequest'] = self._ar_data(ar.getParentAnalysisRequest(), excludearuids)
        cuid = ar.getRawChildAnalysisRequest()
        if cuid and cuid not in excludearuids:
            data['child_analysisrequest'] = self._ar_data(ar.getChildAnalysisRequest(), excludearuids)

        wf = getToolByName(ar, 'portal_workflow')
        allowed_states = ['verified', 'published']
        data['prepublish'] = wf.getInfoFor(ar, 'review_state') not in allowed_states

        data['contact'] = self._contact_data(ar)
        data['client'] = self._client_data(ar)
        data['sample'] = self._sample_data(ar)
        data['batch'] = self._batch_data(ar)
        data['specifications'] = self._specs_data(ar)
        data['sample_matrix'] = self._sample_matrix(ar)
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
        data['managers'] = self._managers_data(ar)

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
                    'url': batch.absolute_url(),
                    'title': to_utf8(batch.Title()),
                    'date': batch.getBatchDate(),
                    'client_batchid': to_utf8(batch.getClientBatchID()),
                    'remarks': to_utf8(batch.getRemarks())}

            uids = batch.Schema()['BatchLabels'].getAccessor(batch)()
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

    def _sample_matrix(self, ar=None):
        samplematrix = ar.getSampleMatrix() if ar else None
        data = {}
        if samplematrix:
            data = {'obj': samplematrix,
                    'id': samplematrix.id,
                    'title': samplematrix.Title(),
                    'url': samplematrix.absolute_url()}
        return data

    def _analyses_data(self, ar, analysis_states=['verified', 'published']):
        analyses = []
        dm = ar.aq_parent.getDecimalMark()
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        for an in ar.getAnalyses(full_objects=True,
                                 review_state=analysis_states):

            # Build the analysis-specific dict
            andict = self._analysis_data(an, dm)

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

    def _analysis_data(self, analysis, decimalmark=None):
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
                  'formatted_uncertainty': '',
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
        andict['formatted_result'] = analysis.getFormattedResult(specs, decimalmark)

        fs = ''
        if specs.get('min', None) and specs.get('max', None):
            fs = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            fs = '> %s' % specs['min']
        elif specs.get('max', None):
            fs = '< %s' % specs['max']
        andict['formatted_specs'] = formatDecimalMark(fs, decimalmark)
        andict['formatted_uncertainty'] = formatDecimalMark(str(analysis.getUncertainty()), decimalmark)

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

    def _managers_data(self, ar):
        managers = {'ids': [], 'dict': {}}
        departments = {}
        ar_mngrs = ar.getResponsible()
        for id in ar_mngrs['ids']:
            new_depts = ar_mngrs['dict'][id]['departments'].split(',')
            if id in managers['ids']:
                for dept in new_depts:
                    if dept not in departments[id]:
                        departments[id].append(dept)
            else:
                departments[id] = new_depts
                managers['ids'].append(id)
                managers['dict'][id] = ar_mngrs['dict'][id]

        mngrs = departments.keys()
        for mngr in mngrs:
            final_depts = ''
            for dept in departments[mngr]:
                if final_depts:
                    final_depts += ', '
                final_depts += dept
            managers['dict'][mngr]['departments'] = final_depts

        return managers

    def publishFromPOST(self):
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        uid = self.request.form.get('uid')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html);
        return self.publishFromHTML(uid, safe_unicode(reporthtml).encode('utf-8'));

    def publishFromHTML(self, aruid, results_html):
        # The AR can be published only and only if allowed
        uc = getToolByName(self.context, 'uid_catalog')
        ars = uc(UID=aruid)
        if not ars or len(ars) != 1:
            return []

        ar = ars[0].getObject();
        wf = getToolByName(ar, 'portal_workflow')
        allowed_states = ['verified', 'published']
        # Publish/Republish allowed?
        if wf.getInfoFor(ar, 'review_state') not in allowed_states:
            # Pre-publish allowed?
            if not ar.getAnalyses(review_state=allowed_states):
                return []

        # SMTP errors are silently ignored if server is in debug mode
        debug_mode = App.config.getConfiguration().debug_mode
        # PDF and HTML files are written to disk if server is in debug mode
        out_path = join(Globals.INSTANCE_HOME, 'var') if debug_mode \
            else None
        out_fn = to_utf8(ar.Title())

        if out_path:
            open(join(out_path, out_fn + ".html"), "w").write(results_html)

        # Create the pdf report (will always be attached to the AR)
        pdf_outfile = join(out_path, out_fn + ".pdf") if out_path else None
        pdf_report = createPdf(results_html, pdf_outfile)

        recipients = []
        contact = ar.getContact()
        lab = ar.bika_setup.laboratory
        if pdf_report:
            if contact:
                recipients = [{
                    'UID': contact.UID(),
                    'Username': to_utf8(contact.getUsername()),
                    'Fullname': to_utf8(contact.getFullname()),
                    'EmailAddress': to_utf8(contact.getEmailAddress()),
                    'PublicationModes': contact.getPublicationPreference()
                }]
            reportid = ar.generateUniqueId('ARReport')
            report = _createObjectByType("ARReport", ar, reportid)
            report.edit(
                AnalysisRequest=ar.UID(),
                Pdf=pdf_report,
                Html=results_html,
                Recipients=recipients
            )
            report.unmarkCreationFlag()
            renameAfterCreation(report)

            # Set status to prepublished/published/republished
            status = wf.getInfoFor(ar, 'review_state')
            transitions = {'verified': 'publish',
                           'published' : 'republish'}
            transition = transitions.get(status, 'prepublish')
            try:
                wf.doActionFor(ar, transition)
            except WorkflowException:
                pass

            # compose and send email.
            # The managers of the departments for which the current AR has
            # at least one AS must receive always the pdf report by email.
            # https://github.com/bikalabs/Bika-LIMS/issues/1028
            mime_msg = MIMEMultipart('related')
            mime_msg['Subject'] = self.get_mail_subject(ar)[0]
            mime_msg['From'] = formataddr(
                (encode_header(lab.getName()), lab.getEmailAddress()))
            mime_msg.preamble = 'This is a multi-part MIME message.'
            msg_txt = MIMEText(results_html, _subtype='html')
            mime_msg.attach(msg_txt)

            to = []
            mngrs = ar.getResponsible()
            for mngrid in mngrs['ids']:
                name = mngrs['dict'][mngrid].get('name', '')
                email = mngrs['dict'][mngrid].get('email', '')
                if (email != ''):
                    to.append(formataddr((encode_header(name), email)))

            if len(to) > 0:
                # Send the email to the managers
                mime_msg['To'] = ','.join(to)
                attachPdf(mime_msg, pdf_report, out_fn)

                try:
                    host = getToolByName(ar, 'MailHost')
                    host.send(mime_msg.as_string(), immediate=True)
                except SMTPServerDisconnected as msg:
                    pass
                    if not debug_mode:
                        raise SMTPServerDisconnected(msg)
                except SMTPRecipientsRefused as msg:
                    raise WorkflowException(str(msg))

        # Send report to recipients
        recips = self.get_recipients(ar)
        for recip in recips:
            if 'email' not in recip.get('pubpref', []) \
                    or not recip.get('email', ''):
                continue

            title = encode_header(recip.get('title', ''))
            email = recip.get('email')
            formatted = formataddr((title, email))

            # Create the new mime_msg object, cause the previous one
            # has the pdf already attached
            mime_msg = MIMEMultipart('related')
            mime_msg['Subject'] = self.get_mail_subject(ar)[0]
            mime_msg['From'] = formataddr(
            (encode_header(lab.getName()), lab.getEmailAddress()))
            mime_msg.preamble = 'This is a multi-part MIME message.'
            msg_txt = MIMEText(results_html, _subtype='html')
            mime_msg.attach(msg_txt)
            mime_msg['To'] = formatted

            # Attach the pdf to the email if requested
            if pdf_report and 'pdf' in recip.get('pubpref'):
                attachPdf(mime_msg, pdf_report, out_fn)

            # For now, I will simply ignore mail send under test.
            if hasattr(self.portal, 'robotframework'):
                continue

            try:
                host = getToolByName(ar, 'MailHost')
                host.send(mime_msg.as_string(), immediate=True)
            except SMTPServerDisconnected as msg:
                if not debug_mode:
                    raise SMTPServerDisconnected(msg)
            except SMTPRecipientsRefused as msg:
                raise WorkflowException(str(msg))

        ar.setDatePublished(DateTime())

        return [ar]

    def publish(self):
        """ Publish the AR report/s. Generates a results pdf file
            associated to each AR, sends an email with the report to
            the lab manager and sends a notification (usually an email
            with the PDF attached) to the AR's contact and CCs.
            Transitions each published AR to statuses 'published',
            'prepublished' or 'republished'.
            Returns a list with the AR identifiers that have been
            published/prepublished/republished (only those 'verified',
            'published' or at least have one 'verified' result).
        """
        if len(self._ars) > 1:
            published_ars = []
            for ar in self._ars:
                arpub = AnalysisRequestPublishView(ar, self.request, publish=True)
                ar = arpub.publish()
                published_ars.extend(ar)
            published_ars = [par.id for par in published_ars]
            return published_ars

        results_html = safe_unicode(self.template()).encode('utf-8')
        return self.publishFromHTML(results_html)


    def get_recipients(self, ar):
        """ Returns a list with the recipients and all its publication prefs
        """
        recips = []

        # Contact and CC's
        contact = ar.getContact()
        if contact:
            recips.append({'title': to_utf8(contact.Title()),
                           'email': contact.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})
        for cc in ar.getCCContact():
            recips.append({'title': to_utf8(cc.Title()),
                           'email': cc.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})

        return recips

    def get_mail_subject(self, ar):
        """ Returns the email subject in accordance with the client
            preferences
        """
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        ai = co = cr = cs = False
        if 'ar' in subject_items:
            ai = True
        if 'co' in subject_items:
            co = True
        if 'cr' in subject_items:
            cr = True
        if 'cs' in subject_items:
            cs = True
        ais = []
        cos = []
        crs = []
        css = []
        blanks_found = False
        if ai:
            ais.append(ar.getRequestID())
        if co:
            if ar.getClientOrderNumber():
                if not ar.getClientOrderNumber() in cos:
                    cos.append(ar.getClientOrderNumber())
            else:
                blanks_found = True
        if cr or cs:
            sample = ar.getSample()
        if cr:
            if sample.getClientReference():
                if not sample.getClientReference() in crs:
                    crs.append(sample.getClientReference())
            else:
                blanks_found = True
        if cs:
            if sample.getClientSampleID():
                if not sample.getClientSampleID() in css:
                    css.append(sample.getClientSampleID())
            else:
                blanks_found = True
        line_items = []
        if ais:
            ais.sort()
            li = t(_('ARs: ${ars}', mapping={'ars': ', '.join(ais)}))
            line_items.append(li)
        if cos:
            cos.sort()
            li = t(_('Orders: ${orders}', mapping={'orders': ', '.join(cos)}))
            line_items.append(li)
        if crs:
            crs.sort()
            li = t(_('Refs: ${references}', mapping={'references':', '.join(crs)}))
            line_items.append(li)
        if css:
            css.sort()
            li = t(_('Samples: ${samples}', mapping={'samples': ', '.join(css)}))
            line_items.append(li)
        tot_line = ' '.join(line_items)
        if tot_line:
            subject = t(_('Analysis results for ${subject_parts}',
                          mapping={'subject_parts':tot_line}))
            if blanks_found:
                subject += (' ' + t(_('and others')))
        else:
            subject = t(_('Analysis results'))
        return subject, tot_line
