from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from archetypes.referencebrowserwidget import utils
from bika.lims.config import POINTS_OF_CAPTURE
from types import StringType

class ServicesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/serviceswidget",
        'helper_js': ("bika_widgets/serviceswidget.js",),
        'helper_css': ("bika_widgets/serviceswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('getCategories')
    def Categories(self, field, allservices = True):
        """ Returns a list of Analysis Categories (keyed by PointOfCapture)
            allservices - set False to return only checked services (for widget view)
        
            returns
            
            {('field', 'Field Analyses PointOfOrigin'):
                {('general', 'General Category'):
                   [('serviceUID','serviceTitle'),('serviceUID','serviceTitle'), ..]
                }
            } 
        """
        cats = {}
        pc = getToolByName(self, 'portal_catalog')
        for poc in POINTS_OF_CAPTURE.keys():
            val = POINTS_OF_CAPTURE.getValue(poc)
            cats[(poc, val)] = {}

        selectedservices = getattr(field, field.accessor)()
        services = pc(portal_type = "AnalysisService")
        # get all services from catalog        
        if allservices:
            for service in services:
                cat = (service.getCategoryUID, service.getCategoryName)
                poc = (service.getPointOfCapture, POINTS_OF_CAPTURE.getValue(service.getPointOfCapture))
                srv = (service.UID, service.Title)
                if not cats[poc].has_key(cat): cats[poc][cat] = []
                cats[poc][cat].append(srv)
        # or get currently selected services from this profile
        else:
            for service in selectedservices:
                cat = (service.getCategoryUID(), service.getCategoryName())
                poc = (service.getPointOfCapture(), POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()))
                srv = (service.UID(), service.Title())
                if not cats[poc].has_key(cat): cats[poc][cat] = []
                cats[poc][cat].append(srv)
        return cats

    def dumpsJSON(self, object):
        import json
        return json.dumps(object)

registerWidget(ServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               used_for = ('Products.Archetypes.Field.ReferenceField',)
               )

#registerPropertyType('default_search_index', 'string', ServicesWidget)
