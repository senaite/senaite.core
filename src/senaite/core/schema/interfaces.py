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

from collective.z3cform.datagridfield.interfaces import IRow
from plone.app.textfield.interfaces import IRichText
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IInt
from zope.schema.interfaces import IList
from zope.schema.interfaces import INativeString
from zope.schema.interfaces import ITimedelta


class IBaseField(IField):
    """Senaite base field
    """


class IIntField(IInt):
    """Senaite integer field
    """


class IDataGridField(IList):
    """Senaite datagrid field
    """


class IDataGridRow(IRow):
    """Datagrid row
    """


class IUIDReferenceField(IList):
    """Senaite UID reference field
    """


class ICoordinateField(IDict):
    """Senaite Coordinate field
    """


class IDatetimeField(IDatetime):
    """Senaite Datetime field
    """


class IAddressField(IList):
    """Senaite multi-address field
    """


class IRichTextField(IRichText):
    """Senaite rich text field
    """


class IPhoneField(INativeString):
    """Input type "phone" widget
    """


class IDurationField(ITimedelta):
    """Senaite Duration field
    """


class IGPSCoordinatesField(IDict):
    """Senaite GPS Coordinated field
    """


class ISelectOtherField(INativeString):
    """Senaite SelectOther field
    """
