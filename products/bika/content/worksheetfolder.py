"""WorksheetFolder is a container for Worksheet instances.

$Id: WorksheetFolder.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.bika.config import PROJECTNAME
from plone.app.folder import folder
from Products.bika.interfaces import IWorksheetFolder, IHaveNoByline
from zope.interface import implements
from Products.bika.config import ManageWorksheets, PROJECTNAME

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class WorksheetFolder(folder.ATFolder):
    implements(IWorksheetFolder, IHaveNoByline)
    schema = schema
    displayContentsTab = False

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(WorksheetFolder, PROJECTNAME)
