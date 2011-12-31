"""A simple log entry.
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField
from AccessControl import getSecurityManager
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BaseSchema.copy() + Schema((
    DateTimeField('ChangeDate',
        default_method = 'current_date',
    ),
    StringField('UserName',
        default_method = 'current_user'
    ),
),
)

class LogEntry(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime()

    security.declarePublic('current_user')
    def current_user(self):
        return getSecurityManager().getUser()

registerType(LogEntry, PROJECTNAME)
