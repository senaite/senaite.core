from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Registry import registerWidget
from Products.ATExtensions.ateapi import RecordsField
from Products.ATExtensions.widget import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _
import sys

class MethodInterimFieldsWidget(RecordsWidget):
    security = ClassSecurityInfo()
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/methodinterimfieldswidget",
        'helper_js': ("bika_widgets/methodinterimfieldswidget.js",),
        'helper_css': ("bika_widgets/methodinterimfieldswidget.css",),
    })

registerWidget(MethodInterimFieldsWidget,
               title = 'Interim Fields',
               description = ('Possible Interim Result fields created in analyses that use this method.'),
               )

schema = BikaSchema.copy() + Schema((
    TextField('MethodDescription',
        widget = TextAreaWidget(
            label = 'Method description',
            label_msgid = 'label_method_description',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    TextField('Instructions',
        widget = TextAreaWidget(
            label = 'Instructions',
            label_msgid = 'label_instructions',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FileField('MethodDocument',  # XXX Multiple documents please
        widget = FileWidget(
            label = 'Method document',
            label_msgid = 'label_method_document',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    RecordsField('InterimFields',
        type = 'interimfields',
        subfields = ('name', 'type', 'default'),
        required_subfields = ('name','type'),
        widget = MethodInterimFieldsWidget(
            label = 'Method Interim Fields',
            label_msgid = 'label_interim_fields',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('DependentAnalyses',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisServiceAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Dependent Analyses',
            label_msgid = 'label_dependent_analyses',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('CalculationTitle',
        widget = StringWidget(
            label = 'Calculation Title',
            label_msgid = 'label_calculation_title',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    TextField('Calculation',
        widget = TextAreaWidget(
            label = 'Calculation',
            label_msgid = 'label_method_description',
            description = 'Type the calculation formula here.  XXX XXX %x markers for dependent analyses results and InterimField field values...',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class Method(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

registerType(Method, PROJECTNAME)
