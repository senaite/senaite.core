from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.bika import logger
from archetypes.referencebrowserwidget import utils
from types import StringType

class ServicesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/serviceswidget",
        'helper_js': ("bika_widgets/serviceswidget.js",),
        'helper_css': ("bika_widgets/serviceswidget.css",),
    })

    security = ClassSecurityInfo()

    # XXX Memoize
    security.declarePublic('getCategories')
    def getCategories(self, field, allservices = True):
        """ Returns a list of Analysis Categories.
            allservices - set False to return only checked services (for widget view)
        """
        categories = {}
        if allservices:
            services = self.portal_catalog(portal_type = 'AnalysisService')
            for service in services:
                if categories.has_key(service.getCategoryName):
                    categories[service.getCategoryName].append(service)
                else:
                    categories[service.getCategoryName] = [service, ]
        else:
            services = getattr(field, field.accessor)()
            for service in services:
                if categories.has_key(service.getCategoryName()):
                    categories[service.getCategoryName()].append(service)
                else:
                    categories[service.getCategoryName()] = [service, ]

        return categories

    security.declarePublic('getCategoryUID')
    def getCategoryUID(self, category_title):
        catalog = getToolByName(self, 'portal_catalog')
        cats = catalog(portal_type = "AnalysisCategory")
        cats = [cat.UID for cat in cats if cat.Title == category_title]
        if cats:
            return cats[0]
        else:
            return ""

    security.declarePublic('SelectedServices')
    def SelectedServices(self, field, category_title):
        """Return a list of selected services in a category
        """
        services = []
        for service in getattr(field, field.accessor)():
            if service.getCategoryName() == category_title:
                services.append(service)
        return services

registerWidget(ServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               used_for = ('Products.Archetypes.Field.ReferenceField',)
               )

#registerPropertyType('default_search_index', 'string', ServicesWidget)
