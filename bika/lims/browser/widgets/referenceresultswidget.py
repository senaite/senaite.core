from AccessControl import ClassSecurityInfo, ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr, DisplayList
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils

class ReferenceResultsWidget(RecordsWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/referenceresultswidget",
        'helper_js': ("bika_widgets/referenceresultswidget.js",),
        'helper_css': ("bika_widgets/referenceresultswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ All ResultsField.X.records: fields have keyword specified in the TAL.
            Remove rows with no other values entered, here.
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        for idx in range(len(value) - 1, -1, -1):
            if len(value[idx].keys()) == 1: del value[idx]
        return value, {}

    security.declarePublic('getServicesByCategory')
    def getServicesByCategory(self):
        """Returns a dictionary of AnalysisCategory[service,service,...]
        """
        categories = {}
        pc = getToolByName(self, 'portal_catalog')
        services = pc(portal_type = 'AnalysisService')
        for service in services:
            service = service.getObject()
            CategoryUID = service.getCategory().UID()
            CategoryTitle = service.getCategory().Title()
            key = "%s_%s"%(CategoryUID, CategoryTitle)
            if categories.has_key(key):
                categories[key].append({'keyword': service.getKeyword(),
                                        'title': service.Title(),
                                        'uid' : service.UID()})
            else:
                categories[key] = [{'keyword': service.getKeyword(),
                                    'title': service.Title(),
                                    'uid': service.UID()},]
        return categories

    security.declarePublic('getServicesWithResultsByCategory')
    def getServicesWithResultsByCategory(self, field):
        """ list of services which have results specified in field
        """
        categories = {}
        pc = getToolByName(self, 'portal_catalog')
        for ref in getattr(field, field.accessor)():
            service = pc(portal_type='AnalysisService',
                         getKeyword=ref['keyword'])[0]
            service = service.getObject()
            CategoryUID = service.getCategory().UID()
            CategoryTitle = service.getCategory().Title()
            key = "%s_%s"%(CategoryUID, CategoryTitle)
            ref['title'] = service.Title()
            if not categories.has_key(key):
                categories[key] = {}
            categories[key][service.UID()] = ref
        return categories

    security.declarePublic('getCategoryUID')
    def getCategoryUID(self, category_title):
        pc = getToolByName(self, 'portal_catalog')
        cats = pc(portal_type = "AnalysisCategory")
        cats = [cat.UID for cat in cats if cat.Title == category_title]
        if cats:
            return cats[0]
        else:
            return ""

    security.declarePublic('dumps')
    def dumps(self, data):
        import json
        return json.dumps(data)

registerWidget(ReferenceResultsWidget,
               title = 'Reference definition results',
               description = ('Reference definition results.'),
               )

#registerPropertyType('default_search_index', 'string', AnalysisSpecsWidget)
