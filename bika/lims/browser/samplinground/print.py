from bika.lims import bikaMessageFactory as _, t
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import os

class PrintForm(BrowserView):
    template = ViewPageTemplateFile("templates/print_form.pt")
    _DEFAULT_TEMPLATE = 'default_form.pt'
    _TEMPLATES_DIR = 'templates'

    def __call__(self):
        return self.template()

    def getSamplingRoundObj(self):
        """Returns the sampling round object
        """
        return self.context

    def getFormTemplate(self):
        """Returns the html template for the current sampling round
        """
        # Using default for now
        return ViewPageTemplateFile("templates/default_form.pt")(self)

    def getCSS(self):
        """ Returns the css style to be used for the current template.
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        path = '%s/%s.css' % (templates_dir, 'default')
        content_file = open(path, 'r')
        return content_file.read()

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
                'sample_id': 'Sample ID',
                'sample_type': 'Sample Type',
                'sampling_point': 'Sampling Point',
                'sampling_date': 'Sampling Date',
                'partition': 'Partition',
                'container': 'Container',
                'analyses': 'Analysis',
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
                    if part.getContainer() else ''
                partans = part.getAnalyses()
                numpartans = len(partans)
                for analysis in partans:
                    service = analysis.getService()
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
                            'value': ar.getSamplePoint().title,
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

    def getLab(self):
        return self.context.bika_setup.laboratory.getLabURL()

    def getLogo(self):
        portal = self.context.portal_url.getPortalObject()
        return "%s/logo_print.png" % portal.absolute_url()
