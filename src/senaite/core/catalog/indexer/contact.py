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
from bika.lims.interfaces import IContact
from bika.lims.interfaces import ILabContact
from bika.lims.interfaces import ISupplierContact
from plone.indexer import indexer
from senaite.core.interfaces.catalog import IContactCatalog


@indexer(IContact, IContactCatalog)
@indexer(ILabContact, IContactCatalog)
@indexer(ISupplierContact, IContactCatalog)
def sortable_title(instance):
    return instance.getFullname().lower()


@indexer(IContact, IContactCatalog)
@indexer(ILabContact, IContactCatalog)
@indexer(ISupplierContact, IContactCatalog)
def getParentUID(instance):
    parent = instance.aq_parent
    if not IClient.providedBy(parent):
        return None
    return parent.UID()


@indexer(IContact, IContactCatalog)
@indexer(ILabContact, IContactCatalog)
@indexer(ISupplierContact, IContactCatalog)
def listing_searchable_text(instance):
    """Extract search tokens for ZC text index
    """

    tokens = [
        instance.getBusinessPhone(),
        instance.getCity(),
        instance.getCountry(),
        instance.getEmailAddress(),
        instance.getFullname(),
        instance.getHomePhone(),
        instance.getJobTitle(),
        instance.getMobilePhone(),
        instance.getUsername(),
    ]

    department = instance.getDepartment()  # part of person base class
    if isinstance(department, list):  # override in labcontact
        department_titles = map(api.get_title, department)
        tokens.extend(department_titles)
    elif api.is_string(department):
        tokens.append(department)

    # remove duplicates and filter out emtpies
    tokens = filter(None, set(tokens))

    # return a single unicode string with all the concatenated tokens
    return u" ".join(map(api.safe_unicode, tokens))
