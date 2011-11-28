from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy()

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class ReferenceManufacturer(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(ReferenceManufacturer, PROJECTNAME)
