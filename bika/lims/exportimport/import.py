from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.content.instrument import getDataInterfaces
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.exportimport import instruments
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

    def __call__(self):
        if 'submitted' in self.request:
            exim = getattr(instruments, self.request['exim'])
            return exim.Import(self.context, self.request)
        else:
            return self.template()

    def getDataInterfaces(self):
        return getDataInterfaces(self.context)

class ajaxGetImportTemplate(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        exim = self.request.get('exim')
        return ViewPageTemplateFile("instruments/%s_import.pt" % exim)(self)
