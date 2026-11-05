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

from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IDeactivable
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.content.person import IPersonSchema
from senaite.core.content.person import Person
from senaite.core.interfaces import ISupplierContact
from zope.interface import implementer


@implementer(ISupplierContact, IPersonSchema, IDeactivable)
class SupplierContact(Person):
    """A Contact of a Supplier

    This type adds no fields of its own, the schema of `Person` is the whole
    contract. It only exists so supplier contacts can be told apart from the
    contacts of a client, that carry their own `CCContact` field.
    """

    # Catalogs where this type will be catalogued
    _catalogs = [CONTACT_CATALOG]

    security = ClassSecurityInfo()
