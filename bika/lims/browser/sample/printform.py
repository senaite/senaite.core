from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from plone.resource.utils import iterDirectoriesOfType
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import createPdf
from bika.lims import logger
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import *
import os
import glob
import traceback
import App
import tempfile


class SamplesPrint(BrowserView):
    """
    This class manages all the logic needed to create a form which is going
    to be printed.
    The sampler will be able to print the form and take it to
    the defined sampling points.
    The class receives the samples selected in the SamplesView in order to
    generate the form.
    If no samples are selected, the system will get all the samples with the
    states 'to_be_sampled' or 'scheduled_sampling'.
    The system will gather field analysis services using the following pattern:

    Sampler_1 - Client_1 - Date_1 - SamplingPoint_1 - Field_AS_1.1
                                                    - Field_AS_1.2
                                  - SamplingPoint_2 - Field_AS_2.1
                         - Date_3 - SamplingPoint_1 - Field_AS_3.1
              - Client_2 - Date_1 - SamplingPoint_1 - Field_AS_4.1

    Sampler_2 - Client_1 - Date_1 - SamplingPoint_1 - Field_AS_5.1
    """
    template = ViewPageTemplateFile("templates/print_form.pt")
    _DEFAULT_TEMPLATE = 'default_form.pt'
    _TEMPLATES_DIR = 'templates/print'
    _TEMPLATES_ADDON_DIR = 'samples'
    # selected samples
    _items = []
    _filter_sampler = ''
    _filter_client = ''

    def __call__(self):
        if self.context.portal_type == 'SamplesFolder':
            if self.request.get('items', ''):
                uids = self.request.get('items').split(',')
                uc = getToolByName(self.context, 'uid_catalog')
                self._items = [obj.getObject() for obj in uc(UID=uids)]
            else:
                catalog = getToolByName(self.context, 'portal_catalog')
                contentFilter = {
                    'portal_type': 'Sample',
                    'sort_on': 'created',
                    'sort_order': 'reverse',
                    'review_state': ['to_be_sampled', 'scheduled_sampling'],
                    'path': {'query': "/", 'level': 0}
                    }
                brains = catalog(contentFilter)
                self._items = [obj.getObject() for obj in brains]
        else:
            # Warn and redirect to referer
            logger.warning(
                'PrintView: type not allowed: %s \n' % self.context.portal_type)
            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())
        # setting the filters
        self._filter_sampler = self.request.form.get('sampler', '')
        self._filter_client = self.request.form.get('client', '')

        # Do print?
        if self.request.form.get('pdf', '0') == '1':
            response = self.request.response
            response.setHeader("Content-type", "application/pdf")
            response.setHeader("Content-Disposition", "inline")
            response.setHeader("filename", "temp.pdf")
            return self.pdfFromPOST()
        else:
            return self.template()

    def _rise_error(self):
        """
        Give the error missage
        """
        tbex = traceback.format_exc()
        logger.error(
            'An error occurred while rendering the view: %s' % tbex)
        self.destination_url = self.request.get_header(
            "referer", self.context.absolute_url())

    def getSortedFilteredSamples(self):
        """
        This function returns all the samples sorted and filtered
        This function returns a dictionary as:
        {
            sampler1:{
                info:{,},
                client1:{
                    info:{,},
                    date1:{
                        [sample_tables]
                    },
                    no_date:{
                        [sample_tables]
                    }
                }
            }
        }
        """
        samples = self._items
        result = {}
        for sample in samples:
            pc = getToolByName(self, 'portal_catalog')
            # Getting the filter keys
            sampler_id = sample.getScheduledSamplingSampler()
            sampler_brain = pc(
                portal_type='LabContact', getUsername=sampler_id)
            sampler_obj = sampler_brain[0].getObject()\
                if sampler_brain else None
            if sampler_obj:
                sampler_uid = sampler_obj.UID()
                sampler_name = sampler_obj.getFullname()
            else:
                sampler_uid = 'no_sampler'
                sampler_name = ''
            client_uid = sample.getClientUID()
            # apply sampler filter

            if (self._filter_sampler == '' or
                    sampler_uid == self._filter_sampler) and \
                (self._filter_client == '' or
                    client_uid == self._filter_client):
                date = \
                    self.ulocalized_time(
                        sample.getSamplingDate(), long_format=0)\
                    if sample.getSamplingDate() else ''
                # Filling the dictionary
                if sampler_uid in result.keys():
                    client_d = result[sampler_uid].get(client_uid, {})
                    # Always write the info again.
                    # Is it faster than doing a check every time?
                    client_d['info'] = {'name': sample.getClientTitle()}
                    if date:
                        c_l = client_d.get(date, [])
                        c_l.append(
                            self._sample_table_builder(sample))
                        client_d[date] = c_l
                    else:
                        c_l = client_d.get('no_date', [])
                        c_l.append(
                            self._sample_table_builder(sample))
                        client_d[date] = c_l
                else:
                    # This sampler isn't in the dict yet.
                    # Write the client dict
                    client_dict = {
                        'info': {
                            'name': sample.getClientTitle()
                            },
                        }
                    # If the sample has a sampling date, build the dictionary
                    # which emulates the table inside a list
                    if date:
                        client_dict[date] = [
                            self._sample_table_builder(sample)]
                    else:
                        client_dict['no_date'] = [
                            self._sample_table_builder(sample)]
                    # Adding the client dict inside the sampler dict
                    result[sampler_uid] = {
                        'info': {
                            'obj': sampler_obj,
                            'id': sampler_id,
                            'name': sampler_name
                            },
                        client_uid: client_dict
                        }
        return result

    def _sample_table_builder(self, sample):
        """
        This function returns a list of dictionaries sorted by Sample
        Partition/Container. It emulates the columns/rows of a table.
        [{'requests and partition info'}, ...]
        """
        # rows will contain the data for each html row
        rows = []
        # columns will be used to sort and define the columns
        columns = {
            'column_order': [
                'sample_id',
                'sample_type',
                'sampling_point',
                'sampling_date',
                'partition',
                'container',
                'analyses',
                ],
            'titles': {
                'sample_id': _('Sample ID'),
                'sample_type': _('Sample Type'),
                'sampling_point': _('Sampling Point'),
                'sampling_date': _('Sampling Date'),
                'partition': _('Partition'),
                'container': _('Container'),
                'analyses': _('Analysis'),
            }
        }
        ars = sample.getAnalysisRequests()
        for ar in ars:
            arcell = False
            numans = len(ar.getAnalyses())
            for part in ar.getPartitions():
                partcell = False
                container = part.getContainer().title \
                    if part.getContainer() else ''
                partans = part.getAnalyses()
                numpartans = len(partans)
                for analysis in partans:
                    service = analysis.getService()
                    if service.getPointOfCapture() == 'field':
                        row = {
                            'sample_id': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value': ar.getSample().id,
                                },
                            'sample_type': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value': ar.getSampleType().title,
                                },
                            'sampling_point': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value':
                                    ar.getSamplePoint().title
                                    if ar.getSamplePoint() else '',
                                },
                            'sampling_date': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value':  self.ulocalized_time(sample.getSamplingDate(), long_format=0),
                                },
                            'partition': {
                                'hidden': True if partcell else False,
                                'rowspan': numpartans,
                                'value': part.id,
                                },
                            'container': {
                                'hidden': True if partcell else False,
                                'rowspan': numpartans,
                                'value': container,
                                },
                            'analyses': {
                                'title': service.title,
                                'units': service.getUnit(),
                            },
                        }
                        rows.append(row)
                        arcell = True
                        partcell = True

        # table will contain the data that from where the html
        # will take the info
        table = {
            'columns': columns,
            'rows': rows,
        }
        return table

    def getAvailableTemplates(self):
        """
        Returns a DisplayList with the available templates found in
        browser/templates/samplesprint
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        for templates_resource in iterDirectoriesOfType(
                self._TEMPLATES_ADDON_DIR):
            prefix = templates_resource.__name__
            templates = [
                tpl for tpl in templates_resource.listDirectory()
                if tpl.endswith('.pt')
                ]
            for template in templates:
                out.append({
                    'id': '{0}:{1}'.format(prefix, template),
                    'title': '{0} ({1})'.format(template[:-3], prefix),
                })
        return out

    def getFormTemplate(self):
        """Returns the selected samples rendered using the template
            specified in the request (param 'template').
        """
        templates_dir = self._TEMPLATES_DIR
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, embedt = embedt.split(':')
            templates_dir = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix).directory
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            reptemplate = \
                "<div class='error-print'>%s '%s':<pre>%s</pre></div>" %\
                (_("Unable to load the template"), embedt, tbex)
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
            resource = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix)
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

    def pdfFromPOST(self):
        """
        It returns the pdf with the printed form
        """
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html)
        return self.printFromHTML(safe_unicode(reporthtml).encode('utf-8'))

    def printFromHTML(self, code_html):
        """
        Tis function generates a pdf file from the html
        :code_html: the html to use to generate the pdf
        """
        # HTML written to debug file
        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".html")
            open(tmp_fn, "wb").write(code_html)

        # Creates the pdf
        # we must supply the file ourself so that createPdf leaves it alone.
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_report = createPdf(htmlreport=code_html, outfile=pdf_fn)
        return pdf_report

    def getSamplers(self):
        """
        Returns a dictionary of dictionaries with info about the samplers
        defined in each sample.
        {
            'uid': {'id':'xxx', 'name':'xxx'},
            'uid': {'id':'xxx', 'name':'xxx'}, ...}
        """
        samplers = {}
        pc = getToolByName(self, 'portal_catalog')
        for sample in self._items:
            sampler_id = sample.getScheduledSamplingSampler()
            sampler_brain = pc(
                portal_type='LabContact', getUsername=sampler_id)
            sampler_obj = sampler_brain[0].getObject()\
                if sampler_brain else None
            if sampler_obj and\
                    sampler_obj.UID() not in samplers.keys():
                samplers[sampler_obj.UID()] = {
                    'uid': sampler_obj.UID(),
                    'name': sampler_obj.getFullname(),
                    'obj': sampler_obj
                }
        return samplers

    def getClients(self):
        """
        Returns a dictionary of dictionaries with info about the clients
        related to the selected samples.
        {
            'uid': {'name':'xxx'},
            'uid': {'name':'xxx'}, ...}
        """
        clients = {}
        for sample in self._items:
            if sample.getClientUID() not in clients.keys():
                clients[sample.getClientUID()] = {
                    'name': sample.getClientTitle()
                }
        return clients

    def getLab(self):
        return self.context.bika_setup.laboratory.getLabURL()

    def getLogo(self):
        portal = self.context.portal_url.getPortalObject()
        return "%s/logo_print.png" % portal.absolute_url()
