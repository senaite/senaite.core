# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import deprecated
from bika.lims.config import PROJECTNAME
from bika.lims.content.contact import Contact
from bika.lims.content.schema.labcontact import schema
from bika.lims.interfaces import ILabContact
from zope.interface import implements


class LabContact(Contact):
    """A Lab Contact, which can be linked to a System User
    """
    implements(ILabContact)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the contact's Fullname as title """
        return safe_unicode(self.getFullname()).encode('utf-8')

    def hasUser(self):
        """ check if contact has user """
        member = self.portal_membership.getMemberById(self.getUsername())
        return member is not None

    @deprecated('[1612] Use getDepartments instead')
    def getDepartment(self):
        """
        This function is a mirror for getDepartments to maintain the
        compability with the old version.
        """
        return self.getDepartments()[0] if self.getDepartments() else None

    def getDepartments_voc(self):
        """
        Returns a vocabulary object with the available departments.
        """
        bsc = getToolByName(self, 'portal_catalog')
        departments = bsc(portal_type='Department', inactive_state='active')
        items = [(o.UID, o.Title) for o in departments]

        # Getting the departments uids
        deps_uids = [i[0] for i in items]
        # Getting the assigned departments
        objs = self.getDepartments()
        # If one department assigned to the Lab Contact is disabled, it will
        # be shown in the list until the department has been unassigned.
        for o in objs:
            if o and o.UID() not in deps_uids:
                items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def _departmentsVoc(self):
        """
        Returns a vocabulary object with the available departments.
        """
        bsc = getToolByName(self, 'portal_catalog')
        departments = bsc(portal_type='Department', inactive_state='active')
        items = [(o.UID, o.Title) for o in departments]
        # Getting the departments uids
        deps_uids = [i[0] for i in items]
        # Getting the assigned departments
        objs = self.getDepartments()
        # If one department assigned to the Lab Contact is disabled, it will
        # be shown in the list until the department has been unassigned.
        for o in objs:
            if o and o.UID() not in deps_uids:
                items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def _defaultDepsVoc(self):
        """
        Returns a vocabulary object containing all its departments.
        """
        # Getting the assigned departments
        deps = self.getDepartments()
        items = [("", "")]
        for d in deps:
            items.append((d.UID(), d.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def addDepartment(self, dep):
        """
        It adds a new department to the departments content field.
        @dep: is a uid or a department object
        @return: True when the adding process has been done,
            False otherwise.
        """
        # check if dep is an uid
        if type(dep) is str:
            deps = self.getDepartments()
            deps = [d.UID() for d in deps]
        else:
            deps = self.getDepartments()
        if dep and dep not in deps:
            deps.append(dep)
            self.setDepartments(deps)
        return True

    def removeDepartment(self, dep):
        """
        It removes a department to the departments content field.
        @dep: is a uid or a department object
        @return: True when the removing process has been done,
            False otherwise.
        """
        # check if dep is an uid
        if type(dep) is str:
            deps = self.getDepartments()
            deps = [d.UID() for d in deps]
        else:
            deps = self.getDepartments()
        if dep and dep in deps:
            deps.remove(dep)
            self.setDepartments(deps)
        return True

    def getSortedDepartments(self):
        """
        It returns the departments the departments sorted by title.
        """
        deps = self.getDepartments()
        deps.sort(key=lambda department: department.title)
        return deps


registerType(LabContact, PROJECTNAME)
