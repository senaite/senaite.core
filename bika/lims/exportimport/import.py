from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.content.instrument import getDataInterfaces
from bika.lims.exportimport import instruments
from bika.lims.exportimport.load_setup_data import LoadSetupData
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from pkg_resources import *
import plone

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

    def getDataInterfaces(self):
        return getDataInterfaces(self.context)

    def getSetupDatas(self):
        datasets = []
        for f in resource_listdir('bika.lims', 'setupdata'):
            try:
                if f+".xlsx" in resource_listdir('bika.lims', 'setupdata/%s'%f):
                    datasets.append(f)
            except OSError:
                pass
        return datasets

    def __call__(self):
        if 'submitted' in self.request:
            if 'setupfile' in self.request.form or \
               'setupexisting' in self.request.form:
                lsd = LoadSetupData(self.context, self.request)
                return lsd()
            else:
                exim = getattr(instruments, self.request['exim'])
                return exim.Import(self.context, self.request)
        else:
            return self.template()

class ajaxGetImportTemplate(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        exim = self.request.get('exim')
        return ViewPageTemplateFile("instruments/%s_import.pt" % exim)(self)
