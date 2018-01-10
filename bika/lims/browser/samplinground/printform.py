# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _, t
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.utils import to_utf8, createPdf
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
import App
import tempfile
import os
import glob
import traceback


class PrintForm(BrowserView):
    template = ViewPageTemplateFile("templates/print_form.pt")
    _DEFAULT_TEMPLATE = 'default_form.pt'
    _TEMPLATES_DIR = 'templates/print'
    _TEMPLATES_ADDON_DIR = 'samplingrounds'
    _current_sr_index = 0
    _samplingrounds = []

    def __call__(self):
        if self.context.portal_type == 'SamplingRound':
            self._samplingrounds = [self.context]

        elif self.context.portal_type == 'SamplingRounds' \
                and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._samplingrounds = [obj.getObject() for obj in uc(UID=uids)]

        else:
            # Warn and redirect to referer
            logger.warning('PrintView: type not allowed: %s' %
                            self.context.portal_type)
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Do print?
        if self.request.form.get('pdf', '0') == '1':
            response = self.request.response
            response.setHeader("Content-type", "application/pdf")
            response.setHeader("Content-Disposition", "inline")
            response.setHeader("filename", "temp.pdf")
            return self.pdfFromPOST()
        else:
            return self.template()

    def getSamplingRoundObj(self):
        """Returns the sampling round object
        """
        return self.context

    def getSRTemplates(self):
        """
        Returns a DisplayList with the available templates found in
        browser/samplinground/templates/
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
        """Returns the current samplinground rendered with the template
            specified in the request (param 'template').
            Moves the iterator to the next samplinground available.
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
            wsid = self._samplingrounds[self._current_sr_index].id
            reptemplate = "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>" % (wsid, _("Unable to load the template"), embedt, tbex)
        if self._current_sr_index < len(self._samplingrounds):
            self._current_sr_index += 1
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

    def getAnalysisRequestTemplatesInfo(self):
        """
        Returns a lost of dicts with the analysis request templates infomration
        [{'uid':'xxxx','id':'xxxx','title':'xxx','url':'xxx'}, ...]
        """
        arts_list = []
        for art in self.context.ar_templates:
            pc = getToolByName(self.context, 'portal_catalog')
            contentFilter = {'portal_type': 'ARTemplate',
                             'UID': art}
            art_brain = pc(contentFilter)
            if len(art_brain) == 1:
                art_obj = art_brain[0].getObject()
                arts_list.append({
                    'uid': art_obj.UID(),
                    'id': art_obj.id,
                    'title': art_obj.title,
                    'url': art_obj.absolute_url(),
                })
        return arts_list

    def getAnalysisRequestBySample(self):
        """
        Returns a list of dictionaries sorted by Sample Partition/Container
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
        ars = self.context.getAnalysisRequests()
        for ar in ars:
            ar = ar.getObject()
            arcell = False
            numans = len(ar.getAnalyses())
            for part in ar.getPartitions():
                partcell = False
                container = part.getContainer().title \
                    if part and part.getContainer() else ''
                partans = part.getAnalyses()
                numpartans = len(partans)
                for analysis in partans:
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
                            'value': ar.getSamplePoint().title if ar.getSamplePoint() else '',
                            },
                        'sampling_date': {
                            'hidden': True if arcell else False,
                            'rowspan': numans,
                            'value': self.context.sampling_date,
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

    def getLab(self):
        return self.context.bika_setup.laboratory.getLabURL()

    def getLogo(self):
        portal = self.context.portal_url.getPortalObject()
        return "%s/logo_print.png" % portal.absolute_url()

    def pdfFromPOST(self):
        """
        It returns the pdf for the sampling rounds printed
        """
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html)
        return self.printFromHTML(safe_unicode(reporthtml).encode('utf-8'))

    def printFromHTML(self, sr_html):
        """
        Tis function generates a pdf file from the html
        :sr_html: the html to use to generate the pdf
        """
        # HTML written to debug file
        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".html")
            open(tmp_fn, "wb").write(sr_html)

        # Creates the pdf
        # we must supply the file ourself so that createPdf leaves it alone.
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_report = createPdf(htmlreport=sr_html, outfile=pdf_fn)
        return pdf_report
