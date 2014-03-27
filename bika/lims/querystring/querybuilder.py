
from bika.lims.querystring import queryparser
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring import querybuilder
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView

import json


class ContentListingView(BrowserView):

    """BrowserView for displaying query results"""

    def __call__(self, **kw):
        return self.index(**kw)


class QueryBuilder(querybuilder.QueryBuilder):

    """ This view is used by the javascripts,
    fetching configuration or results.
    In this copy we have catalog_name. """

    contentFilter = {}

    def __init__(self, context, request, catalog_name='portal_catalog'):
        self.context = context
        self.request = request
        self.catalog_name = request.get('catalog_name', catalog_name)
        querybuilder.QueryBuilder.__init__(self, context, request)

    def __call__(self, query, batch=False, b_start=0, b_size=30,
                 sort_on=None, sort_order=None, limit=0, brains=False):
        """If there are results, make the query and return the results"""
        if self._results is None:
            self._results = self._makequery(
                query=query, batch=batch,
                b_start=b_start, b_size=b_size, sort_on=sort_on,
                sort_order=sort_order, limit=limit, brains=brains)
        return self._results

    def html_results(self, query):
        """html results, used for in the edit screen of a collection,
           used in the live update results"""
        options = dict(original_context=self.context)
        results = self(
            query, sort_on=self.request.get('sort_on', None),
            sort_order=self.request.get('sort_order', None),
            limit=10)
        return getMultiAdapter((results, self.request),
                               name='display_query_results')(**options)

    def _makequery(self, query=None, batch=False, b_start=0, b_size=30,
                   sort_on=None, sort_order=None, limit=0, brains=False):
        """Parse the (form)query and return using multi-adapter"""
        parsedquery = queryparser.parseFormquery(
            self.context, query, sort_on, sort_order,
            catalog_name=self.catalog_name,
            kwargs=self.contentFilter)

        if not parsedquery:
            if brains:
                return []
            else:
                return IContentListing([])

        catalog = getToolByName(self.context, self.catalog_name)
        if batch:
            parsedquery['b_start'] = b_start
            parsedquery['b_size'] = b_size
        elif limit:
            parsedquery['sort_limit'] = limit

        if 'path' not in parsedquery:
            parsedquery['path'] = {'query': ''}
        parsedquery['path']['query'] = getNavigationRoot(self.context) + \
            parsedquery['path']['query']

        results = catalog(parsedquery)
        if not brains:
            results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results


class RegistryConfiguration(BrowserView):

    """Combine default operations from plone.app.query, with
    fields from registry key in prefix
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog_name = self.request.get('catalog_name', 'portal_catalog')
        self.prefix = "bika.lims.%s_query" % self.catalog_name

    def __call__(self):
        """Return the registry configuration in JSON format"""
        registry = getUtility(IRegistry)
        # First grab the base config, so we can use the operations
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "plone.app.querystring.operation"
        op_config = registryreader.parseRegistry()
        # Then combine our fields
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = self.prefix
        config = registryreader.parseRegistry()
        config = registryreader.getVocabularyValues(config)
        config.update(op_config)
        registryreader.mapOperations(config)
        registryreader.mapSortableIndexes(config)
        config = {
            'indexes': config.get(self.prefix + '.field'),
            'sortable_indexes': config.get('sortable'),
        }
        return json.dumps(config)
