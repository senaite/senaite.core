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
))

class Method(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

registerType(Method, PROJECTNAME)
