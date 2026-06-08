# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.supermodel import model
from senaite.core.schema.datetimefield import DatetimeField
from zope import schema

# Permissions
PERM_EDIT_RESULT = "senaite.core.permissions.FieldEditAnalysisResult"
PERM_EDIT_HIDDEN = "senaite.core.permissions.FieldEditAnalysisHidden"
PERM_EDIT_REMARKS = "senaite.core.permissions.FieldEditAnalysisRemarks"

# Vocabulary base path
VOCAB_PREFIX = "senaite.core.vocabularies.analysis"
VOCAB_METHODS = "{}.methods".format(VOCAB_PREFIX)
VOCAB_INSTRUMENTS = "{}.instruments".format(VOCAB_PREFIX)
VOCAB_ANALYSTS = "{}.analysts".format(VOCAB_PREFIX)
VOCAB_UNITS = "{}.units".format(VOCAB_PREFIX)
VOCAB_DL_OPERANDS = "{}.dl_operands".format(VOCAB_PREFIX)


class IEditAnalysisSchema(model.Schema):
    """Schema for the Edit Analysis modal form.

    Fields use directives.write_permission so that
    plone.autoform auto-omits fields the user cannot write.
    """

    directives.write_permission(
        result=PERM_EDIT_RESULT
    )
    result = schema.TextLine(
        title=_(u"Result"),
        required=False,
    )

    directives.write_permission(
        uncertainty=PERM_EDIT_RESULT
    )
    uncertainty = schema.TextLine(
        title=_(u"Uncertainty"),
        required=False,
    )

    directives.write_permission(
        method=PERM_EDIT_RESULT
    )
    method = schema.Choice(
        title=_(u"Method"),
        vocabulary=VOCAB_METHODS,
        required=False,
    )

    directives.write_permission(
        instrument=PERM_EDIT_RESULT
    )
    instrument = schema.Choice(
        title=_(u"Instrument"),
        vocabulary=VOCAB_INSTRUMENTS,
        required=False,
    )

    directives.write_permission(
        analyst=PERM_EDIT_RESULT
    )
    analyst = schema.Choice(
        title=_(u"Analyst"),
        vocabulary=VOCAB_ANALYSTS,
        required=False,
    )

    directives.write_permission(
        unit=PERM_EDIT_RESULT
    )
    unit = schema.Choice(
        title=_(u"Unit"),
        vocabulary=VOCAB_UNITS,
        required=False,
    )

    directives.write_permission(
        detection_limit_operand=PERM_EDIT_RESULT
    )
    detection_limit_operand = schema.Choice(
        title=_(u"Detection Limit"),
        vocabulary=VOCAB_DL_OPERANDS,
        required=False,
    )

    directives.write_permission(
        hidden=PERM_EDIT_HIDDEN
    )
    hidden = schema.Bool(
        title=_(u"Hidden from report"),
        required=False,
    )

    directives.write_permission(
        remarks=PERM_EDIT_REMARKS
    )
    remarks = schema.Text(
        title=_(u"Remarks"),
        required=False,
    )

    directives.write_permission(
        result_capture_date=PERM_EDIT_RESULT
    )
    result_capture_date = DatetimeField(
        title=_(u"Result Capture Date"),
        required=False,
    )
