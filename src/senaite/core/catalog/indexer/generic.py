# -*- coding: utf-8 -*-

from bika.lims import api
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.CatalogTool import \
    sortable_title as plone_sortable_title
from Products.CMFPlone.utils import safe_callable
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.interfaces import ISenaiteCatalog
from senaite.core.catalog.utils import get_searchable_text_tokens


@indexer(IContentish)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.is_active(instance)


@indexer(IContentish)
def sortable_title(instance):
    """Uses the default Plone sortable_text index lower-case
    """
    title = plone_sortable_title(instance)
    if safe_callable(title):
        title = title()
    return title.lower()


@indexer(IContentish, ISenaiteCatalog)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    tokens = get_searchable_text_tokens(instance, SENAITE_CATALOG)
    return u" ".join(tokens)
