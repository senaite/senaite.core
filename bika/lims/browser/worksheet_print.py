# coding=utf-8
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import to_utf8, createPdf
from bika.lims.utils import formatDecimalMark, format_supsub
from bika.lims.utils.analysis import format_uncertainty
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from zope.component import getAdapters
import glob, os, sys, traceback
import App
import Globals

class WorksheetPrintView(BrowserView):
    """ Print view for a worksheet. This view acts as a placeholder, so
        the user can select the preferred options (AR by columns, AR by
        rows, etc.) for printing. Both a print button and pdf button
        are shown.
    """

    template = ViewPageTemplateFile("worksheet/templates/worksheet_print.pt")
    _DEFAULT_TEMPLATE = 'ar_by_column.pt'
    _TEMPLATES_DIR = 'worksheet/templates/print'
    # Add-on folder to look for templates
    _TEMPLATES_ADDON_DIR = 'worksheets'
    _current_ws_index = 0
    _worksheets = []

    def __init__(self, context, request):
        super(WorksheetPrintView, self).__init__(context, request)
        self._worksheets = [self.context]


    def __call__(self):
        """ Entry point of WorksheetPrintView.
            If context.portal_type is a Worksheet, then the PrintView
            is initialized to manage only that worksheet. If the
            context.portal_type is a WorksheetFolder and there are
            items selected in the request (items param), the PrintView
            will show the preview for all the selected Worksheets.
            By default, returns a HTML-encoded template, but if the
            request contains a param 'pdf' with value 1, will flush a
            pdf for the worksheet.
        """

        if self.context.portal_type == 'Worksheet':
            self._worksheets = [self.context]

        elif self.context.portal_type == 'WorksheetFolder' \
            and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._worksheets = [obj.getObject() for obj in uc(UID=uids)]

        else:
            # Warn and redirect to referer
            logger.warning('WorksheetPrintView: type not allowed: %s' %
                            self.context.portal_type)
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Generate PDF?
        if self.request.form.get('pdf', '0') == '1':
            return self._flush_pdf()
        else:
            return self.template()

    def getWSTemplates(self):
        """ Returns a DisplayList with the available templates found in
            templates/worksheets
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        for templates_resource in iterDirectoriesOfType(self._TEMPLATES_ADDON_DIR):
            prefix = templates_resource.__name__
            templates = [tpl for tpl in templates_resource.listDirectory() if tpl.endswith('.pt')]
            for template in templates:
                out.append({
                    'id': '{0}:{1}'.format(prefix, template),
                    'title': '{0} ({1})'.format(template[:-3], prefix),
                })
        return out


    def renderWSTemplate(self):
        """ Returns the current worksheet rendered with the template
            specified in the request (param 'template').
            Moves the iterator to the next worksheet available.
        """
        templates_dir = self._TEMPLATES_DIR
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, embedt = embedt.split(':')
            templates_dir = queryResourceDirectory(self._TEMPLATES_ADDON_DIR, prefix).directory
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            wsid = self._worksheets[self._current_ws_index].id
            reptemplate = "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>" % (wsid, _("Unable to load the template"), embedt, tbex)
        if self._current_ws_index < len(self._worksheets):
            self._current_ws_index += 1
        return reptemplate


    def getWorksheets(self):
        """ Returns the list of worksheets to be printed
        """
        return self._worksheets;


    def getWorksheet(self):
        """ Returns the current worksheet from the list. Returns None when
            the iterator reaches the end of the array.
        """
        ws = None
        if self._current_ws_index < len(self._worksheets):
            ws = self._ws_data(self._worksheets[self._current_ws_index])
        return ws


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


    def _ws_data(self, ws):
        """ Creates an ws dict, accessible from the view and from each
            specific template.
        """
        data = {'obj': ws,
                'id': ws.id,
                'url': ws.absolute_url(),
                'template_title': ws.getWorksheetTemplateTitle(),
                'remarks': ws.getRemarks(),
                'date_printed': self.ulocalized_time(DateTime(), long_format=1),
                'date_created': self.ulocalized_time(ws.created(), long_format=1)}

        # Sub-objects
        # Analyses
        # Instrument

        data['analyses'] = self._analyses_data(ws)
        data['createdby'] = self._createdby_data(ws)
        data['analyst'] = self._analyst_data(ws)
        data['printedby'] = self._printedby_data(ws)

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()
        return data


    def _createdby_data(self, ws):
        username = ws.getOwner().getUserName()
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}

    def _analyst_data(self, ws):
        username = ws.getAnalyst();
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}


    def _printedby_data(self, ws):
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

    def _analyses_data(self, ws):
        analyses = []
        ans = ws.getAnalyses()
        layout = ws.getLayout()
        an_count = len(ans)
        pos_count = 0
        prev_pos = 0
        requestids = []
        ars = {}
        samples = {}
        clients = {}
        for an in ans:
            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Analysis position
            pos = [slot['position'] for slot in layout \
                if slot['analysis_uid'] == an.UID()][0]
            # compensate for possible bad data (dbw#104)
            if type(pos) in (list, tuple) and pos[0] == 'new':
                pos = prev_pos
            pos = int(pos)
            prev_pos = pos

            # This will allow to sort automatically all the analyses,
            # also if they have the same initial position.
            andict['position'] = (pos * 100) + pos_count
            analyses.append(andict)
            pos_count += 1

            # Add the analysis request, client and sample info
            if andict['request_id'] not in requestids:
                sample = an.getSample()
                samples[andict['request_id']] = self._sample_data(sample)

                ar = an.aq_parent
                ars[andict['request_id']] = self._ar_data(ar)

                client = an.aq_parent.aq_parent
                clients[andict['request_id']] = self._client_data(client)

            andict['sample'] = samples[andict['request_id']]
            andict['analysisrequest'] = ars[andict['request_id']]
            andict['client'] = clients[andict['request_id']]

        # Sort analyses by position
        analyses.sort(lambda x, y: cmp(x.get('position'), y.get('position')))
        return analyses

    def _analysis_data(self, analysis):
        decimalmark = analysis.aq_parent.aq_parent.getDecimalMark()
        keyword = analysis.getKeyword()
        service = analysis.getService()
        andict = {'obj': analysis,
                  'id': analysis.id,
                  'title': analysis.Title(),
                  'keyword': keyword,
                  'scientific_name': service.getScientificName(),
                  'accredited': service.getAccredited(),
                  'point_of_capture': to_utf8(POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())),
                  'category': to_utf8(service.getCategoryTitle()),
                  'result': analysis.getResult(),
                  'unit': to_utf8(service.getUnit()),
                  'formatted_unit': format_supsub(to_utf8(service.getUnit())),
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
        scinot = self.context.bika_setup.getScientificNotationReport()
        andict['formatted_result'] = analysis.getFormattedResult(specs=specs, sciformat=int(scinot), decimalmark=decimalmark)

        fs = ''
        if specs.get('min', None) and specs.get('max', None):
            fs = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            fs = '> %s' % specs['min']
        elif specs.get('max', None):
            fs = '< %s' % specs['max']
        andict['formatted_specs'] = formatDecimalMark(fs, decimalmark)
        andict['formatted_uncertainty'] = format_uncertainty(analysis, analysis.getResult(), decimalmark=decimalmark, sciformat=int(scinot))

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

    def _sample_data(self, sample):
        data = {}
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

    def _ar_data(self, ar):
        if not ar:
            return {}

        return {'obj': ar,
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
                'date_published': self.ulocalized_time(DateTime(), long_format=1),
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
                'parent_analysisrequest': None,
                'resultsinterpretation':ar.getResultsInterpretation()}

    def _client_data(self, client):
        data = {}
        if client:
            data['obj'] = client
            data['id'] = client.id
            data['url'] = client.absolute_url()
            data['name'] = to_utf8(client.getName())
        return data


    def _flush_pdf():
        """ Generates a PDF using the current layout as the template and
            returns the chunk of bytes.
        """
        return ""
