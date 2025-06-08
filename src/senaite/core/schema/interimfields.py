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

from plone.autoform import directives

from bika.lims import senaiteMessageFactory as _

from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.interfaces import IInterimFields
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


class IInterimField(Interface):

    directives.widget("keyword", style=u"width: 150px!important;")
    keyword = schema.TextLine(
        title=_(
            u"label_interim_keyword",
            default=u"Keyword"
        ),
        required=True,
        default=u""
    )

    directives.widget("title", style=u"width: 150px!important;")
    title = schema.TextLine(
        title=_(
            u"label_interim_title",
            default=u"Field title"
        ),
        required=True,
        default=u""
    )

    directives.widget("value", style=u"width: 150px!important;")
    value = schema.TextLine(
        title=_(
            u"label_interim_default_value",
            default=u"Default value"
        ),
        required=False,
        default=u""
    )

    directives.widget("choices", style=u"width: 150px!important;")
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

    directives.widget("allow_empty", klass="hide-title")
    allow_empty = schema.Bool(
        title=_(
            u"label_interim_allow_empty",
            default=u"Allow empty"
        ),
        required=False,
        default=False
    )

    directives.widget("unit", style=u"width: 50px!important;")
    unit = schema.TextLine(
        title=_(
            u"label_interim_unit",
            default=u"Unit"
        ),
        required=False,
        default=u""
    )

    directives.widget("report", klass="hide-title")
    report = schema.Bool(
        title=_(
            u"label_interim_report",
            default=u"Report"
        ),
        required=False,
        default=False
    )

    directives.widget("hidden", klass="hide-title")
    hidden = schema.Bool(
        title=_(
            u"label_interim_hidden",
            default=u"Hidden"
        ),
        required=False,
        default=False
    )

    directives.widget("apply_wide", klass="hide-title")
    apply_wide = schema.Bool(
        title=_(
            u"label_interim_apply_wide",
            default=u"Apply wide"
        ),
        required=False,
        default=False
    )


@implementer(IInterimFields)
class InterimFields(DataGridField):

    value_type = DataGridRow(schema=IInterimField)

    def __init__(self, **kwargs):
        default = kwargs.get("default")
        kwargs["default"] = default or []
        super(InterimFields, self).__init__(**kwargs)

    def set(self, object, val):
        # replace None values with empty string
        val = [{k: "" if v is None else v for k, v in i.items()} for i in val]
        super(DataGridField, self).set(object, val)

    def get(self, object):
        # https://github.com/senaite/senaite.core/pull/2600
        # currently, all values are returned as unicodes.
        # Shall we convert them to strings?
        # Or use ASCIIField instead of TextLine?
        value = super(DataGridField, self).get(object)
        return value
