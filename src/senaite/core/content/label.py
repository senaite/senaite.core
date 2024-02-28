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
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.api import label as label_api
from senaite.core.interfaces import ILabel
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class ILabelSchema(model.Schema):
    """Schema interface
    """
    title = schema.TextLine(
        title=_(
            u"title_label_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_label_description",
            default=u"Description"
        ),
        required=False,
    )

    @invariant
    def validate_title(data):
        """Checks if the title is unique
        """
        # https://community.plone.org/t/dexterity-unique-field-validation
        context = getattr(data, "__context__", None)
        if context is not None:
            if context.title == data.title:
                # nothing changed
                return
        labels = label_api.list_labels(inactive=True)
        if data.title in labels:
            raise Invalid(_("Label names must be unique"))


@implementer(ILabel, ILabelSchema, IHideActionsMenu)
class Label(Container):
    """A container for labels
    """
    _catalogs = [SETUP_CATALOG]
