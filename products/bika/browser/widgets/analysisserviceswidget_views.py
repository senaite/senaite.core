""" Widget helper views.
    Widget templates must live in skins folders,
    They can access these views from TAL.
"""

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.bika.interfaces import IAnalysisServicesWidgetHelper, \
    IBikaLIMSLayer
from Products.bika import logger
from zope.interface import implements

class AnalysisServicesWidgetHelper(BrowserView):
    """ This view contains utility methods used by AnalysisServiceWidget template.
    """
    implements(IAnalysisServicesWidgetHelper)

    def Categories(self):
        """ Returns a a list of Analysis Categories.
        """
        return self.context.portal_catalog(portal_type = 'AnalysisCategory')


class AnalysisServicesWidget_AnalysisServices(BrowserView):
    """ Render a list of Analysis Services
    """
    implements(IBikaLIMSLayer)
    template = ViewPageTemplateFile("analysisserviceswidget_analysisservices.pt")

    def services(self):
        categoryUID = self.request.get('categoryUID', None)
        if not categoryUID: return ""
        servicebrains = self.context.portal_catalog(portal_type = 'AnalysisService')
        # XXX slow / stupid
        return [service for service in servicebrains if service.getCategoryUID == categoryUID]

    def __call__(self):
        return self.template()
