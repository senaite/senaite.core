from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IGenerateUniqueId
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy()

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class ReferenceManufacturer(BaseContent):
    implements(IGenerateUniqueId)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(ReferenceManufacturer, PROJECTNAME)
