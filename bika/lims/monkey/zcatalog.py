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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING


def searchResults(self, REQUEST=None, used=None, **kw):
    """Search the catalog

    Search terms can be passed in the REQUEST or as keyword
    arguments.

    The used argument is now deprecated and ignored
    """
    if REQUEST and REQUEST.get('getRequestUID') \
            and self.id == CATALOG_ANALYSIS_LISTING:

        # Fetch all analyses that have the request UID passed in as an ancestor,
        # cause we want for Samples to always return the contained analyses plus
        # those contained in partitions
        request = REQUEST.copy()
        orig_uid = request.get('getRequestUID')

        # Get all analyses, those from descendant ARs included
        del request['getRequestUID']
        request['getAncestorsUIDs'] = orig_uid
        return self.searchResults(REQUEST=request, used=used, **kw)

    # Normal search
    return self._catalog.searchResults(REQUEST, used, **kw)
