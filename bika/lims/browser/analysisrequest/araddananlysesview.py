from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales
from zope.interface import implements

class ARAddAnalysesView(AnalysisRequestViewView):
    """ listing to display Analyses table for AR Add.
    """
    template = ViewPageTemplateFile("templates/add_analyses.pt")

    def __init__(self, context, request):
        super(ARAddAnalysesView, self).__init__(context, request)
        self.portal_url = \
          getToolByName(context, 'portal_url').getPortalObject().absolute_url()

    def __call__(self):
        """ return analyses table
        """
        # turn of the editable border
        return self.template()

    def getPointsOfCapture(self):
        return POINTS_OF_CAPTURE
