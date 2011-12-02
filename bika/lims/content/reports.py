from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.interfaces import IReports
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy()

class Reports(BaseContent):
    implements(IReports)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(Reports, PROJECTNAME)
