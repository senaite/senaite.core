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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Field import TextField
from Products.Archetypes.Widget import RichWidget
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import DecimalWidget
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import InAndOutWidget
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import registerType
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import RejectionSetupWidget
from bika.lims.config import ATTACHMENT_OPTIONS
from bika.lims.config import CURRENCIES
from bika.lims.config import WEEKDAYS
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import MULTI_VERIFICATION_TYPE
from bika.lims.config import PROJECTNAME
from bika.lims.config import SCINOTATION_OPTIONS
from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSetup
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.locales import COUNTRIES
from bika.lims.numbergenerator import INumberGenerator
from bika.lims.vocabularies import getStickerTemplates as _getStickerTemplates
from plone.app.folder import folder
from zope.component import getUtility
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
        'PasswordLifetime',
        schemata="Security",
        required=1,
        default=0,
        widget=IntegerWidget(
            label=_("Password lifetime"),
            description=_("The number of days before a password expires. 0 disables password expiry"),
        )
    ),
    IntegerField(
        'AutoLogOff',
        schemata="Security",
        required=1,
        default=0,
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
        widget=BooleanWidget(
            label=_("Allow access to worksheets only to assigned analysts"),
            description=_("If unchecked, analysts will have access to all worksheets.")
        )
    ),
    BooleanField(
        'AllowToSubmitNotAssigned',
        schemata="Security",
        default=True,
        widget=BooleanWidget(
            label=_("Allow to submit results for unassigned analyses or for "
                    "analyses assigned to others"),
            description=_(
                "If unchecked, users will only be able to submit results "
                "for the analyses they are assigned to, and the submission of "
                "results for unassigned analyses won't be permitted. This "
                "setting does not apply to users with role Lab Manager")
        )
    ),
    BooleanField(
        'RestrictWorksheetManagement',
        schemata="Security",
        default=True,
        widget=BooleanWidget(
            label=_("Only lab managers can create and manage worksheets"),
            description=_("If unchecked, analysts and lab clerks will "
                          "be able to manage Worksheets, too. If the "
                          "users have restricted access only to those "
                          "worksheets for which they are assigned, "
                          "this option will be checked and readonly.")
        )
    ),
    BooleanField(
        'ShowPrices',
        schemata="Accounting",
        default=True,
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
        widget=BooleanWidget(
            label=_("Categorise analysis services"),
            description=_("Group analysis services by category in the LIMS tables, helpful when the list is long")
        ),
    ),
    BooleanField(
        'EnableARSpecs',
        schemata="Analyses",
        default=False,
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
        'EnableAnalysisRemarks',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Add a remarks field to all analyses"),
            description=_(
                "If enabled, a free text field will be displayed close to "
                "each analysis in results entry view"
            )
        ),
    ),
    BooleanField(
        'SelfVerificationEnabled',
        schemata="Analyses",
        default=False,
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
        'ARAttachmentOption',
        schemata="Analyses",
        default='p',
        vocabulary=ATTACHMENT_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("Sample Attachment Option"),
            description=_(
                "The system wide default configuration to indicate "
                "whether file attachments are required, permitted or not "
                "per sample"),
        )
    ),
    StringField(
        'AnalysisAttachmentOption',
        schemata="Analyses",
        default='p',
        vocabulary=ATTACHMENT_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("Analysis Attachment Option"),
            description=_(
                "Same as the above, but sets the default on analysis services. "
                "This setting can be set per individual analysis on its "
                "own configuration"),
        )
    ),
    StringField(
        'ResultsDecimalMark',
        schemata="Analyses",
        vocabulary=DECIMAL_MARKS,
        default=".",
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
        widget=SelectionWidget(
            label=_("Default scientific notation format for results"),
            description=_("Preferred scientific notation format for results"),
            format='select',
        )
    ),
    StringField(
        'WorksheetLayout',
        schemata="Appearance",
        default='1',
        vocabulary=WORKSHEET_LAYOUT_OPTIONS,
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
        widget=BooleanWidget(
            label=_("Use Dashboard as default front page"),
            description=_("Select this to activate the dashboard as a default front page.")
        ),
    ),
    ReferenceField(
        'LandingPage',
        schemata="Appearance",
        multiValued=0,
        allowed_types=('Document', ),
        relationship='SetupLandingPage',
        widget=ReferenceBrowserWidget(
            label=_("Landing Page"),
            description=_("The selected landing page is displayed for non-authenticated users "
                          "and if the Dashboard is not selected as the default front page. "
                          "If no landing page is selected, the default Bika frontpage is displayed."),
            allow_search=1,
            allow_browse=1,
            startup_directory='/',
            force_close_on_insert=1,
            default_search_index='SearchableText',
            base_query={'review_state': 'published'},
        ),
    ),
    BooleanField(
        'PrintingWorkflowEnabled',
        schemata="Sampling",
        default=False,
        widget=BooleanWidget(
            label=_("Enable the Results Report Printing workflow"),
            description=_("Select this to allow the user to set an "
                          "additional 'Printed' status to those Analysis "
                          "Requests tha have been Published. "
                          "Disabled by default.")
        ),
    ),
    BooleanField(
        'SamplingWorkflowEnabled',
        schemata="Sampling",
        default=False,
        widget=BooleanWidget(
            label=_("Enable Sampling"),
            description=_("Select this to activate the sample collection workflow steps.")
        ),
    ),
    BooleanField(
        'ScheduleSamplingEnabled',
        schemata="Sampling",
        default=False,
        widget=BooleanWidget(
            label=_("Enable Sampling Scheduling"),
            description=_(
                "Select this to allow a Sampling Coordinator to" +
                " schedule a sampling. This functionality only takes effect" +
                " when 'Sampling workflow' is active")
        ),
    ),
    BooleanField(
        "AutoreceiveSamples",
        schemata="Sampling",
        default=False,
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
        widget=BooleanWidget(
            label=_("Enable Sample Partitioning"),
            description=_(
                "Select to enable the partitioning module. An additional "
                "transition 'Create Partitions' will be available for samples "
                "in received status")
        ),
    ),
    BooleanField(
        'SamplePreservationEnabled',
        schemata="Sampling",
        default=False,
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
        widget=DurationWidget(
            label=_("Default sample retention period"),
            description=_(
                "The number of days before a sample expires and cannot be analysed "
                "any more. This setting can be overwritten per individual sample type "
                "in the sample types setup"),
        )
    ),
    BooleanField(
        'NotifyOnSampleRejection',
        schemata="Notifications",
        default=False,
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
    BooleanField(
        'NotifyOnSampleInvalidation',
        schemata="Notifications",
        default=True,
        widget=BooleanWidget(
            label=_("Email notification on Sample invalidation"),
            description=_("Select this to activate automatic notifications "
                          "via email to the Client and Lab Managers when a "
                          "Sample is invalidated.")
        ),
    ),
    TextField(
        "EmailBodySampleInvalidation",
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        schemata="Notifications",
        label=_("Email body for Sample Invalidation notifications"),
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
        widget=RichWidget(
            label=_("Email body for Sample Invalidation notifications"),
            description=_("Set the text for the body of the email to be sent, "
                          ", if option 'Email notification on Sample "
                          "'invalidation' enabled,  to the Sample's client "
                          "contact. You can use reserved keywords: $sample_id, "
                          "$sample_link, $retest_id, $retest_link, "
                          "$lab_address"),
            default_mime_type='text/x-rst',
            output_mime_type='text/x-html',
            allow_file_upload=False,
            rows=15,
        ),
    ),
    StringField(
        'AutoPrintStickers',
        schemata="Sticker",
        vocabulary=STICKER_AUTO_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("Automatic sticker printing"),
            description=_(
                "Select 'Register' if you want stickers to be automatically printed when "
                "new Samples or sample records are created. Select 'Receive' to print stickers "
                "when Samples or Samples are received. Select 'None' to disable automatic printing"),
        )
    ),
    StringField(
        'AutoStickerTemplate',
        schemata="Sticker",
        vocabulary="getStickerTemplates",
        widget=SelectionWidget(
            format='select',
            label=_("Sticker templates"),
            description=_("Select which sticker to print when automatic sticker printing is enabled"),
        )
    ),
    StringField(
        'SmallStickerTemplate',
        schemata="Sticker",
        vocabulary="getStickerTemplates",
        default="Code_128_1x48mm.pt",
        widget=SelectionWidget(
            format='select',
            label=_("Small sticker"),
            description=_("Select which sticker should be used as the 'small' sticker by default")
        )
    ),
    StringField(
        'LargeStickerTemplate',
        schemata="Sticker",
        vocabulary="getStickerTemplates",
        default="Code_128_1x72mm.pt",
        widget=SelectionWidget(
            format='select',
            label=_("Large sticker"),
            description=_("Select which sticker should be used as the 'large' sticker by default")
        )
    ),
    IntegerField(
        'DefaultNumberOfCopies',
        schemata="Sticker",
        required="1",
        default="1",
        widget=IntegerWidget(
            label=_("Number of copies"),
            description=_("Set the default number of copies to be printed for each sticker")
        )
    ),
    IDFormattingField(
        'IDFormatting',
        schemata="ID Server",
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
                " <p>The Bika LIMS ID Server provides unique sequential IDs "
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
                "<tr><td>Client</td><td>{client}</td></tr>"
                "<tr><td>Year</td><td>{year}</td></tr>"
                "<tr><td>Date</td><td>{yymmdd}</td></tr>"
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
                " variables like sampleId, client, sampleType.</li>"
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
    RecordsField(
        'RejectionReasons',
        schemata="Analyses",
        widget=RejectionSetupWidget(
            label=_("Enable the rejection workflow"),
            description=_("Select this to activate the rejection workflow "
                          "for Samples. A 'Reject' option will be displayed in "
                          "the actions menu.")
        ),
    ),
    IntegerField(
        'DefaultNumberOfARsToAdd',
        schemata="Analyses",
        required=0,
        default=4,
        widget=IntegerWidget(
            label=_("Default count of Sample to add."),
            description=_("Default value of the 'Sample count' when users click 'ADD' button to create new Samples"),
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
    implements(IBikaSetup, IHaveNoBreadCrumbs)

    schema = schema
    security = ClassSecurityInfo()

    def getAttachmentsPermitted(self):
        """Attachments permitted
        """
        if self.getARAttachmentOption() in ['r', 'p'] \
           or self.getAnalysisAttachmentOption() in ['r', 'p']:
            return True
        else:
            return False

    def getStickerTemplates(self):
        """Get the sticker templates
        """
        out = [[t['id'], t['title']] for t in _getStickerTemplates()]
        return DisplayList(out)

    def getARAttachmentsPermitted(self):
        """AR attachments permitted
        """
        if self.getARAttachmentOption() == 'n':
            return False
        else:
            return True

    def getAnalysisAttachmentsPermitted(self):
        """Analysis attachments permitted
        """
        if self.getAnalysisAttachmentOption() == 'n':
            return False
        else:
            return True

    def getAnalysisServicesVocabulary(self):
        """
        Get all active Analysis Services from Bika Setup and return them as Display List.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
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
        items = [(x['ISO'], x['Country']) for x in COUNTRIES]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    def isRejectionWorkflowEnabled(self):
        """Return true if the rejection workflow is enabled (its checkbox is set)
        """
        widget = self.getRejectionReasons()
        # widget will be something like:
        # [{'checkbox': u'on', 'textfield-2': u'b', 'textfield-1': u'c', 'textfield-0': u'a'}]
        if len(widget) > 0:
            checkbox = widget[0].get('checkbox', False)
            return True if checkbox == 'on' and len(widget[0]) > 1 else False
        else:
            return False

    def getRejectionReasonsItems(self):
        """Return the list of predefined rejection reasons
        """
        reasons = self.getRejectionReasons()
        if not reasons:
            return []
        reasons = reasons[0]
        keys = filter(lambda key: key != "checkbox", reasons.keys())
        return map(lambda key: reasons[key], sorted(keys)) or []

    def _getNumberOfRequiredVerificationsVocabulary(self):
        """
        Returns a DisplayList with the available options for the
        multi-verification list: '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
            multi-verification list
        """
        items = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))

    def getIDServerValuesHTML(self):
        number_generator = getUtility(INumberGenerator)
        keys = number_generator.keys()
        values = number_generator.values()
        results = []
        for i in range(len(keys)):
            results.append('%s: %s' % (keys[i], values[i]))
        return "\n".join(results)


registerType(BikaSetup, PROJECTNAME)
