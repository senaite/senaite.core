from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _
import sys

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
        # subfield values must be the identical twin of Analysis.InterimFields.
        type = 'InterimFields',
        subfields = ('name', 'type', 'value', 'unit', 'collapse'),
        subfield_labels = {'name':'Name', 'type':'Type', 'value':'Default', 'unit':'Unit', 'collapse':'Collapse'},
        required_subfields = ('name',),
        widget = RecordsWidget(
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
        relationship = 'MethodAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Dependent Analyses',
            label_msgid = 'label_dependent_analyses',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TextField('Calculation',
        widget = TextAreaWidget(
            label = 'Calculation',
            label_msgid = 'label_method_description',
            description = 'The formula you type here will be dynamically calculated when an analysis using this method is displayed.',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class Method(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

registerType(Method, PROJECTNAME)
