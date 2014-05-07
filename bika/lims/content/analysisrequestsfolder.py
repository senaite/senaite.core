"""AnalysisRequestsFolder is a fake folder to live in the nav bar.  It has
view from browser/analysisrequest.py wired to it.
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IAnalysisRequestsFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t

schema = folder.ATFolderSchema.copy()

class AnalysisRequestsFolder(folder.ATFolder):
    implements(IAnalysisRequestsFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(AnalysisRequestsFolder, PROJECTNAME)
