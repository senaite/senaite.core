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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import bikaMessageFactory as _
from bika.lims.api import is_active
from senaite.core.i18n import translate as t
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.utils import to_utf8
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from senaite.core.p3compat import cmp
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


class CatalogVocabulary(object):
    """Make vocabulary from catalog query.

    """
    implements(IDisplayListVocabulary)

    catalog = 'uid_catalog'
    contentFilter = {}
    key = 'UID'
    value = 'Title'

    def __init__(self, context, key=None, value=None, contentFilter=None):
        self.context = context
        self.key = key if key else self.key
        self.value = value if value else self.value
        self.contentFilter = \
            contentFilter if contentFilter else self.contentFilter

    def __call__(self, **kwargs):
        site = getSite()
        catalog = getToolByName(site, self.catalog)
        allow_blank = False
        if 'allow_blank' in kwargs:
            allow_blank = kwargs.get('allow_blank')
            del (kwargs['allow_blank'])

        self.contentFilter.update(**kwargs)

        # If a secondary deactivation/cancellation workflow is anbled,
        # Be sure and select only active objects, unless other instructions
        # are explicitly specified:
        if "is_active" not in self.contentFilter:
            self.contentFilter["is_active"] = True

        brains = catalog(self.contentFilter)

        items = [('', '')] if allow_blank else []
        for brain in brains:
            if self.key in brain and self.value in brain:
                key = getattr(brain, self.key)
                value = getattr(brain, self.value)
            else:
                obj = brain.getObjec()
                key = obj[self.key]
                key = callable(key) and key() or key
                value = obj[self.value]
                value = callable(value) and value() or value
            items.append((key, t(value)))

        return DisplayList(items)


class BikaContentVocabulary(object):
    """Vocabulary factory for Bika Setup objects.  We find them by listing
    folder contents directly.
    """
    implements(IVocabularyFactory)

    def __init__(self, folders, portal_types):
        self.folders = isinstance(folders, (tuple, list)) and \
                       folders or [folders, ]
        self.portal_types = isinstance(portal_types, (tuple, list)) and \
                            portal_types or [portal_types, ]

    def __call__(self, context):
        site = getSite()
        items = []
        for folder in self.folders:
            folder = site.restrictedTraverse(folder)
            for portal_type in self.portal_types:
                objects = list(folder.objectValues(portal_type))
                objects = filter(is_active, objects)
                if not objects:
                    continue
                objects.sort(lambda x, y: cmp(x.Title().lower(),
                                              y.Title().lower()))
                xitems = [(t(item.Title()), item.Title()) for item in objects]
                xitems = [SimpleTerm(i[1], i[1], i[0]) for i in xitems]
                items += xitems
        return SimpleVocabulary(items)


