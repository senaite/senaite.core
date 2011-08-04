"""ReferenceDefinition represents a Reference Definition or sample type used for
    quality control testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys
import time

schema = BikaSchema.copy() + Schema((
    ReferenceResultsField('ReferenceResults',
        required = 1,
        widget = ReferenceResultsWidget(
            label = "Reference Results",
            label_msgid = "label_reference_results",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = "Hazardous",
            label_msgid = "label_hazardous",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))


class ReferenceDefinition(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

registerType(ReferenceDefinition, PROJECTNAME)
