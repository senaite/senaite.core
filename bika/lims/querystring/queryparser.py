"""Allow plone.app.querystring/queryparser.py to accept catalog_name
"""

from collections import namedtuple
import logging

from Acquisition import aq_parent
from DateTime import DateTime
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.dottedname.resolve import resolve

logger = logging.getLogger('bika.lims.querystring')

Row = namedtuple('Row', ['index', 'operator', 'values'])


def parseFormquery(context, formquery, sort_on=None, sort_order=None,
                   catalog_name='portal_catalog', **kwargs):
    if not formquery:
        return {}
    reg = getUtility(IRegistry)

    # Make sure the things in formquery are dictionaries
    formquery = map(dict, formquery)

    query = {}
    for row in formquery:
        operator = row.get('o', None)
        function_path = reg["%s.operation" % operator]

        # The functions expect this pattern of object, so lets give it to
        # them in a named tuple instead of jamming things onto the request
        row = Row(index=row.get('i', None),
                  operator=function_path,
                  values=row.get('v', None))

        kwargs = {}
        parser = resolve(row.operator)
        kwargs = parser(context, row)
        query.update(kwargs)

    if not query:
        # If the query is empty fall back onto the equality query
        query = _equal(context, row)

    # Check for valid indexes
    catalog = getToolByName(context, catalog_name)
    valid_indexes = [index for index in query if index in catalog.indexes()]

    # We'll ignore any invalid index, but will return an empty set if none of
    # the indexes are valid.
    if not valid_indexes:
        logger.warning(
            "Using empty query because there are no valid indexes used.")
        return {}

    # Add sorting (sort_on and sort_order) to the query
    if sort_on:
        query['sort_on'] = sort_on
    if sort_order:
        query['sort_order'] = sort_order

    # And also, add whatever kwargs have been passed - some querybuilder
    # may want to add defaults here.
    query.update(kwargs)

    return query
