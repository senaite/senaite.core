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
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.interfaces import IInterimsField
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


DEFAULT_EMPTY_INTERIM_ROW = {
    "keyword": u"",
    "title": u"",
    "value": u"",
    "choices": u"",
    "result_type": "numeric",
    "allow_empty": False,
    "unit": u"",
    "report": False,
    "hidden": False,
    "apply_wide": False,
}


class IInterimRow(Interface):

    keyword = schema.TextLine(
        title=_(
            u"label_interim_keyword",
            default=u"Keyword"
        ),
        required=False,
        default=u""
    )

    title = schema.TextLine(
        title=_(
            u"label_interim_title",
            default=u"Field title"
        ),
        required=False,
        default=u""
    )

    value = schema.TextLine(
        title=_(
            u"label_interim_default_value",
            default=u"Default value"
        ),
        required=False,
        default=u""
    )

    choices = schema.TextLine(
        title=_(
            u"label_interim_choices",
            default=u"Choices"
        ),
        required=False,
        default=u""
    )

    result_type = schema.Choice(
        title=_(
            u"label_interim_result_type",
            default=u"Result type"
        ),
        source="senaite.core.vocabularies.resulttypes",
        default="numeric",
        required=False,
    )

    allow_empty = schema.Bool(
        title=_(
            u"label_interim_allow_empty",
            default=u"Allow empty"
        ),
        required=False,
        default=False
    )

    unit = schema.TextLine(
        title=_(
            u"label_interim_unit",
            default=u"Unit"
        ),
        required=False,
        default=u""
    )

    report = schema.Bool(
        title=_(
            u"label_interim_report",
            default=u"Report"
        ),
        required=False,
        default=False
    )

    hidden = schema.Bool(
        title=_(
            u"label_interim_hidden",
            default=u"Hidden"
        ),
        required=False,
        default=False
    )

    apply_wide = schema.Bool(
        title=_(
            u"label_interim_apply_wide",
            default=u"Apply wide"
        ),
        required=False,
        default=False
    )


@implementer(IInterimsField)
class InterimsField(DataGridField):

    value_type = DataGridRow(schema=IInterimRow)

    def __init__(self, **kwargs):
        default = kwargs.get("default")
        kwargs["default"] = default or [DEFAULT_EMPTY_INTERIM_ROW]
        super(InterimsField, self).__init__(**kwargs)
