# -*- coding:utf-8 -*-
from Acquisition import aq_get
from bika.lims.interfaces import IDisplayListVocabulary
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


class CatalogVocabulary(object):

    """Make vocabulary from catalog query.

    """
    implements(IDisplayListVocabulary)

    catalog = 'portal_catalog'
    contentFilter = {}
    key = 'UID'
    value = 'Title'

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        site = getSite()
        request = aq_get(site, 'REQUEST', None)
        catalog = getToolByName(site, self.catalog)
        if 'inactive_state' in catalog.indexes():
            self.contentFilter['inactive_state'] = 'active'
        if 'cancelled_state' in catalog.indexes():
            self.contentFilter['cancelled_state'] = 'active'
        self.contentFilter.update(**kwargs)
        objects = (b.getObject() for b in catalog(self.contentFilter))

        items = []
        for obj in objects:
            key = obj[self.key]
            key = callable(key) and key() or key
            value = obj[self.value]
            value = callable(value) and value() or value
            items.append((key,
                         translate(safe_unicode(value), context=request)))

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
                objects = [o for o in objects if
                           wf.getInfoFor(o, 'inactive_state') == 'active']
                if not objects:
                    continue
                objects.sort(lambda x, y: cmp(x.Title().lower(),
                                              y.Title().lower()))
                xitems = [(translate(safe_unicode(item.Title()),
                                     context=request),
                           item.Title())
                          for item in objects]
                xitems = [SimpleTerm(i[1], i[1], i[0]) for i in xitems]
                items += xitems
        return SimpleVocabulary(items)


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

    >>> folder.invokeFactory('AnalysisCategory', id='obj1', title='O One')
    'obj1'
    >>> folder.obj1.processForm()
    >>> folder.invokeFactory('AnalysisCategory', id='obj2', title='O Two')
    'obj2'
    >>> folder.obj2.processForm()

    >>> objects = folder.objectValues()
    >>> len(objects)
    5

    >>> source = util(portal)
    >>> source
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'O One' in source.by_token
    True
    >>> 'O Two' in source.by_token
    True
    """

    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_analysiscategories',
                                        ],
                                       ['AnalysisCategory', ])

AnalysisCategoryVocabularyFactory = AnalysisCategoryVocabulary()


class AnalysisProfileVocabulary(BikaContentVocabulary):

    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_analysisprofiles', ],
                                       ['AnalysisProfile', ])

AnalysisProfileVocabularyFactory = AnalysisProfileVocabulary()


class SamplePointVocabulary(BikaContentVocabulary):

    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_samplepoints', ],
                                       ['SamplePoint', ])

SamplePointVocabularyFactory = SamplePointVocabulary()


class SampleTypeVocabulary(BikaContentVocabulary):

    def __init__(self):
        BikaContentVocabulary.__init__(self,
                                       ['bika_setup/bika_sampletypes', ],
                                       ['SampleType', ])

SampleTypeVocabularyFactory = SampleTypeVocabulary()


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
            xitems = [(translate(safe_unicode(item.getFullname()),
                                 context=request),
                       item.getFullname())
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

        items = wftool.listWFStatesByTitle(filter_similar=True)
        items_dict = dict([(i[1], translate(i[0], context=request))
                          for i in items])
        items_list = [(k, v) for k, v in items_dict.items()]
        items_list.sort(lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(k, title=u'%s' % v) for k, v in items_list]
        return SimpleVocabulary(terms)

AnalysisRequestWorkflowStateVocabularyFactory = \
    AnalysisRequestWorkflowStateVocabulary()
