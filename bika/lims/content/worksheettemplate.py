from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.browser.widgets import WorksheetTemplateLayoutWidget
from bika.lims.config import ANALYSIS_TYPES, I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

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
