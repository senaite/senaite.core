"""AttachmentType - the type of attachment

$Id: AttachmentType.py 1000 2007-12-03 11:53:04Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy()

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class AttachmentType(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(AttachmentType, PROJECTNAME)
