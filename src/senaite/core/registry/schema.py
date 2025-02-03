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
from plone.autoform import directives
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from zope import schema


class ISenaiteRegistry(model.Schema):
    """Senaite registry schema
    """


class IClientRegistry(ISenaiteRegistry):
    """Client settings
    """
    model.fieldset(
        "client_settings",
        label=_(u"Client Settings"),
        description=_("Settings for Clients"),
        fields=[
            "auto_create_client_group",
            "client_landing_page",
        ],
    )

    auto_create_client_group = schema.Bool(
        title=_("Automatically Create Client Group"),
        description=_("Automatically create a new global client group when a "
                      "new client is created. If this is disabled, a client "
                      "group is still created when a client contact is linked "
                      "to a user account. Therefore, disabling this option "
                      "makes only sense if you do not plan to link client "
                      "contacts to user accounts and you want to keep your "
                      "groups clean."
                      ),
        default=True,
        required=False,
    )

    client_landing_page = schema.Choice(
        title=_(
            u"label_registry_client_landing_page",
            default=u"Client landing page"
        ),
        description=_(
            u"description_registry_client_landing_page",
            default=u"Select the default landing page. This is used when a "
                    u"Client user logs into the system, or when a client is "
                    u"selected from the client folder listing"
        ),
        vocabulary="senaite.core.vocabularies.registry.client_landing_pages",
        default="analysisrequests",
        required=True,
    )


class ILabelRegistry(ISenaiteRegistry):
    """Label settings
    """
    model.fieldset(
        "label_enabled_portal_types",
        label=_(u"Labels"),
        description=_("Label configuration"),
        fields=[
            "label_enabled_portal_types",
        ],
    )

    directives.widget(label_enabled_portal_types=CheckBoxFieldWidget)
    label_enabled_portal_types = schema.List(
        title=_("Types with labels"),
        description=_(
            "Types that support labels directly.<br/>"
            "NOTE: In cluster setups, other instances need to be "
            "restarted manually for the changes to take place!"
         ),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.PortalTypes",
        ),
        required=False,
    )


class IWorksheetViewRegistry(ISenaiteRegistry):
    """View settings for worksheets
    """
    model.fieldset(
        "worksheet_view",
        label=_(u"Worksheet View"),
        description=_("Worksheet view configuration"),
        fields=[
            "worksheetview_analysis_columns_order",
            "worksheet_print_templates_order",
        ],
    )

    worksheetview_analysis_columns_order = schema.List(
        title=_(u"Analysis columns order"),
        description=_(
            u"Default column order for worksheet analysis listings"
        ),
        value_type=schema.ASCIILine(title=u"Column"),
        required=False,
        default=[
            "Pos",
            "Service",
            "AdditionalValues",
            "DetectionLimitOperand",
            "Result",
            "Uncertainty",
            "Specification",
            "retested",
            "Method",
            "Instrument",
            "Attachments",
            "DueDate",
            "state_title",
        ]
    )

    worksheet_print_templates_order = schema.List(
        title=_(u"Worksheet printing templates order"),
        description=_(
            u"Default printing templates order for worksheet"
        ),
        value_type=schema.ASCIILine(title=u"Column"),
        required=False,
        default=[],
    )


class ISampleViewRegistry(ISenaiteRegistry):
    """View settings for samples
    """
    model.fieldset(
        "sample_view",
        label=_(u"Sample View"),
        description=_("Sample view configuration"),
        fields=[
            "sampleview_collapse_field_analysis_table",
            "sampleview_collapse_lab_analysis_table",
            "sampleview_collapse_qc_analysis_table",
            "sampleview_analysis_columns_order",
        ],
    )
    sampleview_collapse_field_analysis_table = schema.Bool(
        title=_("Collapse field analysis table"),
        description=_("Collapse field analysis table in sample view"),
        default=False,
        required=False,
    )

    sampleview_collapse_lab_analysis_table = schema.Bool(
        title=_("Collapse lab analysis table"),
        description=_("Collapse lab analysis table in sample view"),
        default=False,
        required=False,
    )

    sampleview_collapse_qc_analysis_table = schema.Bool(
        title=_("Collapse qc analysis table"),
        description=_("Collapse qc analysis table in sample view"),
        default=True,
        required=False,
    )

    sampleview_analysis_columns_order = schema.List(
        title=_(u"Analysis columns order"),
        description=_(
            u"Default column order for sample analysis listings"
        ),
        value_type=schema.ASCIILine(title=u"Column"),
        required=False,
        default=[
            "created",
            "Service",
            "AdditionalValues",
            "DetectionLimitOperand",
            "Result",
            "Uncertainty",
            "Unit",
            "Specification",
            "retested",
            "Method",
            "Instrument",
            "Calculation",
            "Attachments",
            "SubmittedBy",
            "Analyst",
            "CaptureDate",
            "DueDate",
            "state_title",
            "Hidden",
        ]
    )


