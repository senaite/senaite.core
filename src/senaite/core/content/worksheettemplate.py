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

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.supermodel import model
from plone.autoform import directives
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema import UIDReferenceField
from senaite.core.content.base import Container
from senaite.core.interfaces import IWorksheetTemplate
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer


class IWorksheetTemplateSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_worksheettemplate_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_worksheettemplate_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget(
        "restrict_to_method",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "Method",
            "is_active": True,
            "sort_limit": 5,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${getFullname}</a>",
        columns=get_labcontact_columns,
        limit=5,
    )
    restrict_to_method = UIDReferenceField(
        title=_(
            u"label_worksheettemplate_restrict_to_method",
            default=u"Restrict to Method"
        ),
        description=_(
            u"description_worksheettemplate_restrict_to_method",
            default=u"Restrict the available analysis services and "
                    u"instruments to those with the selected method.<br/>"
                    u"In order to apply this change to the services list, "
                    u"you should save the change first."
        ),
        allowed_types=("Method",),
        multi_valued=False,
        required=False,
    )

    directives.widget(
        "instrument",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_widget_instrument_query",
        display_template="<a href='${url}'>${getFullname}</a>",
        columns=get_labcontact_columns,
        limit=5,
    )
    instrument = UIDReferenceField(
        title=_(
            u"label_worksheettemplate_instrument",
            default=u"Preferred instrument"
        ),
        description=_(u"description_worksheettemplate_instrument",
                      default=u"Select the preferred instrument"),
        allowed_types=("Instrument",),
        multi_valued=False,
        required=False,
    )

    enable_multiple_use_of_instrument = schema.Bool(
        title=_(
            u"label_worksheettemplate_enable_multiple_user_of_instrument",
            default=u"Enable Multiple Use of Instrument in Worksheets",
        ),
        description=_(
            u"description_worksheettemplate_multiple_user_of_instrument",
            default=u"If unchecked, Lab Managers won't be able to assign "
                    u"the same Instrument more than one Analyses while "
                    u"creating a Worksheet."
        ),
        required=False,
    )

    model.fieldset(
        "layout",
        label=_(
            u"label_fieldset_worksheettemplate_layout",
            default=u"Layout"
        ),
        fields=[
            "layout",
        ]
    )

    layout = schema.TextLine()

    # RecordsField(
    #     "Layout",
    #     schemata="Layout",
    #     required=1,
    #     type="templateposition",
    #     subfields=("pos", "type", "blank_ref", "control_ref", "dup"),
    #     required_subfields=("pos", "type"),
    #     subfield_labels={
    #         "pos": _("Position"),
    #         "type": _("Analysis Type"),
    #         "blank_ref": _("Reference"),
    #         "control_ref": _("Reference"),
    #         "dup": _("Duplicate Of")
    #     },
    #     widget=WorksheetTemplateLayoutWidget(
    #         label=_("Worksheet Layout"),
    #         description=_(
    #             "Specify the size of the Worksheet, e.g. corresponding to a "
    #             "specific instrument's tray size. "
    #             "Then select an Analysis 'type' per Worksheet position."
    #             "Where QC samples are selected, also select which Reference "
    #             "Sample should be used."
    #             "If a duplicate analysis is selected, indicate which sample "
    #             "position it should be a duplicate of"),
    #     )
    # ),

    model.fieldset(
        "analyses",
        label=_(
            u"label_fieldset_worksheettemplate_analyses",
            default=u"Analyses"
        ),
        fields=[
            "service",
        ]
    )

    service = schema.TextLine()

    # UIDReferenceField(
    #     "Service",
    #     schemata="Analyses",
    #     required=0,
    #     multiValued=1,
    #     allowed_types=("AnalysisService",),
    #     widget=ServicesWidget(
    #         label=_("Analysis Service"),
    #         description=_(
    #             "Select which Analyses should be included on the Worksheet"
    #         ),
    #     )
    # ),


@implementer(IWorksheetTemplate, IWorksheetTemplateSchema, IDeactivable)
class WorksheetTemplates(Container):
    """Worksheet Template type
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()
