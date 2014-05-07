"""WorksheetFolder is a container for Worksheet instances.
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IWorksheetFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class WorksheetFolder(folder.ATFolder):
    implements(IWorksheetFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(WorksheetFolder, PROJECTNAME)
