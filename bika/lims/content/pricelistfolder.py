"""PricelistFolder is a container for Pricelist instances.
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManagePricelists, PROJECTNAME

schema = ATBTreeFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

class PricelistFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareObjectProtected(ManagePricelists)

registerType(PricelistFolder, PROJECTNAME)
