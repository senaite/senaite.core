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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IListingSearchableTextProvider
from plone.indexer import indexer
from senaite.core.interfaces.catalog import IClientCatalog
from zope.component import getAdapters
from senaite.core.catalog import CLIENT_CATALOG


@indexer(IClient, IClientCatalog)
def client_searchable_text(instance):
    """Extract search tokens for ZC text index.

    Add-ons can contribute additional tokens by registering a named
    multi-adapter for (IClient, IRequest, IClientCatalog) that provides
    IListingSearchableTextProvider.
    """
    tokens = set([
        instance.getClientID(),
        instance.getName(),
        instance.getPhone(),
        instance.getFax(),
        instance.getEmailAddress(),
        instance.getTaxNumber(),
    ])

    # extend address lines
    tokens.update(instance.getPrintAddress())

    # allow add-ons to contribute additional tokens via named adapters
    catalog = api.get_tool(CLIENT_CATALOG)
    providers = getAdapters(
        (instance, api.get_request(), catalog),
        IListingSearchableTextProvider)
    for name, provider in providers:
        try:
            value = provider()
        except Exception:
            continue
        if isinstance(value, (list, tuple)):
            tokens.update(map(api.safe_unicode, value))
        elif value:
            tokens.add(api.safe_unicode(value))

    tokens = filter(None, tokens)
    return u" ".join(map(api.safe_unicode, tokens))
