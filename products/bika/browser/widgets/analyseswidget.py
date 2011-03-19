from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget


class AnalysesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "bika_widgets/analyseswidget",
        'helper_js': ('bika_widgets/analyseswidget.js',
                      'bika_widgets/dhtml.js'),
        })

    security = ClassSecurityInfo()

    security.declarePublic('Checked')
    def Checked(self, service, value):
        wtool = getToolByName(service, 'portal_workflow')
        for analyses in value:
            review_state = wtool.getInfoFor(analyses, 'review_state', '')
            if review_state == 'not_requested':
                continue
            if service.UID() == analyses.getService().UID():
                return 'checked'

    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ handle analyses input """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        return value, {}


registerWidget(AnalysesWidget,
               title = 'Analyses',
               description = ('Renders a widget for analyses'),
               used_for = ('Products.bika.AnalysesField.AnalysesField',)
               )

