"""StandardSupplierFolder is a container for StandardSupplier instances.

$Id: StandardSupplierFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from ZODB.POSException import ConflictError
from plone.app.folder.folder import ATFolder

schema = BikaFolderSchema.copy()

class StandardSupplierFolder(ATFolder):
    security = ClassSecurityInfo()
    schema = schema

registerType(StandardSupplierFolder, PROJECTNAME)
