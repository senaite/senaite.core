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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Acquisition import aq_get
from bika.lims import bikaMessageFactory as _
from bika.lims.api import is_active
from bika.lims.utils import t
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.utils import to_utf8
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from pkg_resources import resource_filename
from plone.resource.utils import iterDirectoriesOfType
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getAdapters
from zope.site.hooks import getSite

import os
import glob


class CatalogVocabulary(object):
    """Make vocabulary from catalog query.

    """
    implements(IDisplayListVocabulary)

    catalog = 'portal_catalog'
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
        request = aq_get(site, 'REQUEST', None)
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
        request = aq_get(site, 'REQUEST', None)
        items = []
        wf = site.portal_workflow
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
    filtered to return only types listed as indexed by bika_catalog
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


class SamplePointVocabulary(BikaContentVocabulary):
    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_samplepoints', ],
                                       ['SamplePoint', ])


SamplePointVocabularyFactory = SamplePointVocabulary()


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
        request = aq_get(site, 'REQUEST', None)
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


class AnalysisRequestWorkflowStateVocabulary(object):
    """Vocabulary factory for workflow states.

        >>> from zope.component import queryUtility

        >>> portal = layer['portal']

        >>> name = 'bika.lims.vocabularies.AnalysisRequestWorkflowStates'
        >>> util = queryUtility(IVocabularyFactory, name)

        >>> tool = getToolByName(portal, "portal_workflow")

        >>> states = util(portal)
        >>> states
        <zope.schema.vocabulary.SimpleVocabulary object at ...>

        >>> pub = states.by_token['published']
        >>> pub.title, pub.token, pub.value
        (u'Published', 'published', 'published')
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        portal = getSite()
        wftool = getToolByName(portal, 'portal_workflow', None)
        if wftool is None:
            return SimpleVocabulary([])

        # XXX This is evil. A vocabulary shouldn't be request specific.
        # The sorting should go into a separate widget.

        # we get REQUEST from wftool because context may be an adapter
        request = aq_get(wftool, 'REQUEST', None)

        wf = wftool.getWorkflowById('bika_ar_workflow')
        items = wftool.listWFStatesByTitle(filter_similar=True)
        items_dict = dict([(i[1], t(i[0])) for i in items])
        items_list = [(k, v) for k, v in items_dict.items()]
        items_list.sort(lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(k, title=u'%s' % v) for k, v in items_list]
        return SimpleVocabulary(terms)


AnalysisRequestWorkflowStateVocabularyFactory = \
    AnalysisRequestWorkflowStateVocabulary()


def getTemplates(bikalims_path, restype, filter_by_type=False):
    """ Returns an array with the Templates available in the Bika LIMS path
        specified plus the templates from the resources directory specified and
        available on each additional product (restype).

        Each array item is a dictionary with the following structure:
            {'id': <template_id>,
             'title': <template_title>}

        If the template lives outside the bika.lims add-on, both the template_id
        and template_title include a prefix that matches with the add-on
        identifier. template_title is the same name as the id, but with
        whitespaces and without extension.

        As an example, for a template from the my.product add-on located in
        <restype> resource dir, and with a filename "My_cool_report.pt", the
        dictionary will look like:
            {'id': 'my.product:My_cool_report.pt',
             'title': 'my.product: My cool report'}

        :param bikalims_path: the path inside bika lims to find the stickers.
        :type bikalims_path: an string as a path
        :param restype: the resource directory type to search for inside
            an addon.
        :type restype: string
        :param filter_by_type: the folder name to look for inside the
        templates path
        :type filter_by_type: string/boolean
    """
    # Retrieve the templates from bika.lims add-on
    templates_dir = resource_filename("bika.lims", bikalims_path)
    tempath = os.path.join(templates_dir, '*.pt')
    templates = [os.path.split(x)[-1] for x in glob.glob(tempath)]

    # Retrieve the templates from other add-ons
    for templates_resource in iterDirectoriesOfType(restype):
        prefix = templates_resource.__name__
        if prefix == 'bika.lims':
            continue
        directory = templates_resource.directory
        # Only use the directory asked in 'filter_by_type'
        if filter_by_type:
            directory = directory + '/' + filter_by_type
        if os.path.isdir(directory):
            dirlist = os.listdir(directory)
            exts = ['{0}:{1}'.format(prefix, tpl) for tpl in dirlist if
                    tpl.endswith('.pt')]
            templates.extend(exts)

    out = []
    templates.sort()
    for template in templates:
        title = template[:-3]
        title = title.replace('_', ' ')
        title = title.replace(':', ': ')
        out.append({'id': template,
                    'title': title})

    return out


def getStickerTemplates(filter_by_type=False):
    """ Returns an array with the sticker templates available. Retrieves the
        TAL templates saved in templates/stickers folder.

        Each array item is a dictionary with the following structure:
            {'id': <template_id>,
             'title': <template_title>}

        If the template lives outside the bika.lims add-on, both the template_id
        and template_title include a prefix that matches with the add-on
        identifier. template_title is the same name as the id, but with
        whitespaces and without extension.

        As an example, for a template from the my.product add-on located in
        templates/stickers, and with a filename "EAN128_default_small.pt", the
        dictionary will look like:
            {'id': 'my.product:EAN128_default_small.pt',
             'title': 'my.product: EAN128 default small'}
        If filter by type is given in the request, only the templates under
        the path with the type name will be rendered given as vocabulary.
        Example: If filter_by_type=='worksheet', only *.tp files under a
        folder with this name will be displayed.

        :param filter_by_type:
        :type filter_by_type: string/bool.
        :returns: an array with the sticker templates available
    """
    # Retrieve the templates from bika.lims add-on
    # resdirname
    resdirname = 'stickers'
    if filter_by_type:
        bikalims_path = os.path.join(
            "browser", "templates", resdirname, filter_by_type)
    else:
        bikalims_path = os.path.join("browser", "templates", resdirname)
    # getTemplates needs two parameters, the first one is the bikalims path
    # where the stickers will be found. The second one is the resource
    # directory type. This allows us to filter stickers by the type we want.
    return getTemplates(bikalims_path, resdirname, filter_by_type)


class StickerTemplatesVocabulary(object):
    """ Locate all sticker templates
    """
    implements(IVocabularyFactory)

    def __call__(self, context, filter_by_type=False):
        out = [SimpleTerm(x['id'], x['id'], x['title']) for x in
               getStickerTemplates(filter_by_type=filter_by_type)]
        return SimpleVocabulary(out)
