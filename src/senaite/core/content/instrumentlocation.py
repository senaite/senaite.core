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

from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import IInstrumentLocation
from senaite.core.content.base import Item
from bika.lims.interfaces import IDeactivable
from bika.lims import senaiteMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IInstrumentLocationSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            "title_instrumentlocation_title",
            default="Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_instrumentlocation_description",
            default="Description"
        ),
        required=False,
    )


@implementer(IInstrumentLocation, IInstrumentLocationSchema, IDeactivable)
class InstrumentLocation(Item):
    """Holds information about an instrument location
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]
