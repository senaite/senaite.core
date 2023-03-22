# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IClient
from plone.indexer import indexer
from senaite.core.interfaces.catalog import IClientCatalog


@indexer(IClient, IClientCatalog)
def client_searchable_text(instance):
    """Extract search tokens for ZC text index
    """

    tokens = [
        instance.getClientID(),
        instance.getName(),
        instance.getPhone(),
        instance.getFax(),
        instance.getEmailAddress(),
        instance.getTaxNumber(),
    ]

    # extend address lines
    tokens.extend(instance.getPrintAddress())

    return u" ".join(map(api.safe_unicode, set(tokens)))
