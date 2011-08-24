"""The contact person at a reference supplier organisation.

$Id: SupplierContact.py 639 2007-03-20 09:35:32Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.Archetypes.public import *
from bika.lims.content.person import Person
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

schema = Person.schema.copy()


schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'

IdField = schema['id']
IdField.schemata = 'default'
IdField.widget.visible = False
# Don't make title required - it will be computed from the Person's
# Fullname
TitleField = schema['title']
TitleField.schemata = 'default'
TitleField.required = 0
TitleField.widget.visible = False

class SupplierContact(Person):
    security = ClassSecurityInfo()
    archetype_name = 'SupplierContact'
    schema = schema
    allowed_content_types = ('Address',)
    content_icon = 'contact.png'
    default_view = 'base_edit'
    immediate_view = 'base_edit'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
        # Make view action the same as edit
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/base_edit',
         'permissions': (permissions.View,),
        },
    )

registerType(SupplierContact, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
