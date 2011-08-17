"""A log entry for a method.

$Id: MethodLogEntry.py 319 2008-08-22 20:27:14Z godfrey $
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField
from AccessControl import getSecurityManager
from bika.lims.config import PROJECTNAME
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

schema = BaseSchema.copy() + Schema((
    DateTimeField('ChangeDate',
        default_method = 'current_date',
        index = 'DateIndex'
    ),
    StringField('UserName',
        default_method = 'current_user'
    ),
),
)

class MethodLogEntry(BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'MethodLogEntry'
    schema = schema
    allowed_content_types = ()
    global_allow = 0
    filter_content_types = 1
    use_folder_tabs = 0
    factory_type_information = {
        'title': 'Method log entry',
        }
    actions = ()

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('current_user')
    def current_user(self):
        """ return current user """
        return getSecurityManager().getUser()

registerType(MethodLogEntry, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references',
                       'metadata', 'localroles'):
            a['visible'] = 0
    return fti
