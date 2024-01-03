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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IListingSearchableTextProvider
from bika.lims.interfaces import IWorksheet
from plone.indexer import indexer
from senaite.core import logger
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.interfaces import IWorksheetCatalog
from zope.component import getAdapters


@indexer(IWorksheet, IWorksheetCatalog)
def listing_searchable_text(instance):
    """Retrieves most commonly searched values for worksheets

    :returns: string with search terms
    """
    tokens = [
        api.get_id(instance),
        instance.getAnalyst(),
        instance.getWorksheetTemplate(),
        instance.getInstrument(),
        instance.getMethod(),
    ]

    # extend via adapters
    catalog = api.get_tool(WORKSHEET_CATALOG)
    adapters = getAdapters((instance, api.get_request(), catalog),
                            IListingSearchableTextProvider)
    for name, adapter in adapters:
        try:
            value = adapter()
        except (AttributeError, TypeError, api.APIError) as exc:
            logger.error(exc)
            value = []
        if not isinstance(value, (list, tuple)):
            value = [value]
        tokens.extend(value)

    # convert to safe unicode
    tokens = map(api.to_searchable_text_metadata, set(tokens))

    # remove empties
    tokens = filter(None, tokens)

    return u" ".join(map(api.safe_unicode, tokens))
