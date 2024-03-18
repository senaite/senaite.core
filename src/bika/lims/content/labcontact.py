# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.contact import Contact
from bika.lims.content.person import Person
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import ILabContact
from Products.Archetypes import atapi
from Products.Archetypes.Field import ImageField
from Products.Archetypes.Field import ImageWidget
from Products.Archetypes.public import registerType
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import SelectionWidget
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from zope.interface import implements

schema = Person.schema.copy() + atapi.Schema((

    ImageField(
        "Signature",
        widget=ImageWidget(
            label=_("Signature"),
            description=_(
                "Upload a scanned signature to be used on printed "
                "analysis results reports. Ideal size is 250 pixels "
                "wide by 150 high"),
        ),
    ),

    UIDReferenceField(
        "Departments",
        multiValued=1,
        allowed_types=("Department",),
        widget=ReferenceWidget(
            label=_(
                "label_labcontact_departments",
                default="Departments"),
            description=_(
                "description_labcontact_departments",
                default="Assigned laboratory departments"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        ),
    ),

    # NOTE: This field is dynamically modified by
    #       `senaite.core.browser.form.adapters.labcontact.EditForm`
    #
    #       Please leave it as a `SelectionWidget` to allow selection only from
    #       the dependent selected departments field!
    UIDReferenceField(
        "DefaultDepartment",
        allowed_types=("Department",),
        vocabulary="default_department_vocabulary",
        accessor="getRawDefaultDepartment",
        widget=SelectionWidget(
            format="select",
            label=_(
                "label_labcontact_default_department",
                default="Default Department"),
            description=_(
                "description_labcontact_default_department",
                default="Select a default department for this contact "
                        "from one of the selected departments."),
        ),
    ),
))

schema["JobTitle"].schemata = "default"
# Don't make title required - it will be computed from the Person's Fullname
schema["title"].required = 0
schema["title"].widget.visible = False
schema["Department"].required = 0
schema["Department"].widget.visible = False


class LabContact(Contact):
    """A Lab Contact, which can be linked to a System User
    """
    implements(ILabContact, IHaveDepartment, IDeactivable)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the contact's Fullname as title
        """
        return safe_unicode(self.getFullname()).encode("utf-8")

    @security.public
    def getDepartment(self):
        """Required by IHaveDepartment. Returns the list of departments this
        laboratory contact is assigned to plus the default department
        """
        departments = self.getDepartments() + [self.getDefaultDepartment()]
        return filter(None, list(set(departments)))

    @security.public
    def getDefaultDepartment(self):
        """Returns the assigned default department

        :returns: Department object
        """
        return self.getField("DefaultDepartment").get(self)

    @security.public
    def getRawDefaultDepartment(self):
        """Returns the UID of the assigned default department

        NOTE: This is the default accessor of the `DefaultDepartment` schema
        field and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Default Department UID
        """
        field = self.getField("DefaultDepartment")
        return field.getRaw(self)

    def default_department_vocabulary(self):
        """Returns only selected departments
        """
        # Getting the assigned departments
        deps = self.getDepartments()
        items = []
        for d in deps:
            items.append((api.get_uid(d), api.get_title(d)))
        return api.to_display_list(items, sort_by="value", allow_empty=True)

    def hasUser(self):
        """Check if contact has user
        """
        username = self.getUsername()
        if not username:
            return False
        user = api.get_user(username)
        return user is not None

    def addDepartment(self, dep):
        """Adds a department

        :param dep: UID or department object
        :returns: True when the department was added
        """
        if api.is_uid(dep):
            dep = api.get_object_by_uid(dep)
        deps = self.getDepartments()
        if dep not in deps:
            return False
        deps.append(dep)
        self.setDepartments(deps)
        return True

    def removeDepartment(self, dep):
        """Removes a department

        :param dep: UID or department object
        :returns: True when the department was removed
        """
        if api.is_uid(dep):
            dep = api.get_object_by_uid(dep)
        deps = self.getDepartments()
        if dep not in deps:
            return False
        deps.remove(dep)
        self.setDepartments(deps)
        return True


registerType(LabContact, PROJECTNAME)
