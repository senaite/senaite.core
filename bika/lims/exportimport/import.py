from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.content.instrument import getDataInterfaces
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.exportimport import instruments

class ImportView(BrowserView):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("import.pt")

    def __init__(self, context, request):
        super(ImportView, self).__init__(context, request)

        self.icon = ""
        self.title = _("Import")
        self.description = _("Select a data interface")

        request.set('disable_border', 1)

        # templates for each importer
        self.exims = {}
        for exim_id in instruments.__all__:
            exim = getattr(instruments, exim_id)
            self.exims[exim_id] = {
                'template': ViewPageTemplateFile("instruments/%s_import.pt" % exim_id)}

    def __call__(self):
        return self.template()

    def getDataInterfaces(self):
        return getDataInterfaces(self.context)

    def getImportTemplate(self):
        return self.exims[self.context.request['importer']]
