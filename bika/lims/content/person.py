# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.person import schema


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
