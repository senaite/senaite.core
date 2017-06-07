# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

Salutation = StringField(
    'Salutation',
    widget=StringWidget(
        label=_("Salutation",
                "Title"),
        description=_("Greeting title eg. Mr, Mrs, Dr")
    )
)

Firstname = StringField(
    'Firstname',
    required=1,
    widget=StringWidget(
        label=_("Firstname")
    )
)

Middleinitial = StringField(
    'Middleinitial',
    required=0,
    widget=StringWidget(
        label=_("Middle initial")
    )
)

Middlename = StringField(
    'Middlename',
    required=0,
    widget=StringWidget(
        label=_("Middle name")
    )
)

Surname = StringField(
    'Surname',
    required=1,
    widget=StringWidget(
        label=_("Surname")
    )
)

Fullname = ComputedField(
    'Fullname',
    expression='context.getFullname()',
    searchable=1,
    widget=ComputedWidget(
        label=_("Full Name"),
        visible={'edit': 'invisible', 'view': 'invisible'}
    )
)

Username = StringField(
    'Username',
    widget=StringWidget(
        visible=False
    )
)

EmailAddress = StringField(
    'EmailAddress',
    schemata='Email Telephone Fax',
    searchable=1,
    widget=StringWidget(
        label=_("Email Address")
    )
)

BusinessPhone = StringField(
    'BusinessPhone',
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (business)")
    )
)

BusinessFax = StringField(
    'BusinessFax',
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Fax (business)")
    )
)

HomePhone = StringField(
    'HomePhone',
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (home)")
    )
)

MobilePhone = StringField(
    'MobilePhone',
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (mobile)")
    )
)

JobTitle = StringField(
    'JobTitle',
    widget=StringWidget(
        label=_("Job title")
    )
)

Department = StringField(
    'Department',
    widget=StringWidget(
        label=_("Department")
    )
)

PhysicalAddress = AddressField(
    'PhysicalAddress',
    schemata='Address',
    widget=AddressWidget(
        label=_("Physical address")
    )
)

City = ComputedField(
    'City',
    expression='context.getPhysicalAddress().get("city")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    )
)

District = ComputedField(
    'District',
    expression='context.getPhysicalAddress().get("district")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    )
)

PostalCode = ComputedField(
    'PostalCode',
    expression='context.getPhysicalAddress().get("postalCode")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    )
)

Country = ComputedField(
    'Country',
    expression='context.getPhysicalAddress().get("country")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    )
)

PostalAddress = AddressField(
    'PostalAddress',
    schemata='Address',
    widget=AddressWidget(
        label=_("Postal address")
    )
)

ObjectWorkflowStates = ComputedField(
    'ObjectWorkflowStates',
    expression='context.getObjectWorkflowStates()',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    )
)

schema = BikaSchema.copy() + Schema((
    Salutation,
    Firstname,
    Middleinitial,
    Middlename,
    Surname,
    Fullname,
    Username,
    EmailAddress,
    BusinessPhone,
    BusinessFax,
    HomePhone,
    MobilePhone,
    JobTitle,
    Department,
    PhysicalAddress,
    City,
    District,
    PostalCode,
    Country,
    PostalAddress,
    ObjectWorkflowStates
))


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
        mi = self.getMiddleinitial()
        md = self.getMiddlename()
        sn = self.getSurname()
        fullname = ''
        if fn or sn:
            if mi and md:
                fullname = '%s %s %s %s' % (
                    self.getFirstname(),
                    self.getMiddleinitial(),
                    self.getMiddlename(),
                    self.getSurname())
            elif mi:
                fullname = '%s %s %s' % (
                    self.getFirstname(),
                    self.getMiddleinitial(),
                    self.getSurname())
            elif md:
                fullname = '%s %s %s' % (
                    self.getFirstname(),
                    self.getMiddlename(),
                    self.getSurname())
            else:
                fullname = '%s %s' % (self.getFirstname(), self.getSurname())
        return fullname.strip()

    def getListingname(self):
        """ return Person's Fullname as Surname, Firstname """
        fn = self.getFirstname()
        mi = self.getMiddleinitial()
        md = self.getMiddlename()
        sn = self.getSurname()
        if fn and sn:
            fullname = '%s, %s' % (self.getSurname(), self.getFirstname())
        elif fn or sn:
            fullname = '%s %s' % (self.getSurname(), self.getFirstname())
        else:
            fullname = ''

        if fullname != '':
            if mi and md:
                fullname = '%s %s %s' % (fullname, self.getMiddleinitial(),
                                         self.getMiddlename())
            elif mi:
                fullname = '%s %s' % (fullname, self.getMiddleinitial())
            elif md:
                fullname = '%s %s' % (fullname, self.getMiddlename())

        return fullname.strip()

    Title = getFullname

    security.declareProtected(CMFCorePermissions.ManagePortal, 'hasUser')

    def hasUser(self):
        """Check if contact has user
         """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    def getObjectWorkflowStates(self):
        """Returns a dictionary with the workflow id as key and workflow 
        state as value.
        :returns: {'review_state':'active',...}
        """
        workflow = getToolByName(self, 'portal_workflow')
        states = {}
        for w in workflow.getWorkflowsFor(self):
            state = w._getWorkflowStateOf(self).id
            states[w.state_var] = state
        return states


registerType(Person, PROJECTNAME)