class ISampleHeaderRegistry(ISenaiteRegistry):
    """Registry settings for sample header configuration
    """

    model.fieldset(
        "sample_header",
        label=_(u"Sample Header"),
        description=_("Configuration for the sample header information"),
        fields=[
            "sampleheader_show_standard_fields",
            "sampleheader_prominent_columns",
            "sampleheader_standard_columns",
            "sampleheader_prominent_fields",
            "sampleheader_standard_fields",
            "sampleheader_field_visibility",
        ],
    )

    sampleheader_show_standard_fields = schema.Bool(
        title=_("Show standard fields"),
        description=_("Toggle visibility of standard sample header fields"),
        default=True,
        required=False,
    )

    sampleheader_prominent_columns = schema.Int(
        title=_("Number of prominent columns"),
        description=_("Number of prominent columns"),
        default=1,
        required=False,
        min=0,
        max=10,
    )

    sampleheader_standard_columns = schema.Int(
        title=_("Number of standard columns"),
        description=_("Number of standard columns"),
        default=3,
        required=False,
        min=0,
        max=10,
    )

    sampleheader_prominent_fields = schema.List(
        title=_("Prominent fields"),
        description=_("Prominent fields"),
        value_type=schema.ASCIILine(),
        required=False,
    )

    sampleheader_standard_fields = schema.List(
        title=_("Standard fields"),
        description=_("Standard fields"),
        value_type=schema.ASCIILine(),
        required=False,
    )

    sampleheader_field_visibility = schema.Dict(
        title=_("Field visibility"),
        description=_("Visible fields"),
        key_type=schema.ASCIILine(title=_("Field Name"),),
        value_type=schema.Bool(title=_("Field visibility"), default=True),
        required=False,
    )


class IGenericSetupRegistry(ISenaiteRegistry):
    """Registry settings for Generic Setup
    """

    model.fieldset(
        "generic_setup",
        label=_(u"Generic Setup"),
        description=_("Configuration for Generic Setup"),
        fields=[
            "generic_setup_skip_export_types",
        ],
    )

    generic_setup_skip_export_types = schema.List(
        title=_(
            u"label_registry_generic_setup_skip_export_types",
            default=u"Portal types to skip on content structure export"
        ),
        description=_(
            u"description_registry_generic_setup_skip_export_types",
            default=u"List of portal types to be skipped when exporting the "
                    u"content structure of the site via Generic Setup"
        ),
        value_type=schema.ASCIILine(),
        required=False,
        default=[
            "AnalysisRequest",
            "ARReport",
            "Attachment",
            "AutoImportLog",
            "Batch",
            "Invoice",
            "ReferenceSample",
            "Report",
            "Worksheet",
        ]
    )


class ICatalogRegistry(ISenaiteRegistry):
    """Registry settings for Catalog settings
    """

    model.fieldset(
        "catalogs",
        label=_(
            u"label_registry_catalogs_fieldset",
            default=u"Catalogs"
        ),
        fields=[
            "catalog_mappings",
        ],
    )
    catalog_mappings = schema.Dict(
        title=_(
            u"label_registry_catalog_mappings",
            default=u"Catalog mappings"
        ),
        description=_(
            u"description_registry_catalog_mappings",
            default=u"Define the relationship between portal types and the "
                    u"additional catalogs in which these portal types should "
                    u"be indexed, beyond the default catalogs. A restart is "
                    u"required for these changes to take effect."
        ),
        key_type=schema.Choice(
            title=_(
                u"label_registry_catalog_mappings_key",
                default=u"Portal type"
            ),
            vocabulary="plone.app.vocabularies.PortalTypes",
        ),
        value_type=schema.List(
            title=_(
                u"label_registry_catalog_mappings_value",
                default=u"Catalogs"
            ),
            value_type=schema.ASCIILine(),
        ),
        required=False,
    )
