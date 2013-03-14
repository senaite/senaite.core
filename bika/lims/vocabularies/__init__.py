# -*- coding:utf-8 -*-
from Acquisition import aq_get
from bika.lims.interfaces import IDisplayListVocabulary
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implements
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
