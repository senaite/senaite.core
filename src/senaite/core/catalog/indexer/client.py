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

    # remove duplicates and filter out emtpies
    tokens = filter(None, set(tokens))

    # return a single unicode string with all the concatenated tokens
    return u" ".join(map(api.safe_unicode, tokens))
