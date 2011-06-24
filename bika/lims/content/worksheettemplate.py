from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.ATExtensions.field.records import RecordsField
from Products.ATExtensions.widget.records import RecordsWidget
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.config import ANALYSIS_TYPES, I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

class WorksheetTemplateLayoutWidget(RecordsWidget):
    security = ClassSecurityInfo()
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/worksheettemplatelayoutwidget",
        'helper_js': ("bika_widgets/worksheettemplatelayoutwidget.js",),
        'helper_css': ("bika_widgets/worksheettemplatelayoutwidget.css",),
    })

    security.declarePublic('get_template_rows')
    def get_template_rows(self, num_positions, current_field_value):
        try: num_pos = int(num_positions)
        except ValueError: num_pos = 0

        rows = []
        i = 1
        if current_field_value:
            for row in current_field_value:
                if num_pos > 0:
                    if i > num_pos:
                        break
                rows.append(row)
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

registerWidget(WorksheetTemplateLayoutWidget,
               title = 'WS Template Analyses Layout',
               description = ('Worksheet analyses layout.'),
               )

schema = BikaSchema.copy() + Schema((
    TextField('WorksheetTemplateDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    RecordsField('Row',
        required = 1,
        type = 'templateposition',
        subfields = ('pos', 'type', 'sub', 'dup'),
        required_subfields = ('pos', 'type'),
        subfield_labels = {'pos': 'Position',
                           'type': 'Type',
                           'sub': 'Subtype',
                           'dup': 'Duplicate Of'},
        widget = WorksheetTemplateLayoutWidget(
            label = 'Worksheet Layout',
            label_msgid = 'label_positions',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('Service',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'WorksheetTemplateAnalysisService',
        referenceClass = HoldingReference,
        widget = ServicesWidget(
            label = 'Analysis service',
            label_msgid = 'label_analysis',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class WorksheetTemplate(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('getAnalysisTypes')
    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES

registerType(WorksheetTemplate, PROJECTNAME)
