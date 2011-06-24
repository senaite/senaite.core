"""The lab staff

$Id: LabContact.py 639 2007-03-20 09:35:32Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from bika.lims.content.person import Person
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME

schema = Person.schema.copy() + Schema((
    ImageField('Signature',
        widget = ImageWidget(
            label = 'Signature',
            label_msgid = 'label_signature',
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False

class LabContact(Person):
    security = ClassSecurityInfo()
    schema = schema

    def Title(self):
        """ Return the contact's Fullname as title """
        return self.getFullname()

registerType(LabContact, PROJECTNAME)
