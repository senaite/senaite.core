# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""The lab staff
"""
import sys

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from Products.Archetypes import atapi
from Products.Archetypes.public import StringField
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import DisplayList

from zope.interface import implements

from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.content.contact import Contact
from bika.lims.interfaces import ILabContact
from bika.lims import bikaMessageFactory as _

schema = Person.schema.copy() + atapi.Schema((
    atapi.LinesField(
        'PublicationPreference',
        vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
        default='email',
        schemata='Publication preference',
        widget=atapi.MultiSelectionWidget(
            label=_("Publication preference"),
        )),
    atapi.ImageField(
        'Signature',
        widget=atapi.ImageWidget(
            label=_("Signature"),
            description=_(
                "Upload a scanned signature to be used on printed"
                " analysis results reports. Ideal size is 250 pixels"
                " wide by 150 high"),
        )),
    atapi.ReferenceField('Departments',
                         required=0,
                         vocabulary_display_path_bound=sys.maxint,
                         allowed_types=('Department',),
                         relationship='LabContactDepartment',
                         vocabulary='_departmentsVoc',
                         referenceClass=HoldingReference,
                         multiValued=1,
                         widget=atapi.ReferenceWidget(
                             checkbox_bound=0,
                             label=_("Departments"),
                             description=_("The laboratory departments"),
                         )),
    StringField('DefaultDepartment',
                required=0,
                vocabulary_display_path_bound=sys.maxint,
                vocabulary='_defaultDepsVoc',
                widget=SelectionWidget(
                    visible=True,
                    format='select',
                    label=_("Default Department"),
                    description=_("Default Department"),
                )),
))

schema['JobTitle'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
schema['Department'].required = 0
schema['Department'].widget.visible = False


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
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    def getDepartments_voc(self):
        """
        Returns a vocabulary object with the available departments.
        """
        bsc = getToolByName(self, 'portal_catalog')
        items = [(o.UID, o.Title) for o in
                 bsc(portal_type='Department',
                     inactive_state='active')]
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
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(o.UID, o.Title) for o in
                 bsc(portal_type='Department',
                     inactive_state='active')]
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


atapi.registerType(LabContact, PROJECTNAME)
