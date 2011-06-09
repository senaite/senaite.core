from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.browser.fields import TemplatePositionField
from Products.bika.browser.widgets import TemplatePositionWidget
from Products.bika.browser.widgets import ServicesWidget
from Products.bika.config import ANALYSIS_TYPES, I18N_DOMAIN, PROJECTNAME
from Products.bika.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
    TextField('WorksheetTemplateDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TemplatePositionField('Row',
        required = 1,
        widget = TemplatePositionWidget(
            label = 'Positions',
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

class WorksheetTemplate(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('getAnalysisTypes')
    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES

registerType(WorksheetTemplate, PROJECTNAME)
