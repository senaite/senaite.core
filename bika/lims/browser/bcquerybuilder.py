"""Some parts of p.a.querystring and archetypes.querywidget are duplicated
in bika.lims, until they are patched upstream.  This version of QueryBuilder
allows a catalog_name to be specified.
"""

from bika.lims.browser import queryparser
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring import querybuilder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView


class BCQueryBuilder(querybuilder.QueryBuilder):
    """ This view is used by the javascripts,
        fetching configuration or results."""

    catalog_name = 'bika_catalog'

    def __init__(self, context, request):
        super(BCQueryBuilder, self).__init__(context, request)

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
            self.context, query, sort_on, sort_order)

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
