"""The lab staff

$Id: LabContact.py 639 2007-03-20 09:35:32Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.bika.Person import Person
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
    schema = schema

registerType(LabContact, PROJECTNAME)
