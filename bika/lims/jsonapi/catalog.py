# -*- coding: utf-8 -*-

from zope import interface

from DateTime import DateTime
from ZPublisher import HTTPRequest

from bika.lims import logger
from bika.lims import api as bikaapi
from bika.lims.jsonapi import api
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as _
from bika.lims.jsonapi.interfaces import ICatalog
from bika.lims.jsonapi.interfaces import ICatalogQuery


class Catalog(object):
    """Plone catalog adapter
    """
    interface.implements(ICatalog)

    def __init__(self, context):
        self._catalog = api.get_tool("portal_catalog")
        self._bika_catalog = api.get_tool("bika_catalog")
        self._bika_analysis_catalog = api.get_tool("bika_analysis_catalog")
        self._bika_setup_catalog = api.get_tool("bika_setup_catalog")

        self._catalogs = {
            "portal_catalog": self._catalog,
            "bika_catalog": self._bika_catalog,
            "bika_analysis_catalog": self._bika_analysis_catalog,
            "bika_setup_catalog": self._bika_setup_catalog,
        }

    def search(self, query):
        """search the catalog
        """
        logger.info("Catalog query={}".format(query))

        # Support to set the catalog as a request parameter
        catalogs = _.to_list(req.get("catalog", None))
        if catalogs:
            return bikaapi.search(query, catalog=catalogs)
        # Delegate to the search API of Bika LIMS
        return bikaapi.search(query)

    def __call__(self, query):
        return self.search(query)

    def get_catalog(self, name="portal_catalog"):
        return self._catalogs[name]

    def get_schema(self):
        catalog = self.get_catalog()
        return catalog.schema()

    def get_indexes(self):
        """get all indexes managed by this catalog

        TODO: Combine indexes of relevant catalogs depending on the portal_type
        which is searched for.
        """
        catalog = self.get_catalog()
        return catalog.indexes()

    def get_index(self, name):
        """get an index by name

        TODO: Combine indexes of relevant catalogs depending on the portal_type
        which is searched for.
        """
        catalog = self.get_catalog()
        index = catalog._catalog.getIndex(name)
        logger.debug("get_index={} of catalog '{}' --> {}".format(
            name, catalog.__name__, index))
        return index

    def to_index_value(self, value, index):
        """Convert the value for a given index
        """

        # ZPublisher records can be passed to the catalog as is.
        if isinstance(value, HTTPRequest.record):
            return value

        if isinstance(index, basestring):
            index = self.get_index(index)

        if index.id == "portal_type":
            return filter(lambda x: x, _.to_list(value))
        if index.meta_type == "DateIndex":
            return DateTime(value)
        if index.meta_type == "BooleanIndex":
            return bool(value)
        if index.meta_type == "KeywordIndex":
            return value.split(",")

        return value


class CatalogQuery(object):
    """Catalog query adapter
    """
    interface.implements(ICatalogQuery)

    def __init__(self, catalog):
        self.catalog = catalog

    def make_query(self, **kw):
        """create a query suitable for the catalog
        """
        query = kw.pop("query", {})

        query.update(self.get_request_query())
        query.update(self.get_custom_query())
        query.update(self.get_keyword_query(**kw))

        sort_on, sort_order = self.get_sort_spec()
        if sort_on and "sort_on" not in query:
            query.update({"sort_on": sort_on})
        if sort_order and "sort_order" not in query:
            query.update({"sort_order": sort_order})

        logger.info("make_query:: query={} | catalog={}".format(
            query, self.catalog))

        return query

    def get_request_query(self):
        """Checks the request for known catalog indexes and converts the values
        to fit the type of the catalog index.

        :param catalog: The catalog to build the query for
        :type catalog: ZCatalog
        :returns: Catalog query
        :rtype: dict
        """
        query = {}

        # only known indexes get observed
        indexes = self.catalog.get_indexes()

        for index in indexes:
            # Check if the request contains a parameter named like the index
            value = req.get(index)
            # No value found, continue
            if value is None:
                continue
            # Convert the found value to format understandable by the index
            index_value = self.catalog.to_index_value(value, index)
            # Conversion returned None, continue
            if index_value is None:
                continue
            # Append the found value to the query
            query[index] = index_value

        return query

    def get_custom_query(self):
        """Extracts custom query keys from the index.

        Parameters which get extracted from the request:

            `q`: Passes the value to the `SearchableText`
            `path`: Creates a path query
            `recent_created`: Creates a date query
            `recent_modified`: Creates a date query

        :param catalog: The catalog to build the query for
        :type catalog: ZCatalog
        :returns: Catalog query
        :rtype: dict
        """
        query = {}

        # searchable text queries
        q = req.get_query()
        if q:
            query["SearchableText"] = q

        # physical path queries
        path = req.get_path()
        if path:
            query["path"] = {'query': path, 'depth': req.get_depth()}

        # special handling for recent created/modified
        recent_created = req.get_recent_created()
        if recent_created:
            date = api.calculate_delta_date(recent_created)
            query["created"] = {'query': date, 'range': 'min'}

        recent_modified = req.get_recent_modified()
        if recent_modified:
            date = api.calculate_delta_date(recent_modified)
            query["modified"] = {'query': date, 'range': 'min'}

        return query

    def get_keyword_query(self, **kw):
        """Generates a query from the given keywords.
        Only known indexes make it into the generated query.

        :returns: Catalog query
        :rtype: dict
        """
        query = dict()

        # Only known indexes get observed
        indexes = self.catalog.get_indexes()

        # Handle additional keyword parameters
        for k, v in kw.iteritems():
            # handle uid in keywords
            if k.lower() == "uid":
                k = "UID"
            # handle portal_type in keywords
            if k.lower() == "portal_type":
                if v:
                    v = _.to_list(v)
            if k not in indexes:
                logger.warn("Skipping unknown keyword parameter '%s=%s'" % (k, v))
                continue
            if v is None:
                logger.warn("Skip None value in kw parameter '%s=%s'" % (k, v))
                continue
            logger.debug("Adding '%s=%s' to query" % (k, v))
            query[k] = v

        return query

    def get_sort_spec(self):
        """Build sort specification
        """
        all_indexes = self.catalog.get_indexes()
        si = req.get_sort_on(allowed_indexes=all_indexes)
        so = req.get_sort_order()
        return si, so
