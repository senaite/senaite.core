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

from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IManufacturer
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IManufacturerSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_manufacturer_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_manufacturer_description",
            default=u"Description"
        ),
        required=False,
    )


@implementer(IManufacturer, IManufacturerSchema, IDeactivable)
class Manufacturer(Container):
    """A container for manufacturer
    """
    _catalogs = [SETUP_CATALOG]
