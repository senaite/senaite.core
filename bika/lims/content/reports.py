from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.interfaces import IReports
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface import implements

schema = ATFolderSchema.copy()

class Reports(ATFolder):
    implements(IReports)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(Reports, PROJECTNAME)
