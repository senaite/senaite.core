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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets.decimal import DecimalWidget
from bika.lims.browser.worksheet.tools import getWorksheetLayouts
from bika.lims.config import CURRENCIES
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import DEFAULT_WORKSHEET_LAYOUT
from bika.lims.config import MULTI_VERIFICATION_TYPE
from bika.lims.config import PROJECTNAME
from bika.lims.config import SCINOTATION_OPTIONS
from bika.lims.config import WEEKDAYS
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSetup
from plone.app.folder import folder
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import InAndOutWidget
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import registerType
from Products.Archetypes.Field import TextField
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.Archetypes.Widget import RichWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.utils import getToolByName
from senaite.core.api import geo
from senaite.core.browser.fields.records import RecordsField
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.p3compat import cmp
from zope.interface import implements


class IDFormattingField(RecordsField):
    """A list of prefixes per portal_type
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type': 'prefixes',
        'subfields': (
            'portal_type',
            'form',
            'sequence_type',
            'context',
            'counter_type',
            'counter_reference',
            'prefix',
            'split_length'
        ),
        'subfield_labels': {
            'portal_type': 'Portal Type',
            'form': 'Format',
            'sequence_type': 'Seq Type',
            'context': 'Context',
            'counter_type': 'Counter Type',
            'counter_reference': 'Counter Ref',
            'prefix': 'Prefix',
            'split_length': 'Split Length',
        },
        'subfield_readonly': {
            'portal_type': False,
            'form': False,
            'sequence_type': False,
            'context': False,
            'counter_type': False,
            'counter_reference': False,
            'prefix': False,
            'split_length': False,
        },
        'subfield_sizes': {
            'portal_type': 20,
            'form': 30,
            'sequence_type': 1,
            'context': 12,
            'counter_type': 1,
            'counter_reference': 12,
            'prefix': 12,
            'split_length': 5,
        },
        'subfield_types': {
            'sequence_type': 'selection',
            'counter_type': 'selection',
            'split_length': 'int',
        },
        'subfield_vocabularies': {
            'sequence_type': 'getSequenceTypes',
            'counter_type': 'getCounterTypes',
        },
        'subfield_maxlength': {
            'form': 256,
        },
    })

    security = ClassSecurityInfo()

    def getSequenceTypes(self, instance=None):
        return DisplayList([
            ('', ''),
            ('counter', 'Counter'),
            ('generated', 'Generated')
        ])

    def getCounterTypes(self, instance=None):
        return DisplayList([
            ('', ''),
            ('backreference', 'Backreference'),
            ('contained', 'Contained')
        ])


STICKER_AUTO_OPTIONS = DisplayList((
    ('None', _('None')),
    ('register', _('Register')),
    ('receive', _('Receive')),
))


schema = BikaFolderSchema.copy() + Schema((
    IntegerField(
        'AutoLogOff',
        schemata="Security",
        required=1,
        default=0,
        accessor="getAutoLogOff",
        edit_accessor="getAutoLogOff",
        mutator="setAutoLogOff",
        widget=IntegerWidget(
            label=_("Automatic log-off"),
            description=_(
                "The number of minutes before a user is automatically logged off. "
                "0 disables automatic log-off"),
        )
    ),
    BooleanField(
        'RestrictWorksheetUsersAccess',
        schemata="Security",
        default=True,
        accessor="getRestrictWorksheetUsersAccess",
        edit_accessor="getRestrictWorksheetUsersAccess",
        mutator="setRestrictWorksheetUsersAccess",
        widget=BooleanWidget(
            label=_("Restrict worksheet access to assigned analysts"),
            description=_("When enabled, analysts can only access worksheets to "
                          "which they are assigned. When disabled, analysts have "
                          "access to all worksheets.")
        )
    ),
    BooleanField(
        'AllowToSubmitNotAssigned',
        schemata="Security",
        default=True,
        accessor="getAllowToSubmitNotAssigned",
        edit_accessor="getAllowToSubmitNotAssigned",
        mutator="setAllowToSubmitNotAssigned",
        widget=BooleanWidget(
            label=_("Allow submission of results for unassigned analyses"),
            description=_(
                "When enabled, users can submit results for analyses not "
                "assigned to them or for unassigned analyses. When disabled, "
                "users can only submit results for analyses assigned to "
                "themselves. This setting does not apply to users with role "
                "Lab Manager.")
        )
    ),
    BooleanField(
        'RestrictWorksheetManagement',
        schemata="Security",
        default=True,
        accessor="getRestrictWorksheetManagement",
        edit_accessor="getRestrictWorksheetManagement",
        mutator="setRestrictWorksheetManagement",
        widget=BooleanWidget(
            label=_("Restrict worksheet management to lab managers"),
            description=_("When enabled, only lab managers can create and manage "
                          "worksheets. When disabled, analysts and lab clerks can "
                          "also manage worksheets. Note: This setting is "
                          "automatically enabled and locked when worksheet access "
                          "is restricted to assigned analysts.")
        )
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    BooleanField(
        "EnableGlobalAuditlog",
        schemata="Security",
        default=False,
        accessor="getEnableGlobalAuditlog",
        edit_accessor="getEnableGlobalAuditlog",
        mutator="setEnableGlobalAuditlog",
        widget=BooleanWidget(
            label=_("Enable global Audit Log"),
            description=_(
                "The global Auditlog shows all modifications of the system. "
                "When enabled, all entities will be indexed in a separate "
                "catalog. This will increase the time when objects are "
                "created or modified."
            )
        )
    ),
    BooleanField(
        'ShowPrices',
        schemata="Accounting",
        default=True,
        accessor="getShowPrices",
        edit_accessor="getShowPrices",
        mutator="setShowPrices",
        widget=BooleanWidget(
            label=_("Include and display pricing information"),
        )
    ),
    StringField(
        'Currency',
        schemata="Accounting",
        required=1,
        vocabulary=CURRENCIES,
        default='EUR',
        accessor="getCurrency",
        edit_accessor="getCurrency",
        mutator="setCurrency",
        widget=SelectionWidget(
            label=_("Currency"),
            description=_("Select the currency the site will use to display prices."),
            format='select',
        )
    ),
    StringField(
        'DefaultCountry',
        schemata="Accounting",
        required=1,
        vocabulary='getCountries',
        default='',
        accessor="getDefaultCountry",
        edit_accessor="getDefaultCountry",
        mutator="setDefaultCountry",
        widget=SelectionWidget(
            label=_("Country"),
            description=_("Select the country the site will show by default"),
            format='select',
        )
    ),
    FixedPointField(
        'MemberDiscount',
        schemata="Accounting",
        default='33.33',
        accessor="getMemberDiscount",
        edit_accessor="getMemberDiscount",
        mutator="setMemberDiscount",
        widget=DecimalWidget(
            label=_("Member discount %"),
            description=_(
                "The discount percentage entered here, is applied to the prices for clients "
                "flagged as 'members', normally co-operative members or associates deserving "
                "of this discount"),
        )
    ),
    FixedPointField(
        'VAT',
        schemata="Accounting",
        default='19.00',
        accessor="getVAT",
        edit_accessor="getVAT",
        mutator="setVAT",
        widget=DecimalWidget(
            label=_("VAT %"),
            description=_(
                "Enter percentage value eg. 14.0. This percentage is applied system wide "
                "but can be overwrittem on individual items"),
        )
    ),
    StringField(
        'DecimalMark',
        schemata="Results Reports",
        vocabulary=DECIMAL_MARKS,
        default=".",
        accessor="getDecimalMark",
        edit_accessor="getDecimalMark",
        mutator="setDecimalMark",
        widget=SelectionWidget(
            label=_("Default decimal mark"),
            description=_("Preferred decimal mark for reports."),
            format='select',
        )
    ),
    StringField(
        'ScientificNotationReport',
        schemata="Results Reports",
        default='1',
        vocabulary=SCINOTATION_OPTIONS,
        accessor="getScientificNotationReport",
        edit_accessor="getScientificNotationReport",
        mutator="setScientificNotationReport",
        widget=SelectionWidget(
            label=_("Default scientific notation format for reports"),
            description=_("Preferred scientific notation format for reports"),
            format='select',
        )
    ),
    IntegerField(
        'MinimumResults',
        schemata="Results Reports",
        required=1,
        default=5,
        accessor="getMinimumResults",
        edit_accessor="getMinimumResults",
        mutator="setMinimumResults",
        widget=IntegerWidget(
            label=_("Minimum number of results for QC stats calculations"),
            description=_(
                "Using too few data points does not make statistical sense. "
                "Set an acceptable minimum number of results before QC statistics "
                "will be calculated and plotted"),
        )
    ),
    BooleanField(
        'CategoriseAnalysisServices',
        schemata="Analyses",
        default=False,
        accessor="getCategoriseAnalysisServices",
        edit_accessor="getCategoriseAnalysisServices",
        mutator="setCategoriseAnalysisServices",
        widget=BooleanWidget(
            label=_("Categorise analysis services"),
            description=_("Group analysis services by category in the LIMS tables, helpful when the list is long")
        ),
    ),
    BooleanField(
        "CategorizeSampleAnalyses",
        schemata="Analyses",
        default=False,
        accessor="getCategorizeSampleAnalyses",
        edit_accessor="getCategorizeSampleAnalyses",
        mutator="setCategorizeSampleAnalyses",
        widget=BooleanWidget(
            label=_("label_bikasetup_categorizesampleanalyses",
                    default="Categorize sample analyses"),
            description=_("description_bikasetup_categorizesampleanalyses",
                          "Group analyses by category for samples")
        ),
    ),
    BooleanField(
        "SampleAnalysesRequired",
        schemata="Analyses",
        default=True,
        accessor="getSampleAnalysesRequired",
        edit_accessor="getSampleAnalysesRequired",
        mutator="setSampleAnalysesRequired",
        widget=BooleanWidget(
            label=_("label_bikasetup_sampleanalysesrequired",
                    default="Require sample analyses"),
            description=_("description_bikasetup_sampleanalysesrequired",
                          "Analyses are required for sample registration")
        ),
    ),
    BooleanField(
        "AllowManualResultCaptureDate",
        schemata="Analyses",
        default=True,
        accessor="getAllowManualResultCaptureDate",
        edit_accessor="getAllowManualResultCaptureDate",
        mutator="setAllowManualResultCaptureDate",
        widget=BooleanWidget(
            label=_("label_bikasetup_allow_manual_result_capture_date",
                    default="Allow to set the result capture date"),
            description=_(
                "description_bikasetup_allow_manual_result_capture_date",
                default="If this option is activated, the result capture date "
                        "can be entered manually for analyses"),
        ),
    ),
    BooleanField(
        'EnableARSpecs',
        schemata="Analyses",
        default=False,
        accessor="getEnableARSpecs",
        edit_accessor="getEnableARSpecs",
        mutator="setEnableARSpecs",
        widget=BooleanWidget(
            label=_("Enable Sample Specifications"),
            description=_(
                "Analysis specifications which are edited directly on the "
                "Sample."),
        ),
    ),
    IntegerField(
        'ExponentialFormatThreshold',
        schemata="Analyses",
        required=1,
        default=7,
        accessor="getExponentialFormatThreshold",
        edit_accessor="getExponentialFormatThreshold",
        mutator="setExponentialFormatThreshold",
        widget=IntegerWidget(
            label=_("Exponential format threshold"),
            description=_(
                "Result values with at least this number of significant "
                "digits are displayed in scientific notation using the "
                "letter 'e' to indicate the exponent.  The precision can be "
                "configured in individual Analysis Services."),
        )
    ),
    BooleanField(
        "ImmediateResultsEntry",
        schemata="Analyses",
        default=False,
        accessor="getImmediateResultsEntry",
        edit_accessor="getImmediateResultsEntry",
        mutator="setImmediateResultsEntry",
        widget=BooleanWidget(
            label=_("label_bikasetup_immediateresultsentry",
                    default=u"Immediate results entry"),
            description=_(
                "description_bikasetup_immediateresultsentry",
                default=u"Allow the user to directly enter results after "
                "sample creation, e.g. to enter field results immediately, or "
                "lab results, when the automatic sample reception is "
                "activated."
            ),
        ),
    ),
    BooleanField(
        'EnableAnalysisRemarks',
        schemata="Analyses",
        default=False,
        accessor="getEnableAnalysisRemarks",
        edit_accessor="getEnableAnalysisRemarks",
        mutator="setEnableAnalysisRemarks",
        widget=BooleanWidget(
            label=_("Add a remarks field to all analyses"),
            description=_(
                "If enabled, a free text field will be displayed close to "
                "each analysis in results entry view"
            )
        ),
    ),
    BooleanField(
        "AutoVerifySamples",
        schemata="Analyses",
        default=True,
        accessor="getAutoVerifySamples",
        edit_accessor="getAutoVerifySamples",
        mutator="setAutoVerifySamples",
        widget=BooleanWidget(
            label=_("Automatic verification of samples"),
            description=_(
                "When enabled, the sample is automatically verified as soon as "
                "all results are verified. Otherwise, users with enough "
                "privileges have to manually verify the sample afterwards. "
                "Default: enabled"
            )
        )
    ),
    BooleanField(
        'SelfVerificationEnabled',
        schemata="Analyses",
        default=False,
        accessor="getSelfVerificationEnabled",
        edit_accessor="getSelfVerificationEnabled",
        mutator="setSelfVerificationEnabled",
        widget=BooleanWidget(
            label=_("Allow self-verification of results"),
            description=_(
                "If enabled, a user who submitted a result will also be able "
                "to verify it. This setting only take effect for those users "
                "with a role assigned that allows them to verify results "
                "(by default, managers, labmanagers and verifiers)."
                "This setting can be overrided for a given Analysis in "
                "Analysis Service edit view. By default, disabled."),
        ),
    ),
    IntegerField(
        'NumberOfRequiredVerifications',
        schemata="Analyses",
        default=1,
        vocabulary="_getNumberOfRequiredVerificationsVocabulary",
        accessor="getNumberOfRequiredVerifications",
        edit_accessor="getNumberOfRequiredVerifications",
        mutator="setNumberOfRequiredVerifications",
        widget=SelectionWidget(
            format="select",
            label=_("Number of required verifications"),
            description=_(
                "Number of required verifications before a given result being "
                "considered as 'verified'. This setting can be overrided for "
                "any Analysis in Analysis Service edit view. By default, 1"),
        ),
    ),
    StringField(
        'TypeOfmultiVerification',
        schemata="Analyses",
        default='self_multi_enabled',
        vocabulary=MULTI_VERIFICATION_TYPE,
        accessor="getTypeOfmultiVerification",
        edit_accessor="getTypeOfmultiVerification",
        mutator="setTypeOfmultiVerification",
        widget=SelectionWidget(
            label=_("Multi Verification type"),
            description=_(
                "Choose type of multiple verification for the same user."
                "This setting can enable/disable verifying/consecutively verifying"
                "more than once for the same user."),
            format='select',
        )
    ),
    StringField(
        'ResultsDecimalMark',
        schemata="Analyses",
        vocabulary=DECIMAL_MARKS,
        default=".",
        accessor="getResultsDecimalMark",
        edit_accessor="getResultsDecimalMark",
        mutator="setResultsDecimalMark",
        widget=SelectionWidget(
            label=_("Default decimal mark"),
            description=_("Preferred decimal mark for results"),
            format='select',
        )
    ),
    StringField(
        'ScientificNotationResults',
        schemata="Analyses",
        default='1',
        vocabulary=SCINOTATION_OPTIONS,
        accessor="getScientificNotationResults",
        edit_accessor="getScientificNotationResults",
        mutator="setScientificNotationResults",
        widget=SelectionWidget(
            label=_("Default scientific notation format for results"),
            description=_("Preferred scientific notation format for results"),
            format='select',
        )
    ),
    StringField(
        'WorksheetLayout',
        schemata="Appearance",
        default=DEFAULT_WORKSHEET_LAYOUT,
        vocabulary=getWorksheetLayouts(),
        accessor="getWorksheetLayout",
        edit_accessor="getWorksheetLayout",
        mutator="setWorksheetLayout",
        widget=SelectionWidget(
            label=_("Default layout in worksheet view"),
            description=_("Preferred layout of the results entry table "
                          "in the Worksheet view. Classic layout displays "
                          "the Samples in rows and the analyses "
                          "in columns. Transposed layout displays the "
                          "Samples in columns and the analyses "
                          "in rows."),
            format='select',
        )
    ),
    BooleanField(
        'DashboardByDefault',
        schemata="Appearance",
        default=True,
        accessor="getDashboardByDefault",
        edit_accessor="getDashboardByDefault",
        mutator="setDashboardByDefault",
        widget=BooleanWidget(
            label=_("Use Dashboard as default front page"),
            description=_("Select this to activate the dashboard as a default front page.")
        ),
    ),
    UIDReferenceField(
        "LandingPage",
        schemata="Appearance",
        required=0,
        allowed_types=(
            "Document",
            "Client",
            "ClientFolder",
            "Samples",
            "WorksheetFolder",
        ),
        mode="rw",
        multiValued=0,
        relationship="SetupLandingPage",
        accessor="getLandingPage",
        edit_accessor="getLandingPage",
        mutator="setLandingPage",
        widget=ReferenceWidget(
            label=_(
                "label_setup_landingpage",
                default="Landing Page"),
            description=_(
                "description_setup_landingpage",
                default="The landing page is shown for non-authenticated users "
                "if the Dashboard is not selected as the default front page. "
                "If no landing page is selected, the default frontpage is displayed."),
            catalog=["uid_catalog"],
            query={
                "is_active": True,
                "sort_on": "id",
                "sort_order": "ascending"
            },
            columns=[
                {"name": "Title", "label": _("Title")},
                {"name": "portal_type", "label": _("Type")},
            ],

        ),
    ),
    BooleanField(
        'PrintingWorkflowEnabled',
        schemata="Sampling",
        default=False,
        accessor="getPrintingWorkflowEnabled",
        edit_accessor="getPrintingWorkflowEnabled",
        mutator="setPrintingWorkflowEnabled",
        widget=BooleanWidget(
            label=_("Enable the Results Report Printing workflow"),
            description=_("Select this to allow the user to set an "
                          "additional 'Printed' status to those Analysis "
                          "Requests that have been Published. "
                          "Disabled by default.")
        ),
    ),
    BooleanField(
        'SamplingWorkflowEnabled',
        schemata="Sampling",
        default=False,
        accessor="getSamplingWorkflowEnabled",
        edit_accessor="getSamplingWorkflowEnabled",
        mutator="setSamplingWorkflowEnabled",
        widget=BooleanWidget(
            label=_("Enable Sampling"),
            description=_("Select this to activate the sample collection workflow steps.")
        ),
    ),
    BooleanField(
        'ScheduleSamplingEnabled',
        schemata="Sampling",
        default=False,
        accessor="getScheduleSamplingEnabled",
        edit_accessor="getScheduleSamplingEnabled",
        mutator="setScheduleSamplingEnabled",
        widget=BooleanWidget(
            label=_("Enable Sampling Scheduling"),
            description=_(
                "Select this to allow a Sampling Coordinator to" +
                " schedule a sampling. This functionality only takes effect" +
                " when 'Sampling workflow' is active")
        ),
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    BooleanField(
        "DateSampledRequired",
        schemata="Sampling",
        default=True,
        accessor="getDateSampledRequired",
        edit_accessor="getDateSampledRequired",
        mutator="setDateSampledRequired",
        widget=BooleanWidget(
            label=_(
                "label_bikasetup_date_sampled_required",
                default="Date sampled required"
            ),
            description=_(
                "description_bikasetup_date_sampled_required",
                default="Select this to make DateSampled field required on "
                        "sample creation. This functionality only takes "
                        "effect when 'Sampling workflow' is not active"
            ),
        ),
    ),
    BooleanField(
        "AutoreceiveSamples",
        schemata="Sampling",
        default=False,
        accessor="getAutoreceiveSamples",
        edit_accessor="getAutoreceiveSamples",
        mutator="setAutoreceiveSamples",
        widget=BooleanWidget(
            label=_("Auto-receive samples"),
            description=_(
                "Select to receive the samples automatically when created by "
                "lab personnel and sampling workflow is disabled. Samples "
                "created by client contacts won't be received automatically"
            ),
        ),
    ),
    BooleanField(
        'ShowPartitions',
        schemata="Appearance",
        default=False,
        accessor="getShowPartitions",
        edit_accessor="getShowPartitions",
        mutator="setShowPartitions",
        widget=BooleanWidget(
            label=_("Display sample partitions to clients"),
            description=_(
                "Select to show sample partitions to client contacts. "
                "If deactivated, partitions won't be included in listings "
                "and no info message with links to the primary sample will "
                "be displayed to client contacts.")
        ),
    ),
    BooleanField(
        'SamplePreservationEnabled',
        schemata="Sampling",
        default=False,
        accessor="getSamplePreservationEnabled",
        edit_accessor="getSamplePreservationEnabled",
        mutator="setSamplePreservationEnabled",
        widget=BooleanWidget(
            label=_("Enable Sample Preservation"),
            description=_("")
        ),
    ),
    LinesField(
        "Workdays",
        schemata="Sampling",
        vocabulary=WEEKDAYS,
        default=tuple(map(str, range(7))),
        required=1,
        accessor="getWorkdays",
        edit_accessor="getWorkdays",
        mutator="setWorkdays",
        widget=InAndOutWidget(
            visible=True,
            label=_("Laboratory Workdays"),
            description=_("Only laboratory workdays are considered for the "
                          "analysis turnaround time calculation. "),
            format="checkbox",
        )
    ),
    DurationField(
        'DefaultTurnaroundTime',
        schemata="Sampling",
        required=1,
        default={"days": 5, "hours": 0, "minutes": 0},
        accessor="getDefaultTurnaroundTime",
        edit_accessor="getDefaultTurnaroundTime",
        mutator="setDefaultTurnaroundTime",
        widget=DurationWidget(
            label=_("Default turnaround time for analyses."),
            description=_(
                "This is the default maximum time allowed for performing "
                "analyses.  It is only used for analyses where the analysis "
                "service does not specify a turnaround time. "
                "Only laboratory workdays are considered."
            ),
        )
    ),
    DurationField(
        'DefaultSampleLifetime',
        schemata="Sampling",
        required=1,
        default={"days": 30, "hours": 0, "minutes": 0},
        accessor="getDefaultSampleLifetime",
        edit_accessor="getDefaultSampleLifetime",
        mutator="setDefaultSampleLifetime",
        widget=DurationWidget(
            label=_("Default sample retention period"),
            description=_(
                "The number of days before a sample expires and cannot be analysed "
                "any more. This setting can be overwritten per individual sample type "
                "in the sample types setup"),
        )
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    StringField(
        "EmailFromSamplePublication",
        default_method='getEmailFromSamplePublication',
        schemata="Notifications",
        accessor="getEmailFromSamplePublication",
        edit_accessor="getEmailFromSamplePublication",
        mutator="setEmailFromSamplePublication",
        widget=StringWidget(
            label=_(
                "label_bikasetup_email_from_sample_publication",
                default="Publication 'From' address"
            ),
            description=_(
                "description_bikasetup_email_from_sample_publication",
                default="E-mail to use as the 'From' address for outgoing "
                        "e-mails when publishing results reports. This "
                        "address overrides the value set at portal's 'Mail "
                        "settings'."
            ),
        ),
        validators=("isEmail", )
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    TextField(
        "EmailBodySamplePublication",
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        schemata="Notifications",
        # Needed to fetch the default value from the registry
        accessor="getEmailBodySamplePublication",
        edit_accessor="getEmailBodySamplePublication",
        mutator="setEmailBodySamplePublication",
        widget=RichWidget(
            label=_(
                "label_bikasetup_email_body_sample_publication",
                "Email body for Sample publication notifications"),
            description=_(
                "description_bikasetup_email_body_sample_publication",
                default="Set the email body text to be used by default when "
                "sending out result reports to the selected recipients. "
                "You can use reserved keywords: "
                "$client_name, $recipients, $lab_name, $lab_address"),
            default_mime_type="text/x-html",
            output_mime_type="text/x-html",
            allow_file_upload=False,
            rows=15,
        ),
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    BooleanField(
        "AlwaysCCResponsiblesInReportEmail",
        schemata="Notifications",
        default=True,
        accessor="getAlwaysCCResponsiblesInReportEmail",
        edit_accessor="getAlwaysCCResponsiblesInReportEmail",
        mutator="setAlwaysCCResponsiblesInReportEmail",
        widget=BooleanWidget(
            label=_(
                "label_bikasetup_always_cc_responsibles_in_report_emails",
                default="Always send publication email to responsibles"),
            description=_(
                "description_bikasetup_always_cc_responsibles_in_report_emails",
                default="When selected, the responsible persons of all "
                "involved lab departments will receive publication emails."),
        ),
    ),
    BooleanField(
        'NotifyOnSampleRejection',
        schemata="Notifications",
        default=False,
        accessor="getNotifyOnSampleRejection",
        edit_accessor="getNotifyOnSampleRejection",
        mutator="setNotifyOnSampleRejection",
        widget=BooleanWidget(
            label=_("Email notification on Sample rejection"),
            description=_("Select this to activate automatic notifications "
                          "via email to the Client when a Sample is rejected.")
        ),
    ),
    TextField(
        "EmailBodySampleRejection",
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        schemata="Notifications",
        label=_("Email body for Sample Rejection notifications"),
        default="The sample $sample_link has been rejected because of the "
                "following reasons:"
                "<br/><br/>$reasons<br/><br/>"
                "For further information, please contact us under the "
                "following address.<br/><br/>"
                "$lab_address",
        accessor="getEmailBodySampleRejection",
        edit_accessor="getEmailBodySampleRejection",
        mutator="setEmailBodySampleRejection",
        widget=RichWidget(
            label=_("Email body for Sample Rejection notifications"),
            description=_(
                "Set the text for the body of the email to be sent to the "
                "Sample's client contact if the option 'Email notification on "
                "Sample rejection' is enabled. You can use reserved keywords: "
                "$sample_id, $sample_link, $reasons, $lab_address"),
            default_mime_type='text/x-rst',
            output_mime_type='text/x-html',
            allow_file_upload=False,
            rows=15,
        ),
    ),
    # NOTE: This is a Proxy Field which delegates to the SENAITE Registry!
    BooleanField(
        "InvalidationReasonRequired",
        schemata="Notifications",
        default=True,
        accessor="getInvalidationReasonRequired",
        edit_accessor="getInvalidationReasonRequired",
        mutator="setInvalidationReasonRequired",
        widget=BooleanWidget(
            label=_(
                "label_bikasetup_invalidation_reason_required",
                default="Invalidation reason required"
            ),
            description=_(
                "description_bikasetup_invalidation_reason_required",
                default="Specify whether providing a reason is mandatory when "
                        "invalidating a sample. If enabled, the '$reason' "
                        "placeholder in the sample invalidation notification "
                        "email body will be replaced with the entered reason."
            ),
        ),
    ),
    TextField(
        "EmailBodySampleInvalidation",
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        schemata="Notifications",
        default=
            "Some non-conformities have been detected in the results report "
            "published for Sample $sample_link. "
            "<br/><br/> "
            "A new Sample $retest_link has been created automatically, and the "
            "previous request has been invalidated. "
            "<br/><br/> "
            "The root cause is under investigation and corrective "
            "action has been initiated. "
            "<br/><br/> "
            "$lab_address",
        accessor="getEmailBodySampleInvalidation",
        edit_accessor="getEmailBodySampleInvalidation",
        mutator="setEmailBodySampleInvalidation",
        widget=RichWidget(
            label=_(
                "label_bikasetup_invalidation_email_body",
                default="Email body for Sample Invalidation notifications"
            ),
            description=_(
                "description_bikasetup_invalidation_email_body",
                default=
                "Define the template for the email body that will be "
                "automatically sent to primary contacts and laboratory "
                "managers when a sample is invalidated. The following "
                "placeholders are supported: "
                "<code title='The ID of the sample'>$sample_id</code>, "
                "<code title='The ID of the sample retest'>$retest_id</code>, "
                "<code title='The link to the retest'>$retest_link</code>, "
                "<code title='The reason(s) for invalidation'>$reason</code>, "
                "<code title='The address of the lab'>$lab_address</code>."
            ),
            default_mime_type='text/x-rst',
            output_mime_type='text/x-html',
            allow_file_upload=False,
            rows=15,
        ),
    ),

    StringField(
        "AutoPrintStickers",
        schemata="Sticker",
        vocabulary=STICKER_AUTO_OPTIONS,
        accessor="getAutoPrintStickers",
        edit_accessor="getAutoPrintStickers",
        mutator="setAutoPrintStickers",
        widget=SelectionWidget(
            format='select',
            label=_("Automatic Sticker Printing"),
            description=_(
                "Choose when stickers should be automatically printed:<br/>"
                "<ul>"
                "<li><strong>Register:</strong> Stickers are printed "
                " automatically when new samples are created.</li>"
                "<li><strong>Receive:</strong> Stickers are printed "
                " automatically when samples are received.</li>"
                "<li><strong>None:</strong> Disables automatic sticker "
                "printing.</li>"
                "</ul>"
            ),
        )
    ),

    StringField(
        "AutoStickerTemplate",
        schemata="Sticker",
        vocabulary_factory="senaite.core.vocabularies.stickers",
        accessor="getAutoStickerTemplate",
        edit_accessor="getAutoStickerTemplate",
        mutator="setAutoStickerTemplate",
        widget=SelectionWidget(
            format='select',
            label=_("Default Sticker Template"),
            description=_(
                "Select the default sticker template used for "
                "automatic printing.<br/>"
            ),
        )
    ),

    StringField(
        "SmallStickerTemplate",
        schemata="Sticker",
        vocabulary_factory="senaite.core.vocabularies.stickers",
        default="Code_128_1x48mm.pt",
        accessor="getSmallStickerTemplate",
        edit_accessor="getSmallStickerTemplate",
        mutator="setSmallStickerTemplate",
        widget=SelectionWidget(
            format='select',
            label=_("Small Sticker Template"),
            description=_(
                "Choose the default template for 'small' stickers.<br/>"
                "<strong>Note:</strong> Sample-specific 'small' stickers are "
                "configured based on their sample type."
            ),
        )
    ),

    StringField(
        "LargeStickerTemplate",
        schemata="Sticker",
        vocabulary_factory="senaite.core.vocabularies.stickers",
        default="Code_128_1x72mm.pt",
        accessor="getLargeStickerTemplate",
        edit_accessor="getLargeStickerTemplate",
        mutator="setLargeStickerTemplate",
        widget=SelectionWidget(
            format='select',
            label=_("Large Sticker Template"),
            description=_(
                "Choose the default template for 'large' stickers.<br/>"
                "<strong>Note:</strong> Sample-specific 'large' stickers are "
                "configured based on their sample type."
            ),
        )
    ),

    IntegerField(
        "DefaultNumberOfCopies",
        schemata="Sticker",
        required=True,
        default=1,
        accessor="getDefaultNumberOfCopies",
        edit_accessor="getDefaultNumberOfCopies",
        mutator="setDefaultNumberOfCopies",
        widget=IntegerWidget(
            label=_("Default Number of Copies"),
            description=_(
                "Specify how many copies of each sticker should be printed "
                "by default."
            ),
        )
    ),

    IDFormattingField(
        'IDFormatting',
        schemata="ID Server",
        accessor="getIDFormatting",
        edit_accessor="getIDFormatting",
        mutator="setIDFormatting",
        default=[
            {
                'form': 'B-{seq:03d}',
                'portal_type': 'Batch',
                'prefix': 'batch',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': 'D-{seq:03d}',
                'portal_type': 'DuplicateAnalysis',
                'prefix': 'duplicate',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': 'I-{seq:03d}',
                'portal_type': 'Invoice',
                'prefix': 'invoice',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': 'QC-{seq:03d}',
                'portal_type': 'ReferenceSample',
                'prefix': 'refsample',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': 'SA-{seq:03d}',
                'portal_type': 'ReferenceAnalysis',
                'prefix': 'refanalysis',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': 'WS-{seq:03d}',
                'portal_type': 'Worksheet',
                'prefix': 'worksheet',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': '{sampleType}-{seq:04d}',
                'portal_type': 'AnalysisRequest',
                'prefix': 'analysisrequest',
                'sequence_type': 'generated',
                'split_length': 1
            }, {
                'form': '{parent_ar_id}-P{partition_count:02d}',
                'portal_type': 'AnalysisRequestPartition',
                'prefix': 'analysisrequestpartition',
                'sequence_type': '',
                'split-length': 1
            }, {
                'form': '{parent_base_id}-R{retest_count:02d}',
                'portal_type': 'AnalysisRequestRetest',
                'prefix': 'analysisrequestretest',
                'sequence_type': '',
                'split-length': 1
            }, {
                'form': '{parent_ar_id}-S{secondary_count:02d}',
                'portal_type': 'AnalysisRequestSecondary',
                'prefix': 'analysisrequestsecondary',
                'sequence_type': '',
                'split-length': 1
            },
        ],
        widget=RecordsWidget(
            label=_("Formatting Configuration"),
            allowDelete=True,
            description=_(
                " <p>The ID Server provides unique sequential IDs "
                "for objects such as Samples and Worksheets etc, based on a "
                "format specified for each content type.</p>"
                "<p>The format is constructed similarly to the Python format"
                " syntax, using predefined variables per content type, and"
                " advancing the IDs through a sequence number, 'seq' and its"
                " padding as a number of digits, e.g. '03d' for a sequence of"
                " IDs from 001 to 999.</p>"
                "<p>Alphanumeric prefixes for IDs are included as is in the"
                " formats, e.g. WS for Worksheet in WS-{seq:03d} produces"
                " sequential Worksheet IDs: WS-001, WS-002, WS-003 etc.</p>"
                "<p>For dynamic generation of alphanumeric and sequential IDs,"
                " the wildcard {alpha} can be used. E.g WS-{alpha:2a3d}"
                " produces WS-AA001, WS-AA002, WS-AB034, etc.</p>"
                "<p>Variables that can be used include:"
                "<table>"
                "<tr>"
                "<th style='width:150px'>Content Type</th><th>Variables</th>"
                "</tr>"
                "<tr><td>Client ID</td><td>{clientId}</td></tr>"
                "<tr><td>Year</td><td>{year}</td></tr>"
                "<tr><td>Sample ID</td><td>{sampleId}</td></tr>"
                "<tr><td>Sample Type</td><td>{sampleType}</td></tr>"
                "<tr><td>Sampling Date</td><td>{samplingDate}</td></tr>"
                "<tr><td>Date Sampled</td><td>{dateSampled}</td></tr>"
                "</table>"
                "</p>"
                "<p>Configuration Settings:"
                "<ul>"
                "<li>format:"
                "<ul><li>a python format string constructed from predefined"
                " variables like sampleId, clientId, sampleType.</li>"
                "<li>special variable 'seq' must be positioned last in the"
                "format string</li></ul></li>"
                "<li>sequence type: [generated|counter]</li>"
                "<li>context: if type counter, provides context the counting"
                " function</li>"
                "<li>counter type: [backreference|contained]</li>"
                "<li>counter reference: a parameter to the counting"
                " function</li>"
                "<li>prefix: default prefix if none provided in format"
                " string</li>"
                "<li>split length: the number of parts to be included in the"
                " prefix</li>"
                "</ul></p>")
        )
    ),
    StringField(
        'IDServerValues',
        schemata="ID Server",
        accessor="getIDServerValuesHTML",
        readonly=True,
        widget=TextAreaWidget(
            label=_("ID Server Values"),
            cols=30,
            rows=30,
        ),
    ),
    LinesField(
        "RejectionReasons",
        schemata="Analyses",
        # NOTE: accessors/mutators needed to display the proxied values!
        accessor="getRejectionReasons",
        edit_accessor="getRejectionReasons",
        mutator="setRejectionReasons",
        widget=LinesWidget(
            label=_("Rejection Reasons"),
            description=_("List of predefined rejection reasons. "
                          "Enter one reason per line.")
        ),
    ),
    IntegerField(
        'DefaultNumberOfARsToAdd',
        schemata="Analyses",
        required=0,
        default=4,
        accessor="getDefaultNumberOfARsToAdd",
        edit_accessor="getDefaultNumberOfARsToAdd",
        mutator="setDefaultNumberOfARsToAdd",
        widget=IntegerWidget(
            label=_("Default count of Sample to add."),
            description=_("Default value of the 'Sample count' when users click 'ADD' button to create new Samples"),
        )
    ),
    IntegerField(
        "MaxNumberOfSamplesAdd",
        schemata="Analyses",
        required=0,
        default=10,
        accessor="getMaxNumberOfSamplesAdd",
        edit_accessor="getMaxNumberOfSamplesAdd",
        mutator="setMaxNumberOfSamplesAdd",
        widget=IntegerWidget(
            label=_(
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
        )
    ),
    # NOTE: This is a Proxy Field which delegates to senaite_setup DX
    BooleanField(
        "ShowLabNameInLogin",
        schemata="Appearance",
        default=False,
        accessor="getShowLabNameInLogin",
        edit_accessor="getShowLabNameInLogin",
        mutator="setShowLabNameInLogin",
        widget=BooleanWidget(
            label=_(
                u"title_senaitesetup_show_lab_name_in_login",
                default=u"Display laboratory name in the login page"),
            description=_(
                u"description_senaitesetup_show_lab_name_in_login",
                default=u"When selected, the laboratory name will be displayed"
                        u"in the login page, above the access credentials."
            ),
        )
    ),
))

schema['title'].validators = ()
schema['title'].widget.visible = False
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class BikaSetup(folder.ATFolder):
    """LIMS Setup
    """
    implements(IBikaSetup, IHideActionsMenu)

    schema = schema
    security = ClassSecurityInfo()

    def setAutoLogOff(self, value):
        """set session lifetime
        """
        value = int(value)
        if value < 0:
            value = 0
        value = value * 60
        acl = api.get_tool("acl_users")
        session = acl.get("session")
        if session:
            session.timeout = value

    def getAutoLogOff(self):
        """get session lifetime
        """
        acl = api.get_tool("acl_users")
        session = acl.get("session")
        if not session:
            return 0
        return session.timeout // 60

    def getAnalysisServicesVocabulary(self):
        """
        Get all active Analysis Services from Bika Setup and return them as Display List.
        """
        bsc = getToolByName(self, 'senaite_catalog_setup')
        brains = bsc(portal_type='AnalysisService',
                     is_active=True)
        items = [(b.UID, b.Title) for b in brains]
        items.insert(0, ("", ""))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getPrefixFor(self, portal_type):
        """Return the prefix for a portal_type.
           If not found, simply uses the portal_type itself
        """
        prefix = [p for p in self.getIDFormatting() if p['portal_type'] == portal_type]
        if prefix:
            return prefix[0]['prefix']
        else:
            return portal_type

    def getCountries(self):
        items = geo.get_countries()
        items = map(lambda country: (country.alpha_2, country.name), items)
        return items

    def isRejectionWorkflowEnabled(self):
        """Return true if the rejection workflow is enabled
        """
        return self.getEnableRejectionWorkflow()

    def getRejectionReasonsItems(self):
        """Return the list of predefined rejection reasons

        .. deprecated::
            This method now simply returns getRejectionReasons() as both
            return the same format (simple list). Kept for backwards
            compatibility.
        """
        return self.getRejectionReasons()

    def _getNumberOfRequiredVerificationsVocabulary(self):
        """
        Returns a DisplayList with the available options for the
        multi-verification list: '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
            multi-verification list
        """
        items = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))

    def getEmailFromSamplePublication(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEmailFromSamplePublication()

    def setEmailFromSamplePublication(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEmailFromSamplePublication(value)

    def getEmailBodySamplePublication(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEmailBodySamplePublication()

    def setEmailBodySamplePublication(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEmailBodySamplePublication(value)

    def getAlwaysCCResponsiblesInReportEmail(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAlwaysCCResponsiblesInReportEmail()

    def setAlwaysCCResponsiblesInReportEmail(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAlwaysCCResponsiblesInReportEmail(value)

    def getEnableGlobalAuditlog(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEnableGlobalAuditlog()
        return False

    def setEnableGlobalAuditlog(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEnableGlobalAuditlog(value)

    def getImmediateResultsEntry(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getImmediateResultsEntry()
        return False

    def setImmediateResultsEntry(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setImmediateResultsEntry(value)

    def getCategorizeSampleAnalyses(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getCategorizeSampleAnalyses()
        return False

    def setCategorizeSampleAnalyses(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setCategorizeSampleAnalyses(value)

    def getSampleAnalysesRequired(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getSampleAnalysesRequired()
        return False

    def setSampleAnalysesRequired(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setSampleAnalysesRequired(value)

    def getAllowManualResultCaptureDate(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAllowManualResultCaptureDate()
        return False

    def setAllowManualResultCaptureDate(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAllowManualResultCaptureDate(value)

    def getShowLabNameInLogin(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getShowLabNameInLogin()
        return False

    def setShowLabNameInLogin(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setShowLabNameInLogin(value)

    def getDateSampledRequired(self):
        """Get the value form the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getDateSampledRequired()
        return self.getField("DateSampledRequired").default

    def setDateSampledRequired(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setDateSampledRequired(value)

    def getInvalidationReasonRequired(self):
        """Get the value form the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getInvalidationReasonRequired()
        return self.getField("InvalidationReasonRequired").default

    def setInvalidationReasonRequired(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setInvalidationReasonRequired(value)

    # Proxy methods for Security fields
    def getRestrictWorksheetUsersAccess(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getRestrictWorksheetUsersAccess()

    def setRestrictWorksheetUsersAccess(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setRestrictWorksheetUsersAccess(value)

    def getAllowToSubmitNotAssigned(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getAllowToSubmitNotAssigned()

    def setAllowToSubmitNotAssigned(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setAllowToSubmitNotAssigned(value)

    def getRestrictWorksheetManagement(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getRestrictWorksheetManagement()

    def setRestrictWorksheetManagement(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setRestrictWorksheetManagement(value)

    # Proxy methods for Accounting fields
    def getShowPrices(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getShowPrices()

    def setShowPrices(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setShowPrices(value)

    def getCurrency(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getCurrency()

    def setCurrency(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setCurrency(value)

    def getDefaultCountry(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getDefaultCountry()

    def setDefaultCountry(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setDefaultCountry(value)

    def getMemberDiscount(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getMemberDiscount()

    def setMemberDiscount(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setMemberDiscount(value)

    def getVAT(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            return setup.getVAT()

    def setVAT(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        if setup:
            setup.setVAT(value)

    def getDecimalMark(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getDecimalMark()

    def setDecimalMark(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setDecimalMark(value)

    def getScientificNotationReport(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getScientificNotationReport()

    def setScientificNotationReport(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setScientificNotationReport(value)

    def getMinimumResults(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getMinimumResults()

    def setMinimumResults(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setMinimumResults(value)

    def getCategoriseAnalysisServices(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getCategoriseAnalysisServices()

    def setCategoriseAnalysisServices(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setCategoriseAnalysisServices(value)

    def getEnableARSpecs(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEnableARSpecs()

    def setEnableARSpecs(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEnableARSpecs(value)

    def getExponentialFormatThreshold(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getExponentialFormatThreshold()

    def setExponentialFormatThreshold(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setExponentialFormatThreshold(value)

    def getEnableAnalysisRemarks(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEnableAnalysisRemarks()

    def setEnableAnalysisRemarks(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEnableAnalysisRemarks(value)

    def getAutoVerifySamples(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAutoVerifySamples()

    def setAutoVerifySamples(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAutoVerifySamples(value)

    def getSelfVerificationEnabled(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getSelfVerificationEnabled()

    def setSelfVerificationEnabled(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setSelfVerificationEnabled(value)

    def getNumberOfRequiredVerifications(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getNumberOfRequiredVerifications()

    def setNumberOfRequiredVerifications(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setNumberOfRequiredVerifications(value)

    def getTypeOfmultiVerification(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getTypeOfmultiVerification()

    def setTypeOfmultiVerification(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setTypeOfmultiVerification(value)

    def getResultsDecimalMark(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getResultsDecimalMark()

    def setResultsDecimalMark(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setResultsDecimalMark(value)

    def getScientificNotationResults(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getScientificNotationResults()

    def setScientificNotationResults(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setScientificNotationResults(value)

    def getDefaultNumberOfARsToAdd(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getDefaultNumberOfARsToAdd()

    def setDefaultNumberOfARsToAdd(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setDefaultNumberOfARsToAdd(value)

    def getEnableRejectionWorkflow(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEnableRejectionWorkflow()
        return False

    def setEnableRejectionWorkflow(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEnableRejectionWorkflow(value)

    def getRejectionReasons(self):
        """Get the rejection reasons from senaite setup
        Returns a simple list of unicode strings
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getRejectionReasons()
        return []

    def setRejectionReasons(self, value):
        """Set the rejection reasons in senaite setup
        Accepts a simple list of strings
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setRejectionReasons(value)

    def getMaxNumberOfSamplesAdd(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getMaxNumberOfSamplesAdd()

    def setMaxNumberOfSamplesAdd(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setMaxNumberOfSamplesAdd(value)

    def getWorksheetLayout(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getWorksheetLayout()

    def setWorksheetLayout(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setWorksheetLayout(value)

    def getShowPartitions(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getShowPartitions()

    def setShowPartitions(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setShowPartitions(value)

    def getPrintingWorkflowEnabled(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getPrintingWorkflowEnabled()

    def setPrintingWorkflowEnabled(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setPrintingWorkflowEnabled(value)

    def getSamplingWorkflowEnabled(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getSamplingWorkflowEnabled()

    def setSamplingWorkflowEnabled(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setSamplingWorkflowEnabled(value)

    def getScheduleSamplingEnabled(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getScheduleSamplingEnabled()

    def setScheduleSamplingEnabled(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setScheduleSamplingEnabled(value)

    def getAutoreceiveSamples(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAutoreceiveSamples()

    def setAutoreceiveSamples(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAutoreceiveSamples(value)

    def getSamplePreservationEnabled(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getSamplePreservationEnabled()

    def setSamplePreservationEnabled(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setSamplePreservationEnabled(value)

    def getWorkdays(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getWorkdays()

    def setWorkdays(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setWorkdays(value)

    def getDefaultTurnaroundTime(self):
        """Get the value from the senaite setup
        """
        from senaite.core.api import dtime
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            value = setup.getDefaultTurnaroundTime()
            # Convert timedelta to dict for AT form
            return dtime.timedelta_to_dict(value, default={})
        return {}

    def setDefaultTurnaroundTime(self, value):
        """Set the value in the senaite setup
        """
        from senaite.core.api import dtime
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            # Convert dict to timedelta for DX storage
            td_value = dtime.to_timedelta(value, default=None)
            if td_value is not None:
                setup.setDefaultTurnaroundTime(td_value)

    def getDefaultSampleLifetime(self):
        """Get the value from the senaite setup
        """
        from senaite.core.api import dtime
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            value = setup.getDefaultSampleLifetime()
            # Convert timedelta to dict for AT form
            return dtime.timedelta_to_dict(value, default={})
        return {}

    def setDefaultSampleLifetime(self, value):
        """Set the value in the senaite setup
        """
        from senaite.core.api import dtime
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            # Convert dict to timedelta for DX storage
            td_value = dtime.to_timedelta(value, default=None)
            if td_value is not None:
                setup.setDefaultSampleLifetime(td_value)

    def getNotifyOnSampleRejection(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getNotifyOnSampleRejection()

    def setNotifyOnSampleRejection(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setNotifyOnSampleRejection(value)

    def getEmailBodySampleRejection(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEmailBodySampleRejection()

    def setEmailBodySampleRejection(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEmailBodySampleRejection(value)

    def getEmailBodySampleInvalidation(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getEmailBodySampleInvalidation()

    def setEmailBodySampleInvalidation(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setEmailBodySampleInvalidation(value)

    def getAutoPrintStickers(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAutoPrintStickers()

    def setAutoPrintStickers(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAutoPrintStickers(value)

    def getAutoStickerTemplate(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getAutoStickerTemplate()

    def setAutoStickerTemplate(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setAutoStickerTemplate(value)

    def getSmallStickerTemplate(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getSmallStickerTemplate()

    def setSmallStickerTemplate(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setSmallStickerTemplate(value)

    def getLargeStickerTemplate(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getLargeStickerTemplate()

    def setLargeStickerTemplate(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setLargeStickerTemplate(value)

    def getDefaultNumberOfCopies(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getDefaultNumberOfCopies()

    def setDefaultNumberOfCopies(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setDefaultNumberOfCopies(value)

    def getIDFormatting(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getIDFormatting()
        return []

    def setIDFormatting(self, value):
        """Set the value in the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            setup.setIDFormatting(value)

    def getIDServerValuesHTML(self):
        """Get the value from the senaite setup
        """
        setup = api.get_senaite_setup()
        # setup is `None` during initial site content structure installation
        if setup:
            return setup.getIDServerValuesHTML()
        return ""


registerType(BikaSetup, PROJECTNAME)
