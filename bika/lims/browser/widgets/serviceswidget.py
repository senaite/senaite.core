from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
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

    security.declarePublic('getServices')
    def getServices(self, field, selected_only = False):
        """ Returns a list of Analysis Services keyed by POC and Category
            selected_only - set this to return only checked services (for view widget)

            returns

            {('poc_id', 'Point Of Capture'):
                {('cat_id', 'Category Title'): [('serviceUID','service Title'), ..]
                }
            }
        """
        pc = getToolByName(self, 'portal_catalog')
        allservices = [p.getObject() for p in pc(portal_type = "AnalysisService", sort_on='sortable_title')]
        selectedservices = getattr(field, field.accessor)()
        res = {}
        for poc_id in POINTS_OF_CAPTURE.keys():
            poc_title = POINTS_OF_CAPTURE.getValue(poc_id)
            res[(poc_id, poc_title)] = {}
        if selected_only:
            services = selectedservices
        else:
            services = allservices
        for service in services:
            cat = (service.getCategoryUID(), service.getCategoryName())
            poc = (service.getPointOfCapture(), POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()))
            srv = (service.UID(), service.Title())
            if not res[poc].has_key(cat): res[poc][cat] = []
            res[poc][cat].append(srv)
        return res

    def dumpsJSON(self, object):
        import json
        return json.dumps(object)

registerWidget(ServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               )

#registerPropertyType('default_search_index', 'string', ServicesWidget)
