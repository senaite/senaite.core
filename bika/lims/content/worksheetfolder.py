"""WorksheetFolder is a container for Worksheet instances.

$Id: WorksheetFolder.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IWorksheetFolder, IHaveNoBreadCrumbs
from bika.lims.utils import generateUniqueId
from plone.app.folder import folder
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.lims import bikaMessageFactory as _

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class WorksheetFolder(folder.ATFolder):
    implements(IWorksheetFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(WorksheetFolder, PROJECTNAME)
