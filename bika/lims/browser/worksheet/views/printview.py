# coding=utf-8
from DateTime import DateTime
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters

from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import to_utf8, createPdf, formatDecimalMark, format_supsub
from bika.lims.utils.analysis import format_uncertainty

import glob, os, sys, traceback
import App
import Globals


class PrintView(BrowserView):
    """ Print view for a worksheet. This view acts as a placeholder, so
        the user can select the preferred options (AR by columns, AR by
        rows, etc.) for printing. Both a print button and pdf button
        are shown.
    """

    template = ViewPageTemplateFile("../templates/print.pt")
    _DEFAULT_TEMPLATE = 'ar_by_column.pt'
    _DEFAULT_NUMCOLS = 4
    _TEMPLATES_DIR = '../templates/print'
    # Add-on folder to look for templates
    _TEMPLATES_ADDON_DIR = 'worksheets'
    _current_ws_index = 0
    _worksheets = []


    def __init__(self, context, request):
        super(PrintView, self).__init__(context, request)
        self._worksheets = [self.context]


    def __call__(self):
        """ Entry point of PrintView.
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
            logger.warning('PrintView: type not allowed: %s' %
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


    def getCSS(self):
        """ Returns the css style to be used for the current template.
            If the selected template is 'default.pt', this method will
            return the content from 'default.css'. If no css file found
            for the current template, returns empty string
        """
        template = self.request.get('template', self._DEFAULT_TEMPLATE)
        content = ''
        if template.find(':') >= 0:
            prefix, template = template.split(':')
            resource = queryResourceDirectory(self._TEMPLATES_ADDON_DIR, prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
            path = '%s/%s.css' % (templates_dir, template[:-3])
            with open(path, 'r') as content_file:
                content = content_file.read()
        return content


    def getNumColumns(self):
        """ Returns the number of columns to display
        """
        return int(self.request.get('numcols', self._DEFAULT_NUMCOLS))


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


    def splitList(self, elements, chunksnum):
        """ Splits a list to a n lists with chunksnum number of elements
            each one.
            For a list [3,4,5,6,7,8,9] with chunksunum 4, the method
            will return the following list of groups:
            [[3,4,5,6],[7,8,9]]
        """
        if len(elements) < chunksnum:
            return [elements];
        groups=zip(*[elements[i::chunksnum] for i in range(chunksnum)])
        if len(groups)*chunksnum < len(elements):
            groups.extend([elements[-(len(elements)-len(groups)*chunksnum):]])
        return groups


    def _lab_data(self):
        """ Returns a dictionary that represents the lab object
            Keys: obj, title, url, address, confidence, accredited,
                  accreditation_body, accreditation_logo, logo
        """
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
                'logo': "%s/logo_print.png" % portal.absolute_url()}


    def _ws_data(self, ws):
        """ Creates an ws dict, accessible from the view and from each
            specific template.
            Keys: obj, id, url, template_title, remarks, date_printed,
                ars, createdby, analyst, printedby, analyses_titles,
                portal, laboratory
        """
        data = {'obj': ws,
                'id': ws.id,
                'url': ws.absolute_url(),
                'template_title': ws.getWorksheetTemplateTitle(),
                'remarks': ws.getRemarks(),
                'date_printed': self.ulocalized_time(DateTime(), long_format=1),
                'date_created': self.ulocalized_time(ws.created(), long_format=1)}

        # Sub-objects
        data['ars'] = self._analyses_data(ws)
        data['createdby'] = self._createdby_data(ws)
        data['analyst'] = self._analyst_data(ws)
        data['printedby'] = self._printedby_data(ws)
        ans = []
        for ar in data['ars']:
            ans.extend([an['title'] for an in ar['analyses']])
        data['analyses_titles'] = list(set(ans))

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()
        return data


    def _createdby_data(self, ws):
        """ Returns a dict that represents the user who created the ws
            Keys: username, fullmame, email
        """
        username = ws.getOwner().getUserName()
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}

    def _analyst_data(self, ws):
        """ Returns a dict that represent the analyst assigned to the
            worksheet.
            Keys: username, fullname, email
        """
        username = ws.getAnalyst();
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}


    def _printedby_data(self, ws):
        """ Returns a dict that represents the user who prints the ws
            Keys: username, fullname, email
        """
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
        """ Returns a list of dicts. Each dict represents an analysis
            assigned to the worksheet
        """
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
            if an.portal_type == "DuplicateAnalysis":
                andict = self._analysis_data(an.getAnalysis())
                andict['id'] = an.getReferenceAnalysesGroupID();
                andict['obj'] = an;
                andict['type'] = "DuplicateAnalysis"
                andict['reftype'] = 'd'
            else:
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
            andict['tmp_position'] = (pos * 100) + pos_count
            andict['position'] = pos
            pos_count += 1

            # Look for the analysis request, client and sample info and
            # group the analyses per Analysis Request
            reqid = andict['request_id']
            if an.portal_type in ("ReferenceAnalysis", "DuplicateAnalysis"):
                reqid = an.getReferenceAnalysesGroupID()

            if reqid not in ars:
                arobj = an.aq_parent
                if an.portal_type == "DuplicateAnalysis":
                    arobj = an.getAnalysis().aq_parent

                ar = self._ar_data(arobj)
                ar['client'] = self._client_data(arobj.aq_parent)
                ar['sample'] = self._sample_data(an.getSample())
                ar['analyses'] = []
                ar['tmp_position'] = andict['tmp_position']
                ar['position'] = andict['position']
                if an.portal_type in ("ReferenceAnalysis", "DuplicateAnalysis"):
                    ar['id'] = an.getReferenceAnalysesGroupID()
                    ar['url'] = an.absolute_url()

            else:
                ar = ars[reqid]
                if (andict['tmp_position'] < ar['tmp_position']):
                    ar['tmp_position'] = andict['tmp_position'];
                    ar['position'] = andict['position']

            # Sort analyses by position
            ans = ar['analyses']
            ans.append(andict)
            ans.sort(lambda x, y: cmp(x.get('tmp_position'), y.get('tmp_position')))
            ar['analyses'] = ans
            ars[reqid] = ar

        ars = [ar for ar in ars.itervalues()]

        # Sort analysis requests by position
        ars.sort(lambda x, y: cmp(x.get('tmp_position'), y.get('tmp_position')))
        return ars

    def _analysis_data(self, analysis):
        """ Returns a dict that represents the analysis
        """
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

        else:
            # Get the specs directly from the analysis. The getResultsRange
            # function already takes care about which are the specs to be used:
            # AR, client or lab.
            specs = analysis.getResultsRange()

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
        """ Returns a dict that represents the sample
            Keys: obj, id, url, client_sampleid, date_sampled,
                  sampling_date, sampler, date_received, composite,
                  date_expired, date_disposal, date_disposed, adhoc,
                  remarks
        """
        data = {}
        if sample:
            data = {'obj': sample,
                    'id': sample.id,
                    'url': sample.absolute_url(),
                    'date_sampled': self.ulocalized_time(sample.getDateSampled(), long_format=0),
                    'date_received': self.ulocalized_time(sample.getDateReceived(), long_format=0),
                    }

            if sample.portal_type == "ReferenceSample":
                data['sample_type'] = None;
                data['sample_point'] = None;
            else:
                data['sample_type'] = self._sample_type(sample)
                data['sample_point'] = self._sample_point(sample)
        return data

    def _sample_type(self, sample=None):
        """ Returns a dict that represents the sample type assigned to
            the sample specified
            Keys: obj, id, title, url
        """
        data = {}
        sampletype = sample.getSampleType() if sample else None
        if sampletype:
            data = {'obj': sampletype,
                    'id': sampletype.id,
                    'title': sampletype.Title(),
                    'url': sampletype.absolute_url()}
        return data

    def _sample_point(self, sample=None):
        """ Returns a dict that represents the sample point assigned to
            the sample specified
            Keys: obj, id, title, url
        """
        samplepoint = sample.getSamplePoint() if sample else None
        data = {}
        if samplepoint:
            data = {'obj': samplepoint,
                    'id': samplepoint.id,
                    'title': samplepoint.Title(),
                    'url': samplepoint.absolute_url()}
        return data

    def _ar_data(self, ar):
        """ Returns a dict that represents the analysis request
        """
        if not ar:
            return {}

        if ar.portal_type == "AnalysisRequest":
            return {'obj': ar,
                    'id': ar.getRequestID(),
                    'date_received': self.ulocalized_time(ar.getDateReceived(), long_format=0),
                    'date_sampled': self.ulocalized_time(ar.getDateSampled(), long_format=0),
                    'url': ar.absolute_url(),}
        elif ar.portal_type == "ReferenceSample":
            return {'obj': ar,
                    'id': ar.id,
                    'date_received': self.ulocalized_time(ar.getDateReceived(), long_format=0),
                    'date_sampled': self.ulocalized_time(ar.getDateSampled(), long_format=0),
                    'url': ar.absolute_url(),}
        else:
            return {'obj': ar,
                    'id': ar.id,
                    'date_received': "",
                    'date_sampled': "",
                    'url': ar.absolute_url(),}


    def _client_data(self, client):
        """ Returns a dict that represents the client specified
            Keys: obj, id, url, name
        """
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
