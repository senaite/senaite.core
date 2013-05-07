"""
"""
from AccessControl import ClassSecurityInfo
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IQueryFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface import implements

schema = folder.ATFolderSchema.copy()


class QueryFolder(folder.ATFolder):
    implements(IQueryFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(QueryFolder, PROJECTNAME)
