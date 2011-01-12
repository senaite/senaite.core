"""The lab staff

$Id: LabContact.py 639 2007-03-20 09:35:32Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.BikaMembers.Person import Person
from Products.BikaMembers.references import SymmetricalReference
from Products.bika.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin

schema = Person.schema.copy() + Schema((
    ImageField('Signature',
        widget = ImageWidget(
            label = 'Signature',
            label_msgid = 'label_signature',
        ),
    ),
))

schema['JobTitle'].schemata = 'default'

IdField = schema['id']
IdField.schemata = 'default'
IdField.widget.visible = False
# Don't make title required - it will be computed from the Person's
# Fullname
TitleField = schema['title']
TitleField.schemata = 'default'
TitleField.required = 0
TitleField.widget.visible = False

class LabContact(VariableSchemaSupport, BrowserDefaultMixin, Person):
    security = ClassSecurityInfo()
    archetype_name = 'LabContact'
    schema = schema
    allowed_content_types = ('Address',)
    content_icon = 'contact.png'
    default_view = 'tool_base_edit'
    immediate_view = 'tool_base_edit'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
        # Make view action the same as edit
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/tool_base_edit',
         'permissions': (permissions.ModifyPortalContent,),
        },
        {'id': 'edit',
         'name': 'Edit',
         'action': 'string:${object_url}/tool_base_edit',
         'permissions': (permissions.ModifyPortalContent,),
        },
    )

registerType(LabContact, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
