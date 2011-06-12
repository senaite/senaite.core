"""CalculationType - the department in the laboratory. 

$Id: CalculationType.py 1000 2007-12-03 11:53:04Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys

schema = BikaSchema.copy() + Schema((
    TextField('CalculationTypeDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('CalcTypeCode',
        widget = StringWidget(
            label = 'Code',
            label_msgid = 'label_code',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

class CalculationType(VariableSchemaSupport, BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pairs = []
        for contact in self.portal_catalog(portal_type = 'LabContact'):
            pairs.append((contact.UID, contact.Title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    security.declarePublic('getManagerName')
    def getManagerName(self):
        if self.getManager():
            return self.getManager().getFullname()
        else:
            return ''

registerType(CalculationType, PROJECTNAME)
