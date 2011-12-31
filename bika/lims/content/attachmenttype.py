"""AttachmentType - the type of attachment
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IGenerateUniqueId
import sys
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy()

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class AttachmentType(BaseContent):
    implements(IGenerateUniqueId)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(AttachmentType, PROJECTNAME)
