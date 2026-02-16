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
from zope import schema


class IEditAnalysisSchema(model.Schema):
    """Schema for the Edit Analysis modal form.

    Fields use directives.write_permission so that
    plone.autoform auto-omits fields the user cannot write.
    """

    directives.write_permission(
        result="senaite.core.permissions.FieldEditAnalysisResult"
    )
    result = schema.TextLine(
        title=_(u"Result"),
        required=False,
    )

    directives.write_permission(
        uncertainty="senaite.core.permissions.FieldEditAnalysisResult"
    )
    uncertainty = schema.TextLine(
        title=_(u"Uncertainty"),
        required=False,
    )

    directives.write_permission(
        method="senaite.core.permissions.FieldEditAnalysisResult"
    )
    method = schema.Choice(
        title=_(u"Method"),
        vocabulary="senaite.core.vocabularies.analysis.methods",
        required=False,
    )

    directives.write_permission(
        instrument="senaite.core.permissions.FieldEditAnalysisResult"
    )
    instrument = schema.Choice(
        title=_(u"Instrument"),
        vocabulary="senaite.core.vocabularies.analysis.instruments",
        required=False,
    )

    directives.write_permission(
        analyst="senaite.core.permissions.FieldEditAnalysisResult"
    )
    analyst = schema.Choice(
        title=_(u"Analyst"),
        vocabulary="senaite.core.vocabularies.analysis.analysts",
        required=False,
    )

    directives.write_permission(
        unit="senaite.core.permissions.FieldEditAnalysisResult"
    )
    unit = schema.Choice(
        title=_(u"Unit"),
        vocabulary="senaite.core.vocabularies.analysis.units",
        required=False,
    )

    directives.write_permission(
        detection_limit_operand="senaite.core.permissions.FieldEditAnalysisResult"
    )
    detection_limit_operand = schema.Choice(
        title=_(u"Detection Limit"),
        vocabulary="senaite.core.vocabularies.analysis.dl_operands",
        required=False,
    )

    directives.write_permission(
        hidden="senaite.core.permissions.FieldEditAnalysisHidden"
    )
    hidden = schema.Bool(
        title=_(u"Hidden from report"),
        required=False,
    )

    directives.write_permission(
        remarks="senaite.core.permissions.FieldEditAnalysisRemarks"
    )
    remarks = schema.Text(
        title=_(u"Remarks"),
        required=False,
    )

    directives.write_permission(
        result_capture_date="senaite.core.permissions.FieldEditAnalysisResult"
    )
    result_capture_date = schema.TextLine(
        title=_(u"Result Capture Date"),
        required=False,
    )
