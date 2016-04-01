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
        # total_analyses will be a list of index used to create the <tr>
        total_analyses = []
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
            # Getting the partitions, containers and analyses
            partitions_ids = []
            containers_type = []
            # analyses will contain the
            analyses = []

            ar = ar.getObject()
            for part in ar.getPartitions():
                partitions_ids.append(part.id)
                container = part.getContainer().title \
                    if part.getContainer() else ''
                containers_type.append(container)
                for analysis in part.getAnalyses():
                    service = analysis.getService()
                    analyses.append({
                        'title': service.title,
                        'units': service.getUnit()
                    })
            row_info = {
                'sample_id': {
                    'rowspan': len(analyses),
                    'colspan': 1,
                    'value': ar.getSample().id,
                    },
                'sample_type': {
                    'rowspan': len(analyses),
                    'colspan': 1,
                    'value': ar.getSampleType(),
                    },
                'sampling_point': {
                    'rowspan': len(analyses),
                    'colspan': 1,
                    'value': ar.getSamplePoint(),
                    },
                'sampling_date': {
                    'rowspan': len(analyses),
                    'colspan': 1,
                    'value': self.context.sampling_date,
                    },
                'partition': {
                    'rowspan': len(analyses)-len(partitions_ids),
                    'colspan': 1,
                    'value': partitions_ids,
                    },
                'container': {
                    'rowspan': len(analyses)-len(containers_type),
                    'colspan': 1,
                    'value': containers_type,
                    },
                'analyses': {
                    'rowspan': 1,
                    'colspan': 1,
                    'value': analyses,
                    },
            }
            rows.append(row_info)
            total_analyses += analyses
        # table will contain the data that from where the html
        # will take the info
        table = {
            'columns': columns,
            'rows': rows,
            'total_analyses': range(len(total_analyses))
        }
        import pdb; pdb.set_trace()
        return table
