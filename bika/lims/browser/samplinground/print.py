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

    def getAnalysisRequestByPartitions(self):
        """
        Returns a list of dictionaries sorted by Sample Partition/Container
        [{'requests and partition info'}, ...]
        """
        l = []
        import pdb; pdb.set_trace()
        ars = self.context.getAnalysisRequests()
        for ar in ars:
            partitions = ar.getPartitions()
            for part in partitions:
                row_info = {
                    'sample_id': {
                        'title': 'Sample ID'
                        'value': ar.getSample().id},
                    'sample_type': ar.getSampleType(),
                    'sample_point': ar.getSamplePoint(),
                    'ar_id': ar.id,
                    'part_id': part.id,
                    'securitySeal': part.getContainer().getSecuritySealIntact(),
                }
                l.append(row_info)
        return l
