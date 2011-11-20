from AccessControl import ClassSecurityInfo, ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
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
        """ All records have have UID specified in the TAL, so they will show up as valid
            RecordsWidget entries. We remove rows with no other values entered, here.
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
        """Returns a dictionary of all services that do not have dependents.
        If a service has dependents, the reference samples should cater for
        those instead.
        AnalysisCategory[service,service,...]
        """
        categories = {}
        bsc = getToolByName(self, 'bika_setup_catalog')
        services = bsc(portal_type = 'AnalysisService',
                       sort_on='sortable_title')
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            CategoryUID = service.getCategory().UID()
            CategoryTitle = service.getCategory().Title()
            key = "%s_%s"%(CategoryUID, CategoryTitle)
            if categories.has_key(key):
                categories[key].append({'title': service.Title(),
                                        'uid' : service.UID()})
            else:
                categories[key] = [{'title': service.Title(),
                                    'uid': service.UID()},]
        return categories

    security.declarePublic('getServicesWithResultsByCategory')
    def getServicesWithResultsByCategory(self, field):
        """ list of services which have results specified in field
        """
        categories = {}
        bsc = getToolByName(self, 'bika_setup_catalog')
        for ref in getattr(field, field.accessor)():
            service = bsc(portal_type='AnalysisService',
                          sort_on='sortable_title',
                          UID=ref['uid'])[0]
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            CategoryUID = service.getCategory().UID()
            CategoryTitle = service.getCategory().Title()
            key = "%s_%s"%(CategoryUID, CategoryTitle)
            ref['title'] = service.Title()
            ref['service'] = ref['uid']
            if not categories.has_key(key):
                categories[key] = {}
            categories[key][service.UID()] = ref
        return categories

    security.declarePublic('getCategoryUID')
    def getCategoryUID(self, category_title):
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = bsc(portal_type = "AnalysisCategory",
                   sort_on = 'sortable_title')
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
