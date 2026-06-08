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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import string
from datetime import timedelta

import six
from AccessControl import ClassSecurityInfo
from bika.lims import _
from bika.lims import api
from plone.app.textfield import IRichTextValue
from plone.app.textfield.widget import RichTextFieldWidget  # TBD: port to core
from plone.autoform import directives
from plone.formwidget.namedfile.widget import NamedFileFieldWidget
from plone.schema.email import Email
from plone.supermodel import model
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api import dtime
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ISetup
from senaite.core.schema import DurationField
from senaite.core.schema import RichTextField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.textlinefield import TextLineField
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.duration.widget import DurationWidgetFactory
from zope import schema
from zope.component import getUtility
from zope.deprecation import deprecate
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_email_body_sample_publication(context):
    """Returns the default body text for publication emails
    """
    view = api.get_view("senaite_view", context=api.get_senaite_setup())
    if view is None:
        # Test fixture
        return u""
    tpl = ViewPageTemplateFile(
        "../browser/setup/templates/email_body_sample_publication.pt")
    return tpl(view)


@provider(IContextAwareDefaultFactory)
def default_email_from_sample_publication(context):
    """Returns the default email 'From' for results reports publish
    """
    portal_email = api.get_registry_record("plone.email_from_address")
    return portal_email


DEFAULT_ID_FORMATTING = [
    {
        "form": "B-{seq:03d}",
        "portal_type": "Batch",
        "prefix": "batch",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "D-{seq:03d}",
        "portal_type": "DuplicateAnalysis",
        "prefix": "duplicate",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "I-{seq:03d}",
        "portal_type": "Invoice",
        "prefix": "invoice",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "QC-{seq:03d}",
        "portal_type": "ReferenceSample",
        "prefix": "refsample",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "SA-{seq:03d}",
        "portal_type": "ReferenceAnalysis",
        "prefix": "refanalysis",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "WS-{seq:03d}",
        "portal_type": "Worksheet",
        "prefix": "worksheet",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "{sampleType}-{seq:04d}",
        "portal_type": "AnalysisRequest",
        "prefix": "analysisrequest",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "{parent_ar_id}-P{partition_count:02d}",
        "portal_type": "AnalysisRequestPartition",
        "prefix": "analysisrequestpartition",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "{parent_base_id}-R{retest_count:02d}",
        "portal_type": "AnalysisRequestRetest",
        "prefix": "analysisrequestretest",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
    {
        "form": "{parent_ar_id}-S{secondary_count:02d}",
        "portal_type": "AnalysisRequestSecondary",
        "prefix": "analysisrequestsecondary",
        "sequence_type": "generated",
        "context": "",
        "counter_type": "",
        "counter_reference": "",
        "split_length": 1
    },
]


def _record_get(record, key, default=None):
    """Resolve a value from a DataGrid record, which may expose its
    fields either as attributes (RecordsRecord) or as dict items.
    """
    try:
        value = getattr(record, key)
    except AttributeError:
        value = None
    if value is None:
        try:
            value = record[key]
        except (KeyError, TypeError):
            value = default
    return value


class IIDFormattingRecordSchema(Interface):
    """Schema for ID formatting configuration records
    """

    portal_type = TextLineField(
        title=_(u"Portal Type"),
        required=False,
    )

    form = TextLineField(
        title=_(u"Format"),
        required=False,
    )

    sequence_type = schema.Choice(
        title=_(u"Seq Type"),
        values=["", "counter", "generated"],
        required=False,
        default="",
    )

    context = TextLineField(
        title=_(u"Context"),
        required=False,
    )

    counter_type = schema.Choice(
        title=_(u"Counter Type"),
        values=["", "backreference", "contained"],
        required=False,
        default="",
    )

    counter_reference = TextLineField(
        title=_(u"Counter Ref"),
        required=False,
    )

    prefix = TextLineField(
        title=_(u"Prefix"),
        required=False,
    )

    split_length = schema.Int(
        title=_(u"Split Length"),
        required=False,
        default=1,
    )


class ISetupSchema(model.Schema):
    """Schema and marker interface
    """

    email_from_sample_publication = Email(
        title=_(
            "title_senaitesetup_email_from_sample_publication",
            default="Publication 'From' address"
        ),
        description=_(
            "description_senaitesetup_email_from_sample_publication",
            default="E-mail to use as the 'From' address for outgoing e-mails "
                    "when publishing results reports. This address overrides "
                    "the value set at portal's 'Mail settings'."
        ),
        defaultFactory=default_email_from_sample_publication,
        required=False,
    )

    directives.widget("email_body_sample_publication", RichTextFieldWidget)
    email_body_sample_publication = RichTextField(
        title=_("title_senaitesetup_publication_email_text",
                default=u"Publication Email Text"),
        description=_(
            "description_senaitesetup_publication_email_text",
            default=u"Set the email body text to be used by default "
            "when sending out result reports to the selected recipients. "
            "You can use reserved keywords: "
            "$client_name, $recipients, $lab_name, $lab_address"),
        defaultFactory=default_email_body_sample_publication,
        required=False,
    )

    always_cc_responsibles_in_report_emails = schema.Bool(
        title=_(
            "title_senaitesetup_always_cc_responsibles_in_report_emails",
            default=u"Always send publication email to responsibles"),
        description=_(
            "description_senaitesetup_always_cc_responsibles_in_report_emails",
            default="When selected, the responsible persons of all involved "
            "lab departments will receive publication emails."
        ),
        default=True,
    )

    enable_global_auditlog = schema.Bool(
        title=_(u"Enable global Auditlog"),
        description=_(
            "The global Auditlog shows all modifications of the system. "
            "When enabled, all entities will be indexed in a separate "
            "catalog. This will increase the time when objects are "
            "created or modified."
        ),
        default=False,
    )

    # NOTE:
    # We use the `NamedFileFieldWidget` instead of `NamedImageFieldWidget`
    # by purpose! Using the latter rises this PIL error (appears only in log):
    # IOError: cannot identify image file <cStringIO.StringI object at ...>
    directives.widget("site_logo", NamedFileFieldWidget)
    site_logo = schema.Bytes(
        title=_(u"Site Logo"),
        description=_(u"This shows a custom logo on your SENAITE site."),
        required=False,
    )

    site_logo_css = schema.ASCII(
        title=_(u"Site Logo CSS"),
        description=_(
            u"Add custom CSS rules for the Logo, "
            u"e.g. height:15px; width:150px;"
        ),
        required=False,
    )

    immediate_results_entry = schema.Bool(
        title=_(u"Immediate results entry"),
        description=_(
            "description_senaitesetup_immediateresultsentry",
            default=u"Allow the user to directly enter results after sample "
            "creation, e.g. to enter field results immediately, or lab "
            "results, when the automatic sample reception is activated."
        ),
    )

    categorize_sample_analyses = schema.Bool(
        title=_("title_senaitesetup_categorizesampleanalyses",
                default=u"Categorize sample analyses"),
        description=_(
            "description_senaitesetup_categorizesampleanalyses",
            default=u"Group analyses by category for samples"
        ),
        default=False,
    )

    sample_analyses_required = schema.Bool(
        title=_("title_senaitesetup_sampleanalysesrequired",
                default=u"Require sample analyses"),
        description=_(
            "description_senaitesetup_sampleanalysesrequired",
            default=u"Analyses are required for sample registration"
        ),
        default=True,
    )

    # Allow Manual Analysis Result Capture Date
    allow_manual_result_capture_date = schema.Bool(
        title=_("title_senaitesetup_allow_manual_result_capture_date",
                default=u"Allow to set the result capture date"),
        description=_(
            "description_senaitesetup_allow_manual_result_capture_date",
            default=u"If this option is activated, the result capture date "
                    u"can be entered manually for analyses"),
        default=False)

    max_number_of_samples_add = schema.Int(
        title=_(
            u"label_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum value for 'Number of samples' field on "
                    u"registration"
        ),
        description=_(
            u"description_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum number of samples that can be created in "
                    u"accordance with the value set for the field 'Number of "
                    u"samples' on the sample registration form"
        ),
        default=10
    )

    date_sampled_required = schema.Bool(
        title=_(
            u"title_senaitesetup_date_sampled_required",
            default=u"Date sampled required"),
        description=_(
            u"description_senaitesetup_date_sampled_required",
            default=u"Select this to make DateSampled field required on "
                    u"sample creation. This functionality only takes effect "
                    u"when 'Sampling workflow' is not active"
        ),
        default=True,
    )

    show_lab_name_in_login = schema.Bool(
        title=_(
            u"title_senaitesetup_show_lab_name_in_login",
            default=u"Display laboratory name in the login page"),
        description=_(
            u"description_senaitesetup_show_lab_name_in_login",
            default=u"When selected, the laboratory name will be displayed"
                    u"in the login page, above the access credentials."
        ),
        default=False,
    )

    invalidation_reason_required = schema.Bool(
        title=_(
            u"title_senaitesetup_invalidation_reason_required",
            default=u"Invalidation reason required"),
        description=_(
            u"description_senaitesetup_invalidation_reason_required",
            default=u"Specify whether providing a reason is mandatory when "
                    u"invalidating a sample. If enabled, the '$reason' "
                    u"placeholder in the sample invalidation notification "
                    u"email body will be replaced with the entered reason."
        ),
        default=True,
    )

    # Security
    auto_log_off = schema.Int(
        title=_(
            u"title_senaitesetup_auto_log_off",
            default=u"Automatic log-off"
        ),
        description=_(
            u"description_senaitesetup_auto_log_off",
            default=u"The number of minutes before a user is automatically "
                    u"logged off. 0 disables automatic log-off"
        ),
        required=True,
        default=0,
    )

    restrict_worksheet_users_access = schema.Bool(
        title=_(
            u"title_senaitesetup_restrict_worksheet_users_access",
            default=u"Restrict worksheet access to assigned analysts"
        ),
        description=_(
            u"description_senaitesetup_restrict_worksheet_users_access",
            default=u"When enabled, analysts can only access worksheets to "
                    u"which they are assigned. When disabled, analysts have "
                    u"access to all worksheets."
        ),
        default=True,
    )

    allow_to_submit_not_assigned = schema.Bool(
        title=_(
            u"title_senaitesetup_allow_to_submit_not_assigned",
            default=u"Allow submission of results for unassigned analyses"
        ),
        description=_(
            u"description_senaitesetup_allow_to_submit_not_assigned",
            default=u"When enabled, users can submit results for analyses not "
                    u"assigned to them or for unassigned analyses. When "
                    u"disabled, users can only submit results for analyses "
                    u"assigned to themselves. This setting does not apply to "
                    u"users with role Lab Manager."
        ),
        default=True,
    )

    restrict_worksheet_management = schema.Bool(
        title=_(
            u"title_senaitesetup_restrict_worksheet_management",
            default=u"Restrict worksheet management to lab managers"
        ),
        description=_(
            u"description_senaitesetup_restrict_worksheet_management",
            default=u"When enabled, only lab managers can create and manage "
                    u"worksheets. When disabled, analysts and lab clerks can "
                    u"also manage worksheets. Note: This setting is "
                    u"automatically enabled and locked when worksheet access "
                    u"is restricted to assigned analysts."
        ),
        default=True,
    )

    # Accounting
    show_prices = schema.Bool(
        title=_(
            u"title_senaitesetup_show_prices",
            default=u"Include and display pricing information"
        ),
        default=True,
    )

    currency = schema.Choice(
        title=_(
            u"title_senaitesetup_currency",
            default=u"Currency"
        ),
        description=_(
            u"description_senaitesetup_currency",
            default=u"Select the currency the site will use to display prices."
        ),
        vocabulary="senaite.core.vocabularies.currencies",
        required=True,
        default="EUR",
    )

    default_country = schema.Choice(
        title=_(
            u"title_senaitesetup_default_country",
            default=u"Country"
        ),
        description=_(
            u"description_senaitesetup_default_country",
            default=u"Select the country the site will show by default"
        ),
        vocabulary="senaite.core.vocabularies.countries",
        required=False,
    )

    directives.widget("member_discount", klass="numeric")
    member_discount = schema.TextLine(
        title=_(
            u"title_senaitesetup_member_discount",
            default=u"Member discount %"
        ),
        description=_(
            u"description_senaitesetup_member_discount",
            default=u"The discount percentage entered here, is applied to the "
                    u"prices for clients flagged as 'members', normally "
                    u"co-operative members or associates deserving of this "
                    u"discount"
        ),
        required=True,
        default=u"0.0",
    )

    directives.widget("vat", klass="numeric")
    vat = schema.TextLine(
        title=_(
            u"title_senaitesetup_vat",
            default=u"VAT %"
        ),
        description=_(
            u"description_senaitesetup_vat",
            default=u"Enter percentage value eg. 14.0. This percentage is "
                    u"applied system wide but can be overwritten on individual "
                    u"items"
        ),
        required=True,
        default=u"0.0",
    )

    # Results Reports
    decimal_mark = schema.Choice(
        title=_(
            u"title_senaitesetup_decimal_mark",
            default=u"Default decimal mark"
        ),
        description=_(
            u"description_senaitesetup_decimal_mark",
            default=u"Preferred decimal mark for reports."
        ),
        vocabulary="senaite.core.vocabularies.decimal_marks",
        default=".",
    )

    scientific_notation_report = schema.Choice(
        title=_(
            u"title_senaitesetup_scientific_notation_report",
            default=u"Default scientific notation format for reports"
        ),
        description=_(
            u"description_senaitesetup_scientific_notation_report",
            default=u"Preferred scientific notation format for reports"
        ),
        vocabulary="senaite.core.vocabularies.scientific_notation",
        default="1",
    )

    minimum_results = schema.Int(
        title=_(
            u"title_senaitesetup_minimum_results",
            default=u"Minimum number of results for QC stats calculations"
        ),
        description=_(
            u"description_senaitesetup_minimum_results",
            default=u"Using too few data points does not make statistical "
                    u"sense. Set an acceptable minimum number of results before "
                    u"QC statistics will be calculated and plotted"
        ),
        required=True,
        default=5,
    )

    # Analyses
    categorise_analysis_services = schema.Bool(
        title=_(
            u"title_senaitesetup_categorise_analysis_services",
            default=u"Categorise analysis services"
        ),
        description=_(
            u"description_senaitesetup_categorise_analysis_services",
            default=u"Group analysis services by category in the LIMS tables, "
                    u"helpful when the list is long"
        ),
        default=False,
    )

    enable_ar_specs = schema.Bool(
        title=_(
            u"title_senaitesetup_enable_ar_specs",
            default=u"Enable Sample Specifications"
        ),
        description=_(
            u"description_senaitesetup_enable_ar_specs",
            default=u"Analysis specifications which are edited directly on the "
                    u"Sample."
        ),
        default=False,
    )

    exponential_format_threshold = schema.Int(
        title=_(
            u"title_senaitesetup_exponential_format_threshold",
            default=u"Exponential format threshold"
        ),
        description=_(
            u"description_senaitesetup_exponential_format_threshold",
            default=u"Result values with at least this number of significant "
                    u"digits are displayed in scientific notation using the "
                    u"letter 'e' to indicate the exponent. The precision can be "
                    u"configured in individual Analysis Services."
        ),
        required=True,
        default=7,
    )

    enable_analysis_remarks = schema.Bool(
        title=_(
            u"title_senaitesetup_enable_analysis_remarks",
            default=u"Add a remarks field to all analyses"
        ),
        description=_(
            u"description_senaitesetup_enable_analysis_remarks",
            default=u"If enabled, a free text field will be displayed close to "
                    u"each analysis in results entry view"
        ),
        default=False,
    )

    auto_verify_samples = schema.Bool(
        title=_(
            u"title_senaitesetup_auto_verify_samples",
            default=u"Automatic verification of samples"
        ),
        description=_(
            u"description_senaitesetup_auto_verify_samples",
            default=u"When enabled, the sample is automatically verified as "
                    u"soon as all results are verified. Otherwise, users with "
                    u"enough privileges have to manually verify the sample "
                    u"afterwards. Default: enabled"
        ),
        default=True,
    )

    self_verification_enabled = schema.Bool(
        title=_(
            u"title_senaitesetup_self_verification_enabled",
            default=u"Allow self-verification of results"
        ),
        description=_(
            u"description_senaitesetup_self_verification_enabled",
            default=u"If enabled, a user who submitted a result will also be "
                    u"able to verify it. This setting only take effect for "
                    u"those users with a role assigned that allows them to "
                    u"verify results (by default, managers, labmanagers and "
                    u"verifiers). This setting can be overrided for a given "
                    u"Analysis in Analysis Service edit view. By default, "
                    u"disabled."
        ),
        default=False,
    )

    number_of_required_verifications = schema.Choice(
        title=_(
            u"title_senaitesetup_number_of_required_verifications",
            default=u"Number of required verifications"
        ),
        description=_(
            u"description_senaitesetup_number_of_required_verifications",
            default=u"Number of required verifications before a given result "
                    u"being considered as 'verified'. This setting can be "
                    u"overrided for any Analysis in Analysis Service edit view. "
                    u"By default, 1"
        ),
        vocabulary="senaite.core.vocabularies.number_of_verifications",
        default=1,
    )

    type_of_multi_verification = schema.Choice(
        title=_(
            u"title_senaitesetup_type_of_multi_verification",
            default=u"Multi Verification type"
        ),
        description=_(
            u"description_senaitesetup_type_of_multi_verification",
            default=u"Choose type of multiple verification for the same user. "
                    u"This setting can enable/disable verifying/consecutively "
                    u"verifying more than once for the same user."
        ),
        vocabulary="senaite.core.vocabularies.multi_verification_type",
        default="self_multi_enabled",
    )

    results_decimal_mark = schema.Choice(
        title=_(
            u"title_senaitesetup_results_decimal_mark",
            default=u"Default decimal mark"
        ),
        description=_(
            u"description_senaitesetup_results_decimal_mark",
            default=u"Preferred decimal mark for results"
        ),
        vocabulary="senaite.core.vocabularies.decimal_marks",
        default=".",
    )

    scientific_notation_results = schema.Choice(
        title=_(
            u"title_senaitesetup_scientific_notation_results",
            default=u"Default scientific notation format for results"
        ),
        description=_(
            u"description_senaitesetup_scientific_notation_results",
            default=u"Preferred scientific notation format for results"
        ),
        vocabulary="senaite.core.vocabularies.scientific_notation",
        default="1",
    )

    default_number_of_ars_to_add = schema.Int(
        title=_(
            u"title_senaitesetup_default_number_of_ars_to_add",
            default=u"Default count of Sample to add."
        ),
        description=_(
            u"description_senaitesetup_default_number_of_ars_to_add",
            default=u"Default value of the 'Sample count' when users click "
                    u"'ADD' button to create new Samples"
        ),
        required=False,
        default=4,
    )

    enable_rejection_workflow = schema.Bool(
        title=_(
            u"title_senaitesetup_enable_rejection_workflow",
            default=u"Enable the rejection workflow"
        ),
        description=_(
            u"description_senaitesetup_enable_rejection_workflow",
            default=u"Select this to activate the rejection workflow for "
                    u"Samples. A 'Reject' option will be displayed in the "
                    u"actions menu."
        ),
        required=False,
        default=False,
    )

    rejection_reasons = schema.List(
        title=_(
            u"title_senaitesetup_rejection_reasons",
            default=u"Rejection reasons"
        ),
        description=_(
            u"description_senaitesetup_rejection_reasons",
            default=u"Enter the predefined rejection reasons that users can "
                    u"select when rejecting a sample."
        ),
        value_type=schema.TextLine(),
        required=False,
        default=[],
    )

    max_number_of_samples_add = schema.Int(
        title=_(
            u"label_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum value for 'Number of samples' field on "
                    u"registration"
        ),
        description=_(
            u"description_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum number of samples that can be created in "
                    u"accordance with the value set for the field 'Number "
                    u"of samples' on the sample registration form"
        ),
        required=False,
        default=10,
    )

    sampleview_analysis_columns_order = schema.Tuple(
        title=_(
            u"title_senaitesetup_sampleview_columns_order",
            default=u"Sample view analysis columns"
        ),
        description=_(
            u"description_senaitesetup_sampleview_columns_order",
            default=u"Select which columns to display in "
                    u"sample analysis listings. The order "
                    u"of selection determines the display "
                    u"order. Unselected columns are hidden. "
                    u"Leave empty to show all columns in "
                    u"default order."
        ),
        value_type=schema.Choice(
            vocabulary=("senaite.core.vocabularies.analysis_columns")
        ),
        required=False,
    )

    worksheetview_analysis_columns_order = schema.Tuple(
        title=_(
            u"title_senaitesetup_wsview_columns_order",
            default=u"Worksheet view analysis columns"
        ),
        description=_(
            u"description_senaitesetup_wsview_columns_order",
            default=u"Select which columns to display in "
                    u"worksheet analysis listings. The "
                    u"order of selection determines the "
                    u"display order. Unselected columns "
                    u"are hidden. Leave empty to show all "
                    u"columns in default order."
        ),
        value_type=schema.Choice(
            vocabulary=("senaite.core.vocabularies.worksheet_analysis_columns")
        ),
        required=False,
    )

    # Appearance
    worksheet_layout = schema.Choice(
        title=_(
            u"title_senaitesetup_worksheet_layout",
            default=u"Default layout in worksheet view"
        ),
        description=_(
            u"description_senaitesetup_worksheet_layout",
            default=u"Preferred layout of the results entry table in the "
                    u"Worksheet view. Classic layout displays the Samples in "
                    u"rows and the analyses in columns. Transposed layout "
                    u"displays the Samples in columns and the analyses in rows."
        ),
        vocabulary="senaite.core.vocabularies.worksheet_layout",
        default="analyses_classic_view",
    )

    dashboard_by_default = schema.Bool(
        title=_(
            u"title_senaitesetup_dashboard_by_default",
            default=u"Use Dashboard as default front page"
        ),
        description=_(
            u"description_senaitesetup_dashboard_by_default",
            default=u"Select this to activate the dashboard as a default front "
                    u"page."
        ),
        default=True,
    )

    landing_page = UIDReferenceField(
        title=_(
            u"title_senaitesetup_landing_page",
            default=u"Landing Page"
        ),
        description=_(
            u"description_senaitesetup_landing_page",
            default=u"The landing page is shown for non-authenticated users if "
                    u"the Dashboard is not selected as the default front page. "
                    u"If no landing page is selected, the default frontpage is "
                    u"displayed."
        ),
        allowed_types=(
            "Document",
            "Client",
            "ClientFolder",
            "Samples",
            "WorksheetFolder",
        ),
        multi_valued=False,
        relationship="SetupLandingPage",
        required=False,
    )

    show_partitions = schema.Bool(
        title=_(
            u"title_senaitesetup_show_partitions",
            default=u"Display sample partitions to clients"
        ),
        description=_(
            u"description_senaitesetup_show_partitions",
            default=u"Select to show sample partitions to client contacts. If "
                    u"deactivated, partitions won't be included in listings and "
                    u"no info message with links to the primary sample will be "
                    u"displayed to client contacts."
        ),
        default=False,
    )

    sidebar_folders = schema.Tuple(
        title=_(
            u"title_senaitesetup_sidebar_folders",
            default=u"Sidebar navigation folders"
        ),
        description=_(
            u"description_senaitesetup_sidebar_folders",
            default=u"Select which top-level folders should be displayed in "
                    u"the sidebar navigation. The order of selection determines "
                    u"the display order in the sidebar. If none are selected, "
                    u"all folders will be shown in the default order."
        ),
        value_type=schema.Choice(
            vocabulary="senaite.core.vocabularies.top_level_folders"
        ),
        required=False,
        default=("clients", "samples", "methods", "batches", "worksheets"),
    )

    sidebar_navigation_depth = schema.Int(
        title=_(
            u"title_senaitesetup_sidebar_navigation_depth",
            default=u"Sidebar navigation depth"
        ),
        description=_(
            u"description_senaitesetup_sidebar_navigation_depth",
            default=u"Maximum depth of the sidebar navigation tree. "
                    u"Level 1 shows only top-level folders, level 2 includes "
                    u"their children, and so on."
        ),
        required=True,
        default=1,
        min=1,
        max=3,
    )

    sidebar_skip_types = schema.Tuple(
        title=_(
            u"title_senaitesetup_sidebar_skip_types",
            default=u"Sidebar skipped portal types"
        ),
        description=_(
            u"description_senaitesetup_sidebar_skip_types",
            default=u"Select which content types should be excluded from the "
                    u"sidebar navigation. If none are selected, all content "
                    u"types will be shown."
        ),
        value_type=schema.Choice(
            vocabulary="senaite.core.vocabularies.navigation_portal_types"
        ),
        required=False,
        default=("AnalysisRequest", "Attachment", ),
    )

    # Sampling
    sample_duplicate_enabled = schema.Bool(
        title=_(
            u"title_senaitesetup_sample_duplicate_enabled",
            default=u"Allow sample duplication"
        ),
        description=_(
            u"description_senaitesetup_sample_duplicate_enabled",
            default=u"If enabled, users with sufficient privileges can "
                    u"create a sibling sample directly from an existing "
                    u"one via the 'Duplicate' action in the samples "
                    u"listing. Enabled by default."
        ),
        default=True,
    )

    printing_workflow_enabled = schema.Bool(
        title=_(u"Enable the Results Report Printing workflow"),
        description=_(
            u"Select this to allow the user to set an additional 'Printed' "
            u"status to those Analysis Requests that have been Published. "
            u"Disabled by default."
        ),
        default=False,
    )

    sampling_workflow_enabled = schema.Bool(
        title=_(u"Enable Sampling"),
        description=_(
            u"Select this to activate the sample collection workflow steps."
        ),
        default=False,
    )

    schedule_sampling_enabled = schema.Bool(
        title=_(u"Enable Sampling Scheduling"),
        description=_(
            u"Select this to allow a Sampling Coordinator to schedule a "
            u"sampling. This functionality only takes effect when 'Sampling "
            u"workflow' is active"
        ),
        default=False,
    )

    autoreceive_samples = schema.Bool(
        title=_(u"Auto-receive samples"),
        description=_(
            u"Select to receive the samples automatically when created by lab "
            u"personnel and sampling workflow is disabled. Samples created by "
            u"client contacts won't be received automatically"
        ),
        default=False,
    )

    sample_preservation_enabled = schema.Bool(
        title=_(u"Enable Sample Preservation"),
        description=u"",
        default=False,
    )

    workdays = schema.List(
        title=_(u"Laboratory Workdays"),
        description=_(
            u"Only laboratory workdays are considered for the analysis "
            u"turnaround time calculation."
        ),
        value_type=schema.Choice(
            vocabulary="senaite.core.vocabularies.weekdays"
        ),
        default=[u"0", u"1", u"2", u"3", u"4", u"5", u"6"],
        required=True,
    )

    directives.widget("default_turnaround_time", DurationWidgetFactory)
    default_turnaround_time = DurationField(
        title=_(u"Default turnaround time for analyses."),
        description=_(
            u"This is the default maximum time allowed for performing "
            u"analyses. It is only used for analyses where the analysis "
            u"service does not specify a turnaround time. Only laboratory "
            u"workdays are considered."
        ),
        required=True,
        default=timedelta(days=5),
    )

    directives.widget("default_sample_lifetime", DurationWidgetFactory)
    default_sample_lifetime = DurationField(
        title=_(u"Default sample retention period"),
        description=_(
            u"The number of days before a sample expires and cannot be "
            u"analysed any more. This setting can be overwritten per "
            u"individual sample type in the sample types setup"
        ),
        required=True,
        default=timedelta(days=30),
    )

    # Notifications
    notify_on_sample_rejection = schema.Bool(
        title=_(u"Email notification on Sample rejection"),
        description=_(
            u"Select this to activate automatic notifications via email to "
            u"the Client when a Sample is rejected."
        ),
        default=False,
    )

    directives.widget("email_body_sample_rejection", RichTextFieldWidget)
    email_body_sample_rejection = RichTextField(
        title=_(u"Email body for Sample Rejection notifications"),
        description=_(
            u"Set the text for the body of the email to be sent to the "
            u"Sample's client contact if the option 'Email notification on "
            u"Sample rejection' is enabled. You can use reserved keywords: "
            u"$sample_id, $sample_link, $reasons, $lab_address"
        ),
        default=u"The sample $sample_link has been rejected because of the "
                u"following reasons:<br/><br/>$reasons<br/><br/>For further "
                u"information, please contact us under the following address."
                u"<br/><br/>$lab_address",
        required=False,
    )

    directives.widget("email_body_sample_invalidation", RichTextFieldWidget)
    email_body_sample_invalidation = RichTextField(
        title=_(u"Email body for Sample Invalidation notifications"),
        description=_(
            u"Define the template for the email body that will be "
            u"automatically sent to primary contacts and laboratory managers "
            u"when a sample is invalidated. The following placeholders are "
            u"supported: $sample_id, $retest_id, $retest_link, $reason, "
            u"$lab_address."
        ),
        default=u"Some non-conformities have been detected in the results "
                u"report published for Sample $sample_link.<br/><br/>A new "
                u"Sample $retest_link has been created automatically, and the "
                u"previous request has been invalidated.<br/><br/>The root "
                u"cause is under investigation and corrective action has been "
                u"initiated.<br/><br/>$lab_address",
        required=False,
    )

    # Sticker
    auto_print_stickers = schema.Choice(
        title=_(u"Automatic Sticker Printing"),
        description=_(
            u"Choose when stickers should be automatically printed:<br/>"
            u"<ul><li><strong>Register:</strong> Stickers are printed "
            u"automatically when new samples are created.</li>"
            u"<li><strong>Receive:</strong> Stickers are printed automatically "
            u"when samples are received.</li>"
            u"<li><strong>None:</strong> Disables automatic sticker printing."
            u"</li></ul>"
        ),
        vocabulary=schema.vocabulary.SimpleVocabulary([
            schema.vocabulary.SimpleTerm("None", "None", _(u"None")),
            schema.vocabulary.SimpleTerm("register", "register",
                                         _(u"Register")),
            schema.vocabulary.SimpleTerm("receive", "receive", _(u"Receive")),
        ]),
        required=False,
        default="None",
    )

    auto_sticker_template = schema.Choice(
        title=_(u"Default Sticker Template"),
        description=_(
            u"Select the default sticker template used for automatic printing."
        ),
        vocabulary="senaite.core.vocabularies.stickers",
        default=u"Code_128_1x48mm.pt",
        required=False,
    )

    small_sticker_template = schema.Choice(
        title=_(u"Small Sticker Template"),
        description=_(
            u"Choose the default template for 'small' stickers. Note: "
            u"Sample-specific 'small' stickers are configured based on their "
            u"sample type."
        ),
        vocabulary="senaite.core.vocabularies.stickers",
        default=u"Code_128_1x48mm.pt",
        required=False,
    )

    large_sticker_template = schema.Choice(
        title=_(u"Large Sticker Template"),
        description=_(
            u"Choose the default template for 'large' stickers. Note: "
            u"Sample-specific 'large' stickers are configured based on their "
            u"sample type."
        ),
        vocabulary="senaite.core.vocabularies.stickers",
        default=u"Code_128_1x72mm.pt",
        required=False,
    )

    default_number_of_copies = schema.Int(
        title=_(u"Default Number of Copies"),
        description=_(
            u"Specify how many copies of each sticker should be printed by "
            u"default."
        ),
        required=True,
        default=1,
    )

    # ID Server
    directives.widget(
        "id_formatting",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=False)
    id_formatting = DataGridField(
        title=_(u"Formatting Configuration"),
        description=_(
            u"<p>The ID Server provides unique sequential IDs for objects "
            u"such as Samples and Worksheets etc, based on a format "
            u"specified for each content type. The format is constructed "
            u"similarly to the Python format syntax, e.g. "
            u"<code>WS-{seq:03d}</code> produces <code>WS-001</code>, "
            u"<code>WS-002</code>, <code>WS-003</code> etc.</p>"
            u"<p>The current persistent counter values are managed in the "
            u"<a href='ng'>Number Generator view</a>.</p>"
            u"<details class='id-server-cheatsheet'>"
            u"<summary>Available variables</summary>"
            u"<table class='table table-sm'>"
            u"<thead><tr><th style='width:30%'>Variable</th>"
            u"<th>Description</th></tr></thead>"
            u"<tbody>"
            u"<tr><td><code>{seq}</code> / <code>{seq:04d}</code></td>"
            u"<td>Numeric sequence number, optionally zero-padded.</td></tr>"
            u"<tr><td><code>{alpha:NaNd}</code></td>"
            u"<td>Alphanumeric counter, e.g. <code>{alpha:2a3d}</code> "
            u"yields AA001, AA002, ..., AB001, ...</td></tr>"
            u"<tr><td><code>{year}</code></td>"
            u"<td>Two-digit current year (e.g. <code>26</code>).</td></tr>"
            u"<tr><td><code>{yymmdd}</code></td>"
            u"<td>Current date as <code>yymmdd</code>.</td></tr>"
            u"<tr><td><code>{clientId}</code></td>"
            u"<td>Client ID (samples only).</td></tr>"
            u"<tr><td><code>{sampleType}</code></td>"
            u"<td>Sample type prefix.</td></tr>"
            u"<tr><td><code>{samplingDate}</code> / "
            u"<code>{dateSampled}</code></td>"
            u"<td>Sample dates (Python <code>strftime</code> specs apply).</td></tr>"
            u"<tr><td><code>{parent_ar_id}</code> / "
            u"<code>{parent_base_id}</code></td>"
            u"<td>For partitions/retests/secondaries: the parent sample ID.</td></tr>"
            u"<tr><td><code>{partition_count}</code></td>"
            u"<td>Per-parent partition counter.</td></tr>"
            u"<tr><td><code>{retest_count}</code> / "
            u"<code>{secondary_count}</code> / "
            u"<code>{test_count}</code></td>"
            u"<td>Counters for retests, secondaries, and total tests.</td></tr>"
            u"</tbody></table>"
            u"</details>"
            u"<details class='id-server-cheatsheet'>"
            u"<summary>Configuration fields</summary>"
            u"<ul>"
            u"<li><strong>Format</strong>: the ID template.</li>"
            u"<li><strong>Seq Type</strong>: "
            u"<code>generated</code> uses the persistent number counter; "
            u"<code>counter</code> uses the count of related objects.</li>"
            u"<li><strong>Context</strong>: only used by <code>counter</code> "
            u"type; the named context the counter applies to.</li>"
            u"<li><strong>Counter Type</strong>: "
            u"<code>backreference</code> (deprecated) or "
            u"<code>contained</code>.</li>"
            u"<li><strong>Counter Ref</strong>: relationship name "
            u"(backreference) or meta type (contained).</li>"
            u"<li><strong>Prefix</strong>: default prefix if none in the "
            u"format.</li>"
            u"<li><strong>Split Length</strong>: how many segments of the "
            u"format become the storage key prefix. Determines how the "
            u"counter is partitioned (e.g. per year, per sample type).</li>"
            u"</ul>"
            u"</details>"
            u"<style>"
            u".id-server-cheatsheet { margin: 0.5em 0; }"
            u".id-server-cheatsheet > summary { cursor: pointer; "
            u"font-weight: 600; padding: 0.25em 0; }"
            u".id-server-cheatsheet table { margin-top: 0.5em; }"
            u"</style>"
        ),
        value_type=DataGridRow(schema=IIDFormattingRecordSchema),
        required=False,
        default=DEFAULT_ID_FORMATTING,
    )

    ###
    # Fieldsets
    ###
    model.fieldset(
        "security",
        label=_(u"Security"),
        fields=[
            "auto_log_off",
            "restrict_worksheet_users_access",
            "allow_to_submit_not_assigned",
            "restrict_worksheet_management",
            "enable_global_auditlog",
        ]
    )

    model.fieldset(
        "accounting",
        label=_(u"Accounting"),
        fields=[
            "show_prices",
            "currency",
            "default_country",
            "member_discount",
            "vat",
        ]
    )

    model.fieldset(
        "results_reports",
        label=_(u"Results Reports"),
        fields=[
            "decimal_mark",
            "scientific_notation_report",
            "minimum_results",
        ]
    )

    model.fieldset(
        "analyses",
        label=_(u"Analyses"),
        fields=[
            "categorise_analysis_services",
            "categorize_sample_analyses",
            "sample_analyses_required",
            "allow_manual_result_capture_date",
            "enable_ar_specs",
            "exponential_format_threshold",
            "immediate_results_entry",
            "enable_analysis_remarks",
            "auto_verify_samples",
            "self_verification_enabled",
            "number_of_required_verifications",
            "type_of_multi_verification",
            "results_decimal_mark",
            "scientific_notation_results",
            "enable_rejection_workflow",
            "rejection_reasons",
            "default_number_of_ars_to_add",
            "max_number_of_samples_add",
            "sampleview_analysis_columns_order",
            "worksheetview_analysis_columns_order",
        ]
    )

    model.fieldset(
        "appearance",
        label=_(u"Appearance"),
        fields=[
            "worksheet_layout",
            "show_partitions",
            "site_logo",
            "site_logo_css",
            "show_lab_name_in_login",
            "sidebar_folders",
            "sidebar_navigation_depth",
            "sidebar_skip_types",
        ]
    )

    model.fieldset(
        "sampling",
        label=_(u"Sampling"),
        fields=[
            "sample_duplicate_enabled",
            "printing_workflow_enabled",
            "sampling_workflow_enabled",
            "schedule_sampling_enabled",
            "date_sampled_required",
            "autoreceive_samples",
            "sample_preservation_enabled",
            "workdays",
            "default_turnaround_time",
            "default_sample_lifetime",
        ]
    )

    model.fieldset(
        "notifications",
        label=_(u"Notifications"),
        fields=[
            "email_from_sample_publication",
            "email_body_sample_publication",
            "always_cc_responsibles_in_report_emails",
            "notify_on_sample_rejection",
            "email_body_sample_rejection",
            "invalidation_reason_required",
            "email_body_sample_invalidation",
        ]
    )

    model.fieldset(
        "sticker",
        label=_(u"Sticker"),
        fields=[
            "auto_print_stickers",
            "auto_sticker_template",
            "small_sticker_template",
            "large_sticker_template",
            "default_number_of_copies",
        ]
    )

    model.fieldset(
        "id_server",
        label=_(u"ID Server"),
        fields=[
            "id_formatting",
        ]
    )

    @invariant
    def validate_id_formatting(data):  # noqa: pylint:disable=no-self-argument
        """Validate the IDFormatting entries.

        Note: ``@invariant`` functions take the form data wrapper, not
        a regular ``self``; the parameter name follows the
        zope.interface convention.

        - Each `form` value must parse as a Python format string.
        - No duplicate `portal_type` entries (the second one would be
          shadowed by the first at lookup time).
        """
        records = getattr(data, "id_formatting", None) or []
        seen_types = {}
        for idx, record in enumerate(records, start=1):
            portal_type = (_record_get(record, "portal_type") or "").strip()
            form_str = _record_get(record, "form") or ""
            if portal_type:
                conflict = seen_types.get(portal_type)
                if conflict:
                    raise Invalid(_(
                        u"Duplicate ID format for portal type "
                        u"'${pt}' (rows ${a} and ${b}). Only the first "
                        u"row is used; remove or merge the duplicate.",
                        mapping={"pt": portal_type, "a": conflict,
                                 "b": idx}))
                seen_types[portal_type] = idx
            if form_str:
                try:
                    list(string.Formatter().parse(form_str))
                except (ValueError, IndexError) as exc:
                    raise Invalid(_(
                        u"Invalid ID format on row ${i} "
                        u"('${pt}'): ${err}",
                        mapping={"i": idx, "pt": portal_type or "",
                                 "err": str(exc)}))


@implementer(ISetup, ISetupSchema, IHideActionsMenu)
class Setup(Container):
    """SENAITE Setup Folder
    """
    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getEmailFromSamplePublication(self):
        """Returns the 'From' address for publication emails
        """
        accessor = self.accessor("email_from_sample_publication")
        email = accessor(self)
        if not email:
            email = default_email_from_sample_publication(self)
        return email

    @security.protected(permissions.ModifyPortalContent)
    def setEmailFromSamplePublication(self, value):
        """Set the 'From' address for publication emails
        """
        mutator = self.mutator("email_from_sample_publication")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEmailBodySamplePublication(self):
        """Returns the transformed email body text for publication emails
        """
        accessor = self.accessor("email_body_sample_publication")
        value = accessor(self)
        if IRichTextValue.providedBy(value):
            # Transforms the raw value to the output mimetype
            value = value.output_relative_to(self)
        if not value:
            # Always fallback to default value
            value = default_email_body_sample_publication(self)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setEmailBodySamplePublication(self, value):
        """Set email body text for publication emails
        """
        mutator = self.mutator("email_body_sample_publication")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAlwaysCCResponsiblesInReportEmail(self):
        """Returns if responsibles should always receive publication emails
        """
        accessor = self.accessor("always_cc_responsibles_in_report_emails")
        return accessor(self)

    @security.protected(permissions.View)
    def setAlwaysCCResponsiblesInReportEmail(self, value):
        """Set if responsibles should always receive publication emails
        """
        mutator = self.mutator("always_cc_responsibles_in_report_emails")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEnableGlobalAuditlog(self):
        """Returns if the global Auditlog is enabled
        """
        accessor = self.accessor("enable_global_auditlog")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEnableGlobalAuditlog(self, value):
        """Enable/Disable global Auditlogging
        """
        if value is False:
            # clear the auditlog catalog
            catalog = api.get_tool(AUDITLOG_CATALOG)
            catalog.manage_catalogClear()
        mutator = self.mutator("enable_global_auditlog")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSiteLogo(self):
        """Returns the global site logo
        """
        accessor = self.accessor("site_logo")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteLogo(self, value):
        """Set the site logo
        """
        mutator = self.mutator("site_logo")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSiteLogoCSS(self):
        """Returns the global site logo
        """
        accessor = self.accessor("site_logo_css")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteLogoCSS(self, value):
        """Set the site logo
        """
        mutator = self.mutator("site_logo_css")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getImmediateResultsEntry(self):
        """Returns if immediate results entry is enabled or not
        """
        accessor = self.accessor("immediate_results_entry")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setImmediateResultsEntry(self, value):
        """Enable/Disable global Auditlogging
        """
        mutator = self.mutator("immediate_results_entry")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getCategorizeSampleAnalyses(self):
        """Returns if analyses should be grouped by category for samples
        """
        accessor = self.accessor("categorize_sample_analyses")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCategorizeSampleAnalyses(self, value):
        """Enable/Disable grouping of analyses by category for samples
        """
        mutator = self.mutator("categorize_sample_analyses")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSampleAnalysesRequired(self):
        """Returns if analyses are required in sample add form
        """
        accessor = self.accessor("sample_analyses_required")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleAnalysesRequired(self, value):
        """Allow/Disallow to create samples without analyses
        """
        mutator = self.mutator("sample_analyses_required")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAllowManualResultCaptureDate(self):
        """Returns if analyses are required in sample add form
        """
        accessor = self.accessor("allow_manual_result_capture_date")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAllowManualResultCaptureDate(self, value):
        """Allow/Disallow to create samples without analyses
        """
        mutator = self.mutator("allow_manual_result_capture_date")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDateSampledRequired(self):
        """Returns whether the DateSampled field is required on sample creation
        when the sampling workflow is not active
        """
        accessor = self.accessor("date_sampled_required")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDateSampledRequired(self, value):
        """Sets whether the entry of a value for DateSampled field on sample
        creation is required when the sampling workflow is not active
        """
        mutator = self.mutator("date_sampled_required")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getShowLabNameInLogin(self):
        """Returns if the laboratory name has to be displayed in login page
        """
        accessor = self.accessor("show_lab_name_in_login")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShowLabNameInLogin(self, value):
        """Show/hide the laboratory name in the login page
        """
        mutator = self.mutator("show_lab_name_in_login")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSidebarFolders(self):
        """Returns the sidebar navigation folders
        """
        accessor = self.accessor("sidebar_folders")
        return accessor(self) or ()

    @security.protected(permissions.ModifyPortalContent)
    def setSidebarFolders(self, value):
        """Set the sidebar navigation folders
        """
        mutator = self.mutator("sidebar_folders")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSidebarNavigationDepth(self):
        """Returns the sidebar navigation depth
        """
        accessor = self.accessor("sidebar_navigation_depth")
        depth = accessor(self)
        return depth if depth is not None else 3

    @security.protected(permissions.ModifyPortalContent)
    def setSidebarNavigationDepth(self, value):
        """Set the sidebar navigation depth
        """
        mutator = self.mutator("sidebar_navigation_depth")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSidebarSkipTypes(self):
        """Returns the sidebar skipped portal types
        """
        accessor = self.accessor("sidebar_skip_types")
        return accessor(self) or ()

    @security.protected(permissions.ModifyPortalContent)
    def setSidebarSkipTypes(self, value):
        """Set the sidebar skipped portal types
        """
        mutator = self.mutator("sidebar_skip_types")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getInvalidationReasonRequired(self):
        """Returns whether the introduction of a reason is required when
        invalidating a sample
        """
        accessor = self.accessor("invalidation_reason_required")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setInvalidationReasonRequired(self, value):
        """Set whether the introduction of a reason is required when
        invalidating a sample
        """
        mutator = self.mutator("invalidation_reason_required")
        return mutator(self, value)

    # Auto Log Off - special handling with session timeout
    @security.protected(permissions.View)
    def getAutoLogOff(self):
        """Get session lifetime in minutes
        """
        acl = api.get_tool("acl_users")
        session = acl.get("session")
        if not session:
            return 0
        return session.timeout // 60

    @security.protected(permissions.ModifyPortalContent)
    def setAutoLogOff(self, value):
        """Set session lifetime in minutes
        """
        value = api.to_int(value, default=0)
        if value < 0:
            value = 0
        value = value * 60
        acl = api.get_tool("acl_users")
        session = acl.get("session")
        if session:
            session.timeout = value
        mutator = self.mutator("auto_log_off")
        return mutator(self, value // 60)

    # Security fields
    @security.protected(permissions.View)
    def getRestrictWorksheetUsersAccess(self):
        """Get restrict worksheet users access setting
        """
        accessor = self.accessor("restrict_worksheet_users_access")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRestrictWorksheetUsersAccess(self, value):
        """Set restrict worksheet users access setting
        """
        mutator = self.mutator("restrict_worksheet_users_access")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAllowToSubmitNotAssigned(self):
        """Get allow to submit not assigned setting
        """
        accessor = self.accessor("allow_to_submit_not_assigned")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAllowToSubmitNotAssigned(self, value):
        """Set allow to submit not assigned setting
        """
        mutator = self.mutator("allow_to_submit_not_assigned")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getRestrictWorksheetManagement(self):
        """Get restrict worksheet management setting
        """
        accessor = self.accessor("restrict_worksheet_management")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRestrictWorksheetManagement(self, value):
        """Set restrict worksheet management setting
        """
        mutator = self.mutator("restrict_worksheet_management")
        return mutator(self, value)

    # Accounting fields
    @security.protected(permissions.View)
    def getShowPrices(self):
        """Get show prices setting
        """
        accessor = self.accessor("show_prices")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShowPrices(self, value):
        """Set show prices setting
        """
        mutator = self.mutator("show_prices")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getCurrency(self):
        """Get currency setting
        """
        accessor = self.accessor("currency")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCurrency(self, value):
        """Set currency setting
        """
        mutator = self.mutator("currency")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDefaultCountry(self):
        """Get default country setting
        """
        accessor = self.accessor("default_country")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDefaultCountry(self, value):
        """Set default country setting
        """
        mutator = self.mutator("default_country")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getMemberDiscount(self):
        """Get member discount percentage
        Returns string value, defaults to "0.0" if empty
        """
        accessor = self.accessor("member_discount")
        value = accessor(self)
        # Convert to string if numeric (from AT FixedPointField)
        if value is None or value == "":
            return u"0.0"
        if isinstance(value, (int, float)):
            return api.safe_unicode(str(value))
        return api.safe_unicode(value)

    @security.protected(permissions.ModifyPortalContent)
    def setMemberDiscount(self, value):
        """Set member discount percentage
        Accepts string or numeric value
        """
        # Convert numeric to string
        if value is not None and not isinstance(value, basestring):
            value = api.safe_unicode(str(value))
        elif value:
            value = api.safe_unicode(value)
        else:
            value = u""
        mutator = self.mutator("member_discount")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getVAT(self):
        """Get VAT percentage
        Returns string value, defaults to "0.0" if empty
        """
        accessor = self.accessor("vat")
        value = accessor(self)
        # Convert to string if numeric (from AT FixedPointField)
        if value is None or value == "":
            return u"0.0"
        if isinstance(value, (int, float)):
            return api.safe_unicode(str(value))
        return api.safe_unicode(value)

    @security.protected(permissions.ModifyPortalContent)
    def setVAT(self, value):
        """Set VAT percentage
        Accepts string or numeric value
        """
        # Convert numeric to string
        if value is not None and not isinstance(value, basestring):
            value = api.safe_unicode(str(value))
        elif value:
            value = api.safe_unicode(value)
        else:
            value = u""
        mutator = self.mutator("vat")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDecimalMark(self):
        """Get decimal mark for reports
        """
        accessor = self.accessor("decimal_mark")
        value = accessor(self)
        # Return default if value is empty
        return value or "."

    @security.protected(permissions.ModifyPortalContent)
    def setDecimalMark(self, value):
        """Set decimal mark for reports
        """
        mutator = self.mutator("decimal_mark")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getScientificNotationReport(self):
        """Get scientific notation format for reports
        """
        accessor = self.accessor("scientific_notation_report")
        value = accessor(self)
        # Return default if value is empty
        return value or "1"

    @security.protected(permissions.ModifyPortalContent)
    def setScientificNotationReport(self, value):
        """Set scientific notation format for reports
        """
        mutator = self.mutator("scientific_notation_report")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getMinimumResults(self):
        """Get minimum number of results for QC stats
        """
        accessor = self.accessor("minimum_results")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setMinimumResults(self, value):
        """Set minimum number of results for QC stats
        Converts to int if needed
        """
        value = api.to_int(value, default=None)
        mutator = self.mutator("minimum_results")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getCategoriseAnalysisServices(self):
        """Get categorise analysis services setting
        """
        accessor = self.accessor("categorise_analysis_services")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCategoriseAnalysisServices(self, value):
        """Set categorise analysis services setting
        """
        mutator = self.mutator("categorise_analysis_services")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEnableARSpecs(self):
        """Get enable AR specs setting
        """
        accessor = self.accessor("enable_ar_specs")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEnableARSpecs(self, value):
        """Set enable AR specs setting
        """
        mutator = self.mutator("enable_ar_specs")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getExponentialFormatThreshold(self):
        """Get exponential format threshold
        """
        accessor = self.accessor("exponential_format_threshold")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setExponentialFormatThreshold(self, value):
        """Set exponential format threshold
        Converts to int if needed
        """
        value = api.to_int(value, default=None)
        mutator = self.mutator("exponential_format_threshold")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEnableAnalysisRemarks(self):
        """Get enable analysis remarks setting
        """
        accessor = self.accessor("enable_analysis_remarks")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEnableAnalysisRemarks(self, value):
        """Set enable analysis remarks setting
        """
        mutator = self.mutator("enable_analysis_remarks")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAutoVerifySamples(self):
        """Get auto verify samples setting
        """
        accessor = self.accessor("auto_verify_samples")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAutoVerifySamples(self, value):
        """Set auto verify samples setting
        """
        mutator = self.mutator("auto_verify_samples")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSelfVerificationEnabled(self):
        """Get self verification enabled setting
        """
        accessor = self.accessor("self_verification_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSelfVerificationEnabled(self, value):
        """Set self verification enabled setting
        """
        mutator = self.mutator("self_verification_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getNumberOfRequiredVerifications(self):
        """Get number of required verifications
        Returns 1 (default) if not set
        """
        accessor = self.accessor("number_of_required_verifications")
        value = accessor(self)
        # Return default of 1 if not set
        if value is None:
            return 1
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setNumberOfRequiredVerifications(self, value):
        """Set number of required verifications
        """
        mutator = self.mutator("number_of_required_verifications")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getTypeOfmultiVerification(self):
        """Get type of multi verification
        """
        accessor = self.accessor("type_of_multi_verification")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setTypeOfmultiVerification(self, value):
        """Set type of multi verification
        """
        mutator = self.mutator("type_of_multi_verification")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getResultsDecimalMark(self):
        """Get decimal mark for results
        """
        accessor = self.accessor("results_decimal_mark")
        value = accessor(self)
        # Return default if value is empty
        return value or "."

    @security.protected(permissions.ModifyPortalContent)
    def setResultsDecimalMark(self, value):
        """Set decimal mark for results
        """
        mutator = self.mutator("results_decimal_mark")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getScientificNotationResults(self):
        """Get scientific notation format for results
        """
        accessor = self.accessor("scientific_notation_results")
        value = accessor(self)
        # Return default if value is empty
        return value or "1"

    @security.protected(permissions.ModifyPortalContent)
    def setScientificNotationResults(self, value):
        """Set scientific notation format for results
        """
        mutator = self.mutator("scientific_notation_results")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDefaultNumberOfARsToAdd(self):
        """Get default number of ARs to add
        """
        accessor = self.accessor("default_number_of_ars_to_add")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDefaultNumberOfARsToAdd(self, value):
        """Set default number of ARs to add
        Converts to int if needed
        """
        value = api.to_int(value, default=None)
        mutator = self.mutator("default_number_of_ars_to_add")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEnableRejectionWorkflow(self):
        """Get enable rejection workflow
        """
        accessor = self.accessor("enable_rejection_workflow")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEnableRejectionWorkflow(self, value):
        """Set enable rejection workflow
        """
        mutator = self.mutator("enable_rejection_workflow")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getRejectionReasons(self):
        """Get rejection reasons
        Returns a list of unicode strings. The v02_07_000 upgrade step
        converts old AT RecordsField data to this format.
        """
        accessor = self.accessor("rejection_reasons")
        reasons = accessor(self)
        if not reasons:
            return []
        # Ensure all reasons are unicode
        return [api.safe_unicode(r) for r in reasons]

    @security.protected(permissions.ModifyPortalContent)
    def setRejectionReasons(self, value):
        """Set rejection reasons
        Accepts a simple list of strings (DX format).
        The v02_07_000 upgrade step handles AT→DX conversion before calling
        this setter, so no format conversion is needed here.
        """
        # Ensure all values are unicode
        if value and isinstance(value, (list, tuple)):
            value = [api.safe_unicode(v) for v in value if v]
        else:
            value = []
        mutator = self.mutator("rejection_reasons")
        return mutator(self, value)

    @deprecate("Method is kept for backwards compatibility only")
    def getRejectionReasonsItems(self):
        """Return the list of predefined rejection reasons

        .. deprecated::
            Use getRejectionReasons() instead. This method is kept for
            backwards compatibility only and will be removed in a future
            version.
        """
        return self.getRejectionReasons()

    @security.protected(permissions.View)
    def getMaxNumberOfSamplesAdd(self):
        """Get maximum number of samples to add
        """
        accessor = self.accessor("max_number_of_samples_add")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setMaxNumberOfSamplesAdd(self, value):
        """Set maximum number of samples to add
        Converts to int if needed
        """
        value = api.to_int(value, default=None)
        mutator = self.mutator("max_number_of_samples_add")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSampleviewAnalysisColumnsOrder(self):
        """Returns the sample view analysis columns order
        """
        accessor = self.accessor(
            "sampleview_analysis_columns_order"
        )
        return accessor(self) or ()

    @security.protected(permissions.ManagePortal)
    def setSampleviewAnalysisColumnsOrder(self, value):
        """Set the sample view analysis columns order
        """
        mutator = self.mutator(
            "sampleview_analysis_columns_order"
        )
        return mutator(self, value)

    @security.protected(permissions.View)
    def getWorksheetviewAnalysisColumnsOrder(self):
        """Returns the worksheet view analysis columns order
        """
        accessor = self.accessor(
            "worksheetview_analysis_columns_order"
        )
        return accessor(self) or ()

    @security.protected(permissions.ManagePortal)
    def setWorksheetviewAnalysisColumnsOrder(self, value):
        """Set the worksheet view analysis columns order
        """
        mutator = self.mutator(
            "worksheetview_analysis_columns_order"
        )
        return mutator(self, value)

    @security.protected(permissions.View)
    def getWorksheetLayout(self):
        """Get worksheet layout
        """
        accessor = self.accessor("worksheet_layout")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setWorksheetLayout(self, value):
        """Set worksheet layout
        """
        mutator = self.mutator("worksheet_layout")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getShowPartitions(self):
        """Get show partitions setting
        """
        accessor = self.accessor("show_partitions")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShowPartitions(self, value):
        """Set show partitions setting
        """
        mutator = self.mutator("show_partitions")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSampleDuplicateEnabled(self):
        """Get allow sample duplicate setting
        """
        accessor = self.accessor("sample_duplicate_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleDuplicateEnabled(self, value):
        """Set allow sample duplicate setting
        """
        mutator = self.mutator("sample_duplicate_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getPrintingWorkflowEnabled(self):
        """Get printing workflow enabled setting
        """
        accessor = self.accessor("printing_workflow_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPrintingWorkflowEnabled(self, value):
        """Set printing workflow enabled setting
        """
        mutator = self.mutator("printing_workflow_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSamplingWorkflowEnabled(self):
        """Get sampling workflow enabled setting
        """
        accessor = self.accessor("sampling_workflow_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSamplingWorkflowEnabled(self, value):
        """Set sampling workflow enabled setting
        """
        mutator = self.mutator("sampling_workflow_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getScheduleSamplingEnabled(self):
        """Get schedule sampling enabled setting
        """
        accessor = self.accessor("schedule_sampling_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setScheduleSamplingEnabled(self, value):
        """Set schedule sampling enabled setting
        """
        mutator = self.mutator("schedule_sampling_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAutoreceiveSamples(self):
        """Get autoreceive samples setting
        """
        accessor = self.accessor("autoreceive_samples")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAutoreceiveSamples(self, value):
        """Set autoreceive samples setting
        """
        mutator = self.mutator("autoreceive_samples")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSamplePreservationEnabled(self):
        """Get sample preservation enabled setting
        """
        accessor = self.accessor("sample_preservation_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSamplePreservationEnabled(self, value):
        """Set sample preservation enabled setting
        """
        mutator = self.mutator("sample_preservation_enabled")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getWorkdays(self):
        """Get laboratory workdays
        """
        accessor = self.accessor("workdays")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setWorkdays(self, value):
        """Set laboratory workdays
        """
        mutator = self.mutator("workdays")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDefaultTurnaroundTime(self):
        """Get default turnaround time
        """
        accessor = self.accessor("default_turnaround_time")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDefaultTurnaroundTime(self, value):
        """Set default turnaround time
        """
        # Handle both dict (from AT) and timedelta (from DX) formats
        if isinstance(value, dict):
            value = dtime.to_timedelta(value)
        mutator = self.mutator("default_turnaround_time")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDefaultSampleLifetime(self):
        """Get default sample lifetime
        """
        accessor = self.accessor("default_sample_lifetime")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDefaultSampleLifetime(self, value):
        """Set default sample lifetime
        """
        # Handle both dict (from AT) and timedelta (from DX) formats
        if isinstance(value, dict):
            value = dtime.to_timedelta(value)
        mutator = self.mutator("default_sample_lifetime")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getNotifyOnSampleRejection(self):
        """Get notify on sample rejection setting
        """
        accessor = self.accessor("notify_on_sample_rejection")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setNotifyOnSampleRejection(self, value):
        """Set notify on sample rejection setting
        """
        mutator = self.mutator("notify_on_sample_rejection")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEmailBodySampleRejection(self):
        """Returns the transformed email body text for rejection emails
        """
        accessor = self.accessor("email_body_sample_rejection")
        value = accessor(self)
        if IRichTextValue.providedBy(value):
            # Transforms the raw value to the output mimetype
            value = value.output_relative_to(self)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setEmailBodySampleRejection(self, value):
        """Set email body for sample rejection
        """
        mutator = self.mutator("email_body_sample_rejection")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEmailBodySampleInvalidation(self):
        """Returns the transformed email body text for invalidation emails
        """
        accessor = self.accessor("email_body_sample_invalidation")
        value = accessor(self)
        if IRichTextValue.providedBy(value):
            # Transforms the raw value to the output mimetype
            value = value.output_relative_to(self)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setEmailBodySampleInvalidation(self, value):
        """Set email body for sample invalidation
        """
        mutator = self.mutator("email_body_sample_invalidation")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAutoPrintStickers(self):
        """Get auto print stickers setting
        Returns "None" (string) if not set
        """
        accessor = self.accessor("auto_print_stickers")
        value = accessor(self)
        # Return "None" string as default if not set
        if value is None:
            return "None"
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setAutoPrintStickers(self, value):
        """Set auto print stickers setting
        """
        mutator = self.mutator("auto_print_stickers")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAutoStickerTemplate(self):
        """Get auto sticker template
        """
        accessor = self.accessor("auto_sticker_template")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAutoStickerTemplate(self, value):
        """Set auto sticker template
        """
        mutator = self.mutator("auto_sticker_template")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSmallStickerTemplate(self):
        """Get small sticker template
        """
        accessor = self.accessor("small_sticker_template")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSmallStickerTemplate(self, value):
        """Set small sticker template
        """
        mutator = self.mutator("small_sticker_template")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getLargeStickerTemplate(self):
        """Get large sticker template
        """
        accessor = self.accessor("large_sticker_template")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLargeStickerTemplate(self, value):
        """Set large sticker template
        """
        mutator = self.mutator("large_sticker_template")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDefaultNumberOfCopies(self):
        """Get default number of copies
        """
        accessor = self.accessor("default_number_of_copies")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDefaultNumberOfCopies(self, value):
        """Set default number of copies
        Converts to int if needed
        """
        value = api.to_int(value, default=None)
        mutator = self.mutator("default_number_of_copies")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getIDFormatting(self):
        """Get ID formatting configuration
        Normalizes None values to empty strings for Choice fields
        Ensures string values are returned as byte strings (not unicode)
        """
        accessor = self.accessor("id_formatting")
        value = accessor(self)
        if not value:
            return DEFAULT_ID_FORMATTING

        # Normalize values: convert `None` to empty strings
        # In Python 2: convert unicode to bytes to prevent `UnicodeDecodeError`
        # when formatting with UTF-8 encoded values
        # In Python 3: keep strings as unicode (no conversion needed)
        normalized = []
        for row in value:
            normalized_row = {}
            for key, val in row.items():
                if val is None:
                    normalized_row[key] = ""
                elif six.PY2 and isinstance(val, six.text_type):
                    normalized_row[key] = val.encode("utf-8")
                else:
                    normalized_row[key] = val
            normalized.append(normalized_row)

        return normalized

    @security.protected(permissions.ModifyPortalContent)
    def setIDFormatting(self, value):
        """Set ID formatting configuration
        Normalizes None values to empty strings for Choice fields
        """
        if value:
            # Normalize None values to empty strings for Choice fields
            normalized = []
            for row in value:
                normalized_row = dict(row)
                # Convert None to empty string for Choice fields
                if normalized_row.get("sequence_type") is None:
                    normalized_row["sequence_type"] = ""
                if normalized_row.get("counter_type") is None:
                    normalized_row["counter_type"] = ""
                # Convert None to empty string for text fields
                for key in ["context", "counter_reference", "prefix",
                            "portal_type", "form"]:
                    if normalized_row.get(key) is None:
                        normalized_row[key] = ""
                # Ensure split_length is an int
                split_length = normalized_row.get("split_length")
                split_length_int = api.to_int(split_length, default=1)
                normalized_row["split_length"] = max(split_length_int, 1)
                normalized.append(normalized_row)
            value = normalized

        mutator = self.mutator("id_formatting")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getIDServerValues(self):
        """Get current ID server values
        This is a computed field - returns current counter values
        """
        from senaite.core.interfaces import INumberGenerator
        number_generator = getUtility(INumberGenerator)
        keys = number_generator.keys()
        values = number_generator.values()
        results = []
        for i in range(len(keys)):
            results.append("{}: {}".format(keys[i], values[i]))
        return "\n".join(results)

    @security.protected(permissions.View)
    def getIDServerValuesHTML(self):
        """Get current ID server values as HTML
        Alias for backwards compatibility with AT BikaSetup
        """
        return self.getIDServerValues()

    @security.protected(permissions.View)
    def isRejectionWorkflowEnabled(self):
        """Return true if the rejection workflow is enabled
        """
        return self.getEnableRejectionWorkflow()
