from analysesperservice import AnalysesPerService
from analysespersampletype import AnalysesPerSampleType
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import TimeOrDate
from bika.lims.interfaces import IReports
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class ProductivityView(BrowserView):
    """ Sample View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("reports_productivity.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        return self.template()

class QualityControlView(BrowserView):
    """ Sample View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("reports_qualitycontrol.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        return self.template()

class AdministrationView(BrowserView):
    """ Sample View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("reports_administration.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        return self.template()

class SubmitForm(BrowserView):
    """ Redirect to specific report
    """
    implements(IViewView)
    template = ViewPageTemplateFile("report_frame.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        #self.request.form values to determine which report really wanted jkkkk
        self.reportout = AnalysesPerService(self.context, self.request)()
        #self.reportout = AnalysesPerSampleType(self.context, self.request)()

        return self.template()

