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

from collective.z3cform.datagridfield.interfaces import IDataGridField
from z3c.form.interfaces import IObjectWidget
from z3c.form.interfaces import IWidget


class IUIDReferenceWidget(IWidget):
    """UID reference field widget
    """


class INumberWidget(IWidget):
    """Input type "number" widget
    """


class IDataGridWidget(IDataGridField):
    """Datagrid widget (table)
    """


class IDataGridRowWidget(IObjectWidget):
    """Datagrid row widget (table rows)
    """


class IDatetimeWidget(IObjectWidget):
    """Date and time widget
    """


class IAddressWidget(IObjectWidget):
    """Address widget for multiple addresses
    """


class IPhoneWidget(IWidget):
    """Input type "phone" widget
    """


class IQuerySelectWidget(IWidget):
    """Allows to search and select a value
    """


class ICoordinateWidget(IWidget):
    """Allows to set a coordinate in degrees, minutes, seconds and bearing
    """


class IGPSCoordinatesWidget(IWidget):
    """Allows to set GPS Coordinates with latitude and longitude
    """


class IDurationWidget(IWidget):
    """Allows to set a duration period in days, hours and minutes
    """


class IListingWidget(IWidget):
    """Listing view widget
    """


class ISelectOtherWidget(IWidget):
    """Allows to select a pre-populated option from a select element along with
    manual introduction when the built-in option 'Other' is selected
    """
