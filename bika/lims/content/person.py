from webdav.common import rfc1123_date
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.ATExtensions.ateapi import RecordWidget
from bika.lims.browser.widgets import AddressWidget
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from bika.lims.config import GENDERS, PROJECTNAME
from bika.lims.browser.fields import AddressField
from bika.lims import PMF, bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('Salutation',
        widget = StringWidget(
            label = _("Salutation",
                      "Title"),
            description = _("Greeting title eg. Mr, Mrs, Dr"),
        ),
    ),
    StringField('Firstname',
        required = 1,
        widget = StringWidget(
            label = _("Firstname"),
        ),
    ),
    StringField('Surname',
        required = 1,
        widget = StringWidget(
            label = _("Surname"),
        ),
    ),
    ComputedField('Fullname',
        expression = 'context.getFullname()',
        searchable = 1,
        widget = ComputedWidget(
            label = _("Full Name"),
            visible = {'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    StringField('Username',
        widget = StringWidget(
            visible = False
        ),
    ),
    StringField('EmailAddress',
        schemata = 'Email Telephone Fax',
        searchable = 1,
        widget = StringWidget(
            label = _("Email Address"),
        ),
    ),
    StringField('BusinessPhone',
        schemata = 'Email Telephone Fax',
        widget = StringWidget(
            label = _("Phone (business)"),
        ),
    ),
    StringField('BusinessFax',
        schemata = 'Email Telephone Fax',
        widget = StringWidget(
            label = _("Fax (business)"),
        ),
    ),
    StringField('HomePhone',
        schemata = 'Email Telephone Fax',
        widget = StringWidget(
            label = _("Phone (home)"),
        ),
    ),
    StringField('MobilePhone',
        schemata = 'Email Telephone Fax',
        widget = StringWidget(
            label = _("Phone (mobile)"),
        ),
    ),
    StringField('JobTitle',
        widget = StringWidget(
            label = _("Job title"),
        ),
    ),
    StringField('Department',
        widget = StringWidget(
            label = _("Department"),
        ),
    ),
    AddressField('PhysicalAddress',
        schemata = 'Address',
        widget = AddressWidget(
           label = _("Physical address"),
        ),
    ),
    AddressField('PostalAddress',
        schemata = 'Address',
        widget = AddressWidget(
           label = _("Postal address"),
        ),
    ),
),
)

class Person(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
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

    def getListingname(self):
        """ return Person's Fullname as Surname, Firstname """
        fn = self.getFirstname()
        sn = self.getSurname()
        if fn and sn:
            return '%s, %s' % (self.getSurname(), self.getFirstname())
        elif fn or sn:
            return '%s %s' % (self.getSurname(), self.getFirstname())
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
