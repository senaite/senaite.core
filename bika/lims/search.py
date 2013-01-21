# -*- coding: utf-8 -*-
"""
This is code from plone.app.search.browser, modified to
include objects indexed in catalogs other than portal_catalog
"""

import os
from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZCTextIndex.ParseTree import ParseError
from zope.i18nmessageid import MessageFactory
from plone.app.search.browser import Search
from plone.app.search.browser import quote_chars
import plone

_ = MessageFactory('plone')

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
MULTISPACE = u'\u3000'.encode('utf-8')
EVER = DateTime('1970-01-03')


class SearchView(Search):

    catalogs = ['portal_catalog', 'bika_catalog', 'bika_setup_catalog']

    def __init__(self, context, request):
        super(SearchView, self).__init__(self, context, request)
        # Construct template from a file which lies in plone.app.search
        self.index = ViewPageTemplateFile(
            os.path.join(
                os.path.dirname(plone.app.search.__file__),"templates", "search.pt") )

    def results(self, query=None, batch=True, b_size=10, b_start=0):
        """ Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' should be a dictionary of catalog parameters.
        """
        if query is None:
            query = {}
        if batch:
            query['b_start'] = b_start = int(b_start)
            query['b_size'] = b_size
        query = self.filter_query(query)

        results = []
        if query is not None:
            for catalog_name in self.catalogs:
                catalog = getToolByName(self.context, catalog_name)
                try:
                    results = results + list(catalog(**query))
                except ParseError:
                    pass
        if not results:
            return results

        results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def filter_query(self, query):
        request = self.request
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
        if not text:
            # Without text, the only meaningful case is Subject
            subjects = request.form.get('Subject')
            if not subjects:
                return

        valid_keys = self.valid_keys
        for catalog_name in self.catalogs:
            catalog = getToolByName(self.context, catalog_name)
            valid_keys = valid_keys + tuple(catalog.indexes())
        valid_keys = sorted(set(valid_keys))

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):
                query[k] = v
        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        if created:
            if created.get('query'):
                if created['query'][0] <= EVER:
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            query['path'] = getNavigationRoot(self.context)

        return query

    def types_list(self):
        # only show those types that have any content
        used_types = []
        for catalog_name in self.catalogs:
            catalog = getToolByName(self.context, catalog_name)
            used_types = used_types + catalog._catalog.getIndex('portal_type').uniqueValues()
        return self.filter_types(list(used_types))


class UpdatedSearchView(Search):
    def __init__(self, context, request):
        super(UpdatedSearchView, self).__init__(self, context, request)
        # Construct template from a file which lies in plone.app.search
        self.index = ViewPageTemplateFile(
            os.path.join(
                os.path.dirname(plone.app.search.__file__),"templates", "updated_search.pt") )