class BikaCatalogTypesVocabulary(object):
    """Vocabulary factory for really user friendly portal types,
    filtered to return only types listed as indexed by senaite_catalog
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        translate = context.translate
        types = (
            ('AnalysisRequest', translate(to_utf8(_('Sample')))),
            ('Batch', translate(to_utf8(_('Batch')))),
            # TODO Remove in >v1.3.0
            ('Sample', translate(to_utf8(_('Sample')))),
            ('ReferenceSample', translate(to_utf8(_('Reference Sample')))),
            ('Worksheet', translate(to_utf8(_('Worksheet'))))
        )
        items = [SimpleTerm(i[0], i[0], i[1]) for i in types]
        return SimpleVocabulary(items)


BikaCatalogTypesVocabularyFactory = BikaCatalogTypesVocabulary()


class AnalysisCategoryVocabulary(BikaContentVocabulary):
    """" AnalysisCategories

    >>> portal = layer['portal']

    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import login
    >>> login(portal, TEST_USER_NAME)
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

    >>> from zope.component import queryUtility
    >>> name = 'bika.lims.vocabularies.AnalysisCategories'
    >>> util = queryUtility(IVocabularyFactory, name)
    >>> folder = portal.bika_setup.bika_analysiscategories
    >>> objects = folder.objectValues()
    >>> len(objects)
    3

    >>> source = util(portal)
    >>> source
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'Water Chemistry' in source.by_token
    True
    """

    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_analysiscategories', ],
                                       ['AnalysisCategory', ])


AnalysisCategoryVocabularyFactory = AnalysisCategoryVocabulary()


class AnalysisProfileVocabulary(BikaContentVocabulary):
    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_analysisprofiles', ],
                                       ['AnalysisProfile', ])


AnalysisProfileVocabularyFactory = AnalysisProfileVocabulary()


class StorageLocationVocabulary(BikaContentVocabulary):
    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_storagelocations', ],
                                       ['StorageLocation', ])


StorageLocationVocabularyFactory = StorageLocationVocabulary()


class AnalysisServiceVocabulary(BikaContentVocabulary):
    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_analysisservices', ],
                                       ['AnalysisService', ])


AnalysisServiceVocabularyFactory = AnalysisServiceVocabulary()


class ClientVocabulary(BikaContentVocabulary):
    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['clients', ],
                                       ['Client', ])


ClientVocabularyFactory = ClientVocabulary()


class UserVocabulary(object):
    """ Present a vocabulary containing users in the specified
    list of roles

    >>> from zope.component import queryUtility

    >>> portal = layer['portal']
    >>> name = 'bika.lims.vocabularies.Users'
    >>> util = queryUtility(IVocabularyFactory, name)

    >>> tool = portal.portal_registration
    >>> tool.addMember('user1', 'user1',
    ...     properties = {
    ...         'username': 'user1',
    ...         'email': 'user1@example.com',
    ...         'fullname': 'user1'}
    ... )
    <MemberData at /plone/portal_memberdata/user1 used for /plone/acl_users>

    >>> source = util(portal)
    >>> source
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'test_user_1_' in source.by_value
    True
    >>> 'user1' in source.by_value
    True
    """
    implements(IVocabularyFactory)

    def __init__(self, roles=[]):
        self.roles = roles if isinstance(roles, (tuple, list)) else [roles, ]

    def __call__(self, context):
        site = getSite()
        mtool = getToolByName(site, 'portal_membership')
        users = mtool.searchForMembers(roles=self.roles)
        items = [(item.getProperty('fullname'), item.getId())
                 for item in users]
        items.sort(lambda x, y: cmp(x[0].lower(), y[0].lower()))
        items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
        return SimpleVocabulary(items)


UserVocabularyFactory = UserVocabulary()

ClientVocabularyFactory = ClientVocabulary()


class ClientContactVocabulary(object):
    """ Present Client Contacts

    >>> from zope.component import queryUtility

    >>> portal = layer['portal']
    >>> name = 'bika.lims.vocabularies.ClientContacts'
    >>> util = queryUtility(IVocabularyFactory, name)

    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import login
    >>> login(portal, TEST_USER_NAME)
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

    >>> portal.clients.invokeFactory('Client', id='client1')
    'client1'
    >>> client1 = portal.clients.client1
    >>> client1.processForm()
    >>> client1.invokeFactory('Contact', id='contact1')
    'contact1'
    >>> contact1 = client1.contact1
    >>> contact1.processForm()
    >>> contact1.edit(Firstname='Contact', Surname='One')
    >>> contact1.reindexObject()

    >>> source = util(portal)
    >>> source
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'Contact One' in source.by_value
    True
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        items = []
        for client in site.clients.objectValues('Client'):
            objects = list(client.objectValues('Contact'))
            objects.sort(lambda x, y: cmp(x.getFullname().lower(),
                                          y.getFullname().lower()))
            xitems = [(to_utf8(item.getFullname()), item.getFullname())
                      for item in objects]
            xitems = [SimpleTerm(i[1], i[1], i[0]) for i in xitems]
            items += xitems
        return SimpleVocabulary(items)


ClientContactVocabularyFactory = ClientContactVocabulary()


class AnalystVocabulary(UserVocabulary):
    def __init__(self):
        UserVocabulary.__init__(self, roles=['Analyst', ])


AnalystVocabularyFactory = AnalystVocabulary()
