"""AttachmentType - the type of attachment

$Id: AttachmentType.py 1000 2007-12-03 11:53:04Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys

schema = BikaSchema.copy() + Schema((
    TextField('AttachmentTypeDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

class AttachmentType(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

registerType(AttachmentType, PROJECTNAME)
