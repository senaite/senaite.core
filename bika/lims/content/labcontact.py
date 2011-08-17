"""The lab staff

$Id: LabContact.py 639 2007-03-20 09:35:32Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.content.person import Person
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME, \
    I18N_DOMAIN        
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')
import sys

schema = Person.schema.copy() + Schema((
    ImageField('Signature',
        widget = ImageWidget(
            label = 'Signature',
            label_msgid = 'label_signature',
        ),
    ),
    ReferenceField('Department',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        relationship = 'LabContactDepartment',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Department',
            label_msgid = 'label_department',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
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
