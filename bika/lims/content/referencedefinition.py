"""Reference Definitions represent standard specifications for reference samples used in quality control
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
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    ReferenceResultsField('ReferenceResults',
        schemata = 'Reference Results',
        required = 1,
        widget = ReferenceResultsWidget(
            label = _("Reference Results"),
            description = _("Enter the expected results and the min and max allowed values, "
                            "or enter the expected result and an error % for the system to "
                            "calculate min and max values"),
        ),
    ),
    BooleanField('Blank',
        schemata = 'Description',
        default = False,
        widget = BooleanWidget(
            label = _("Blank"),
            description = _("Check this if the reference sample values are zero or 'blank'"),
        ),
    ),
    BooleanField('Hazardous',
        schemata = 'Description',
        default = False,
        widget = BooleanWidget(
            label = _("Hazardous"),
            description = _("Check this box if these reference samples should be treated as hazardous"),
        ),
    ),
))

schema['title'].schemata = 'Description'
schema['title'].widget.visible = True
schema['description'].schemata = 'Description'
schema['description'].widget.visible = True

class ReferenceDefinition(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

registerType(ReferenceDefinition, PROJECTNAME)
