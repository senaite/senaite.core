"""ReferenceSupplierFolder is a container for ReferenceSupplier instances.

$Id: ReferenceSupplierFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from ZODB.POSException import ConflictError
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IReferenceSupplierFolder, IHaveNoBreadCrumbs
from bika.lims.utils import generateUniqueId
from plone.app.folder.folder import ATFolder
from zope.interface import implements

schema = BikaFolderSchema.copy()

class ReferenceSupplierFolder(ATFolder):
    implements(IReferenceSupplierFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

atapi.registerType(ReferenceSupplierFolder, PROJECTNAME)
