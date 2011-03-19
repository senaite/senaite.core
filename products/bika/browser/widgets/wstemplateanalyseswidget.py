from AccessControl import ClassSecurityInfo, ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr, DisplayList
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils

class WSTemplateAnalysesWidget(RecordsWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/wstemplateanalyseswidget",
        'helper_js': ("bika_widgets/wstemplateanalyseswidget.js", "jquery-tablednd.js"),
        'helper_css': ("bika_widgets/wstemplateanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}

    security.declarePublic('getAnalyses')
    def getAnalyses(self, field):
        """
        """
        rows = []
        for row in getattr(field, field.accessor)():
            print row
            rows.append(row)
        return rows

registerWidget(WSTemplateAnalysesWidget,
               title = 'WS Template Analyses',
               description = ('Worksheet analyses layout.'),
               used_for = ('Products.bika.browser.fields.WSTemplateAnalysesField',)
               )

#registerPropertyType('default_search_index', 'string', AnalysisSpecsWidget)
