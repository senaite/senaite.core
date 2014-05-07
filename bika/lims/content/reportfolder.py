from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IReportFolder, IHaveNoBreadCrumbs
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface import implements

schema = ATFolderSchema.copy()

class ReportFolder(ATFolder):
    implements(IReportFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(ReportFolder, PROJECTNAME)
