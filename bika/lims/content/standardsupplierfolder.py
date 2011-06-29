"""StandardSupplierFolder is a container for StandardSupplier instances.

$Id: StandardSupplierFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from ZODB.POSException import ConflictError
from plone.app.folder.folder import ATFolder
from bika.lims.interfaces import IStandardSupplierFolder, IHaveNoBreadCrumbs
from zope.interface import implements

schema = BikaFolderSchema.copy()

class StandardSupplierFolder(ATFolder):
    implements(IStandardSupplierFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    schema = schema

atapi.registerType(StandardSupplierFolder, PROJECTNAME)
