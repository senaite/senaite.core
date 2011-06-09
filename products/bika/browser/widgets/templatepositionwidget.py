from AccessControl import ClassSecurityInfo, ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr, DisplayList
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils

class TemplatePositionWidget(RecordsWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/templatepositionwidget",
        'helper_js': ("bika_widgets/templatepositionwidget.js",),
        'helper_css': ("bika_widgets/templatepositionwidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('get_template_rows')
    def get_template_rows(self, num_positions, template_rows):
        print template_rows
        try:
            num_pos = int(num_positions)
        except ValueError:
            num_pos = 0
        rows = []
        i = 1
        if template_rows:
            for t_row in template_rows:
                if num_pos > 0:
                    if i > num_pos:
                        break
                rows.append(t_row)
                i = i + 1
        else:
            if num_pos == 0:
                num_pos = 10
        for i in range(i, (num_pos + 1)):
            row = {
                'pos': i,
                'type': 'a',
                'sub': 1}
            rows.append(row)

        return rows

registerWidget(TemplatePositionWidget,
               title = 'WS Template Analyses Layout',
               description = ('Worksheet analyses layout.'),
               )
