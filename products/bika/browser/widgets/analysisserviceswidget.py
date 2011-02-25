from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils
from types import StringType



class AnalysisServicesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisserviceswidget",
        'helper_js': ("bika_widgets/analysisserviceswidget.js",),
        'helper_css': ("bika_widgets/analysisserviceswidget.css",),
    })

    security = ClassSecurityInfo()


registerWidget(AnalysisServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               used_for = ('Products.Archetypes.Field.ReferenceField',)
               )

#registerPropertyType('default_search_index', 'string', AnalysisRequestWidget)
