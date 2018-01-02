# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
import datetime
from calendar import monthrange
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
    _filter_date_from = ''
    _filter_date_to = ''
    _avoid_filter_by_date = False

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
        self._filter_date_from = self.request.form.get('date_from', '')
        self._filter_date_to = self.request.form.get('date_to', '')
        self._avoid_filter_by_date = True if self.request.form.get(
            'avoid_filter_by_date', False) == 'true' else False
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

    def _get_contacts_for_sample(self, sample, contacts_list):
        """
        This function returns the contacts defined in each analysis request.
        :sample: a sample object
        :old_list: A list with the contact names
        Returns a sorted list with the complete names.
        """
        ars = sample.getAnalysisRequests()
        for ar in ars:
            contact = ar.getContactFullName()
            if contact not in contacts_list:
                contacts_list.append(contact)
        contacts_list.sort()
        return contacts_list

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
        if not(self._avoid_filter_by_date):
            self._filter_date_from = \
                self.ulocalized_time(self._filter_date_from) if\
                self._filter_date_from else self.default_from_date()
            self._filter_date_to =\
                self.ulocalized_time(self._filter_date_to) if\
                self._filter_date_to else self.default_to_date()
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
            sd = sample.getSamplingDate()
            date = self.ulocalized_time(sd, long_format=0) if sd else ''
            # Getting the sampler filter result
            in_sampler_filter = self._filter_sampler == '' or\
                sampler_uid == self._filter_sampler
            # Getting the client filter result
            in_client_filter = self._filter_client == '' or\
                client_uid == self._filter_client
            # Getting the date filter result
            in_date_filter = self._avoid_filter_by_date or\
                (date >= self.ulocalized_time(self._filter_date_from) and
                    date <= self.ulocalized_time(self._filter_date_to))
            # Apply filter
            if in_sampler_filter and in_client_filter and in_date_filter:
                # Filling the dictionary
                if sampler_uid in result.keys():
                    client_d = result[sampler_uid].get(client_uid, {})
                    if not client_d.keys():
                        client_d['info'] = {
                            'name': sample.getClientTitle(),
                            'reference': sample.getClientReference(),
                            # Contacts contains the client contacts selected in
                            # each ar to the same client
                            'contacts':
                                self._get_contacts_for_sample(sample, [])
                                }
                    else:
                        # Only update the contacts list
                        contacts = self._get_contacts_for_sample(
                            sample, client_d['info'].get('contacts', []))
                        client_d['info']['contacts'] = contacts
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
                    result[sampler_uid][client_uid] = client_d
                else:
                    # This sampler isn't in the dict yet.
                    # Write the client dict
                    client_dict = {
                        'info': {
                            'name': sample.getClientTitle(),
                            'reference': sample.getClientReference(),
                            # Contacts contains the client contacts selected in
                            # each ar to the same client
                            'contacts':
                                self._get_contacts_for_sample(sample, [])
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
        The table contains only the info for one sample/ar.
        """
        # rows will contain the data for each html row
        rows = []
        # columns will be used to sort and define the columns. Each header row
        # is a list itself.
        columns = {
            'column_order': [
                [
                    'sample_id',
                    'sample_type',
                    'sampling_point',
                    'sampling_date',
                    'partition',
                    'container',
                    'analyses'],
                [
                    'temp',
                    'amb_cond',
                    'client_ref',
                    'client_sample_id',
                    'composite',
                    'adhoc',
                    'sample_cond']
                ],
            'titles': {
                'sample_id': _('Sample ID'),
                'sample_type': _('Sample Type'),
                'sampling_point': _('Sampling Point'),
                'sampling_date': _('Exp. Sampling Date'),
                'partition': _('Partition'),
                'container': _('Container'),
                'analyses': _('Analysis'),
                'temp': _('Temperature'),
                'amb_cond': _('Ambiental Conditions'),
                'client_ref': _('Client Reference'),
                'client_sample_id': _('Client Sample ID'),
                'composite': _('Composite'),
                'adhoc': _('Ad-Hoc'),
                'sample_cond': _('Sample Conditions'),
            }
        }
        ars = sample.getAnalysisRequests()
        labans = False
        # The form is divided by ar(samples).
        for ar in ars:
            # Since the form is divided by ar, we need a marker to know if
            # we are still inside the same ar or it is a new one. The fields
            # related with the ar itself shouldn't be repeated each loop.
            # arcell == analysis request cell
            arcell = False
            # Getting the analyses for each analysis request (sample). This
            # number will be used in order to set the height of the ar html row
            numans = len(ar.getAnalyses())
            # We want a row per patition in order to draw the barcodes
            for part in ar.getPartitions():
                # The same logic used for 'arcell':True qhen the row still
                # belongs to the same partition
                # partcell == partition cell
                partcell = False
                container = part.getContainer().title \
                    if part and part.getContainer() else ''
                # Gettin the analyses linked to the partition
                partans = part.getAnalyses()
                # Getting the number of partitions. Needed to know the height
                # of the partition row.
                numpartans = len(partans)
                # Getting the points of capture if needed
                labpoc = [an for an in partans if an.getPointOfCapture() == 'field']
                labans = True if labans or len(labpoc) > 0 else labans
                labpoc = [partans[0]] if len(labpoc) == 0 else labpoc
                # for each analyses, build the structure
                for analysis in labpoc:
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
                            'value':  self.ulocalized_time(ar.getSamplingDate()),
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
                            'title': analysis.Title(),
                            'units': analysis.getUnit(),
                        },
                        'temp': {
                            'hidden': True if arcell else False,
                            'value': '',
                        },
                        'amb_cond': {
                            'hidden': True if arcell else False,
                            'value': '',
                        },
                        'client_ref': {
                            'hidden': True if arcell else False,
                            'value': sample.getClientReference() if
                                sample.getClientReference() else '',
                        },
                        'client_sample_id': {
                            'hidden': True if arcell else False,
                            'value': sample.getClientSampleID() if
                                sample.getClientSampleID() else '',
                        },
                        'composite': {
                            'hidden': True if arcell else False,
                            'value': 'Yes' if ar.getComposite() else 'No',
                        },
                        'adhoc': {
                            'hidden': True if arcell else False,
                            'value': 'Yes' if ar.getAdHoc() else 'No',
                            'rowspan': numans,
                        },
                        'sample_cond': {
                            'hidden': True if arcell else False,
                            'value': '',
                        },
                    }
                    rows.append(row)
                    # After the first iteration, we definitely are in a
                    # analysis request and partition row
                    arcell = True
                    partcell = True

        # table will contain the data from where the html
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

    def default_from_date(self):
        """
        Return the default min date in order to filter the samples.
        Default will return a datetime.date object: <current_date> - 10d
        """
        default = 10
        today = datetime.date.today()
        day = today.day
        month = today.month
        year = today.year
        # Checking if the day is correct after been computed
        if (day - default) <= 0:
            # substract a month
            if (month-1) < 0:
                year -= 1
                month = 12
            else:
                month -= 1
            month_max = monthrange(year=year, month=month)[1]
            day = month_max + day - default
        else:
            day -= default
        return DateTime(year, month, day)

    def default_to_date(self):
        """
        Return the default max date in order to filter the samples.
        Default will return a datetime object: <current_date> + 10d
        """
        default = 10
        today = datetime.date.today()
        day = today.day
        month = today.month
        year = today.year
        # Checking if the day is correct after been computed
        month_max = monthrange(year=year, month=month)[1]
        if (day + default) > month_max:
            # increase a month
            if (month+1) > 12:
                year += 1
                month = 1
            else:
                month += 1
                day = day + default - month_max
        else:
            day += default
        return DateTime(year, month, day)

    def getLab(self):
        return self.context.bika_setup.laboratory.getLabURL()

    def getLogo(self):
        portal = self.context.portal_url.getPortalObject()
        return "%s/logo_print.png" % portal.absolute_url()
