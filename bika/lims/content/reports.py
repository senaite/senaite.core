from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IReports, IHaveNoBreadCrumbs
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface import implements

schema = ATFolderSchema.copy()

class Reports(ATFolder):
    implements(IReports, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(Reports, PROJECTNAME)
