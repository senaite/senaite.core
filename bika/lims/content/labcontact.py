# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""The lab staff
"""
import sys

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from Products.Archetypes import atapi
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import DisplayList

from plone import api
from zope.interface import implements

from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.content.contact import Contact
from bika.lims.interfaces import ILabContact
from bika.lims import logger
from bika.lims import bikaMessageFactory as _


schema = Person.schema.copy() + atapi.Schema((
    atapi.LinesField('PublicationPreference',
                     vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
                     default='email',
                     schemata='Publication preference',
                     widget=atapi.MultiSelectionWidget(
                         label=_("Publication preference"),
                     )),
    atapi.ImageField('Signature',
                     widget=atapi.ImageWidget(
                         label=_("Signature"),
                         description=_(
                             "Upload a scanned signature to be used on printed analysis "
                             "results reports. Ideal size is 250 pixels wide by 150 high"),
                     )),
    atapi.ReferenceField('Department',
                         required=0,
                         vocabulary_display_path_bound=sys.maxint,
                         allowed_types=('Department',),
                         relationship='LabContactDepartment',
                         vocabulary='getDepartments',
                         referenceClass=HoldingReference,
                         widget=atapi.ReferenceWidget(
                             checkbox_bound=0,
                             label=_("Department"),
                             description=_("The laboratory department"),
                         )),
    atapi.ComputedField('DepartmentTitle',
                        expression="context.getDepartment() and context.getDepartment().Title() or ''",
                        widget=atapi.ComputedWidget(
                            visible=False,
                        )),
))

schema['JobTitle'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False


class LabContact(Contact):
    """A Lab Contact, which can be linked to a System User
    """
    implements(ILabContact)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    def Title(self):
        """ Return the contact's Fullname as title """
        return safe_unicode(self.getFullname()).encode('utf-8')

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Department',
                                  inactive_state='active')]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(LabContact, PROJECTNAME)
