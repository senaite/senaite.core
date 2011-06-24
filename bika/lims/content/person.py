from webdav.common import rfc1123_date
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.ATExtensions.ateapi import RecordWidget
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from bika.lims.config import GENDERS, PROJECTNAME
from bika.lims.browser.fields import AddressField

schema = BikaSchema.copy() + Schema((
    StringField('Salutation',
        widget = StringWidget(
            label = 'Title',
            label_msgid = 'label_salutation',
            description = "Greeting title eg. Mr, Mrs, Dr",
            description_msgid = "help_salutation",
        ),
    ),
    StringField('Firstname',
        required = 1,
        widget = StringWidget(
            label = 'Firstname',
            label_msgid = 'label_firstname',
        ),
    ),
    StringField('Surname',
        required = 1,
        widget = StringWidget(
            label = 'Surname',
            label_msgid = 'label_surname',
        ),
    ),
    ComputedField('Fullname',
        expression = 'context.getFullname()',
        searchable = 1,
        widget = ComputedWidget(
            label = 'Full name',
            label_msgid = 'label_fullname',
            visible = {'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    StringField('Username',
        index = 'FieldIndex',
        widget = StringWidget(
            visible = False
        ),
    ),
    StringField('EmailAddress',
        searchable = 1,
        widget = StringWidget(
            label = 'Email address',
            label_msgid = 'label_email_address',
        ),
    ),
    StringField('BusinessPhone',
        index = "FieldIndex:Brains",
        widget = StringWidget(
            label = 'Phone (business)',
            label_msgid = 'label_phone_business',
        ),
    ),
    StringField('BusinessFax',
        widget = StringWidget(
            label = 'Fax (business)',
            label_msgid = 'label_fax_business',
        ),
    ),
    StringField('HomePhone',
        widget = StringWidget(
            label = 'Phone (home)',
            label_msgid = 'label_phone_home',
        ),
    ),
    StringField('MobilePhone',
        widget = StringWidget(
            label = 'Phone (mobile)',
            label_msgid = 'label_phone_mobile',
        ),
    ),
    StringField('JobTitle',
        widget = StringWidget(
            label = 'Job title',
            label_msgid = 'label_jobtitle',
        ),
    ),
    StringField('Department',
        widget = StringWidget(
            label = 'Department',
            label_msgid = 'label_department',
        ),
    ),
    AddressField('PhysicalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = 'Physical address',
           label_msgid = 'label_physical_address',
        ),
    ),
    AddressField('PostalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = 'Postal address',
           label_msgid = 'label_postal_address',
        ),
    ),
),
)

class Person(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

    security.declareProtected(CMFCorePermissions.View, 'getSchema')
    def getSchema(self):
        return self.schema

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress']

    def getFullname(self):
        """ return Person's Fullname """
        fn = self.getFirstname()
        sn = self.getSurname()
        if fn or sn:
            return '%s %s' % (self.getFirstname(), self.getSurname())
        else:
            return ''

    Title = getFullname

    security.declareProtected(CMFCorePermissions.ManagePortal, 'hasUser')
    def hasUser(self):
        """ check if contact has user """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    def getEmailAddress(self, **kw):
        """ Return the email address stored in member data if the
            person is a Plone user, else return the one stored on the
            person.
        """
        member = self.portal_membership.getMemberById(self.getUsername())
        if member:
            return member.getProperty('email')
        else:
            return self.Schema()['EmailAddress'].get(self)

    def setEmailAddress(self, value, **kw):
        """ Set email in member data if the person is a Plone user, else
            store it on the Person instance.
        """
        member = self.portal_membership.getMemberById(self.getUsername())
        if member:
            member.setMemberProperties({'email': value})
        else:
            return self.Schema()['EmailAddress'].set(self, value, **kw)


registerType(Person, PROJECTNAME)
