# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import sys

from AccessControl import ClassSecurityInfo

from zope.interface import implements
from plone.app.folder import folder

from Products.CMFCore.utils import getToolByName
from Products.ATExtensions.ateapi import RecordsField

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import DecimalWidget
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import ReferenceWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.Archetypes.references import HoldingReference
from archetypes.referencebrowserwidget import ReferenceBrowserWidget

from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import RejectionSetupWidget
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSetup
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.vocabularies import getStickerTemplates as _getStickerTemplates

from bika.lims.config import ARIMPORT_OPTIONS
from bika.lims.config import ATTACHMENT_OPTIONS
from bika.lims.config import CURRENCIES
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import DEFAULT_AR_SPECS
from bika.lims.config import MULTI_VERIFICATION_TYPE
from bika.lims.config import PROJECTNAME
from bika.lims.config import SCINOTATION_OPTIONS
from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
from bika.lims.locales import COUNTRIES

from bika.lims import bikaMessageFactory as _


class PrefixesField(RecordsField):
    """A list of prefixes per portal_type
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type': 'prefixes',
        'subfields': ('portal_type', 'prefix', 'separator', 'padding', 'sequence_start'),
        'subfield_labels': {'portal_type': 'Portal type',
                            'prefix': 'Prefix',
                            'separator': 'Prefix Separator',
                            'padding': 'Padding',
                            'sequence_start': 'Sequence Start'},
        'subfield_readonly': {'portal_type': False,
                              'prefix': False,
                              'padding': False,
                              'separator': False,
                              'sequence_start': False},
        'subfield_sizes': {'portal_type': 32,
                           'prefix': 12,
                           'padding': 12,
                           'separator': 5,
                           'sequence_start': 12},
        'subfield_types': {'padding': 'int',
                           'sequence_start': 'int'},
    })

    security = ClassSecurityInfo()


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
        'AllowClerksToEditClients',
        schemata="Security",
        default=False,
        widget=BooleanWidget(
            label=_("Allow Lab Clerks to create and edit clients"),
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
        'ShowNewReleasesInfo',
        schemata="Security",
        default=True,
        widget=BooleanWidget(
            label=_("Display an alert on new releases of Bika LIMS"),
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
        default='ZAR',
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
        default='14.00',
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
        'IncludePreviousFromBatch',
        schemata="Results Reports",
        default=False,
        widget=BooleanWidget(
            label=_("Include Previous Results From Batch"),
            description=_(
                "If there are previous results for a service in the "
                "same batch of Analysis Requests, they will be displayed "
                "in the report.")
        )
    ),
    IntegerField(
        'BatchEmail',
        schemata="Results Reports",
        required=1,
        default=5,
        widget=IntegerWidget(
            label=_("Maximum columns per results email"),
            description=_(
                "Set the maximum number of analysis requests per results email. "
                "Too many columns per email are difficult to read for some clients "
                "who prefer fewer results per email"),
        )
    ),
    TextField(
        'ResultFooter',
        schemata="Results Reports",
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        default="",
        widget=TextAreaWidget(
            label=_("Result Footer"),
            description=_("This text will be appended to results reports."),
            append_only=False,
        ),
    ),
    # IntegerField('BatchFax',
    #     schemata = "Results Reports",
    #     required = 1,
    #     default = 4,
    #     widget = IntegerWidget(
    #         label=_("Maximum columns per results fax"),
    #         description = "Too many AR columns per fax will see the font size minimised and could "
    #                         "render faxes illegible. 4 ARs maximum per page is recommended",
    #     )
    # ),
    # StringField('SMSGatewayAddress',
    #     schemata = "Results Reports",
    #     required = 0,
    #     widget = StringWidget(
    #         label=_("SMS Gateway Email Address"),
    #         description = "The email to SMS gateway address. Either a complete email address, "
    #                         "or just the domain, e.g. '@2way.co.za', the contact's mobile phone "
    #                         "number will be prepended to",
    #     )
    # ),
    BooleanField(
        'PrintingWorkflowEnabled',
        schemata="Results Reports",
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
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Enable the Sampling workflow"),
            description=_("Select this to activate the sample collection workflow steps.")
        ),
    ),
    BooleanField(
        'ScheduleSamplingEnabled',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Enable the Schedule a Sampling functionality"),
            description=_(
                "Select this to allow a Sampling Coordinator to" +
                " schedule a sampling. This functionality only takes effect" +
                " when 'Sampling workflow' is active")
        ),
    ),
    BooleanField(
        'ShowPartitions',
        schemata="Analyses",
        default=True,
        widget=BooleanWidget(
            label=_("Display individual sample partitions "),
            description=_("Turn this on if you want to work with sample partitions")
        ),
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
        default=True,
        widget=BooleanWidget(
            label=_("Enable AR Specifications"),
            description=_(
                "Analysis specifications which are edited directly on the "
                "Analysis Request."),
        ),
    ),
    StringField(
        'DefaultARSpecs',
        schemata="Analyses",
        default='ar_specs',
        vocabulary=DEFAULT_AR_SPECS,
        widget=SelectionWidget(
            label=_("Default AR Specifications"),
            description=_(
                "Choose the default specifications used for all AR views "
                "to display alerts and notifications.  These will also be "
                "applied when an AR is published in permanent media, "
                "e.g. PDF."),
            format='select',
        )
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
            label=_("Number of required verifications"),
            description=_(
                "Number of required verifications before a given result being "
                "considered as 'verified'. This setting can be overrided for "
                "any Analysis in Analysis Service edit view. By default, 1"),
            format="select",
         ),
    ),
    StringField('TypeOfmultiVerification',
        schemata = "Analyses",
        default = 'self_multi_enabled',
        vocabulary = MULTI_VERIFICATION_TYPE,
        widget = SelectionWidget(
            label=_("Multi Verification type"),
            description = _(
                "Choose type of multiple verification for the same user."
                "This setting can enable/disable verifying/consecutively verifying"
                "more than once for the same user."),
            format='select',
        )
    ),
    ReferenceField(
        'DryMatterService',
        schemata="Analyses",
        required=0,
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('AnalysisService',),
        relationship='SetupDryAnalysisService',
        vocabulary='getAnalysisServicesVocabulary',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            label=_("Dry matter analysis"),
            description=_("The analysis to be used for determining dry matter."),
        )
    ),
    LinesField(
        'ARImportOption',
        schemata="Analyses",
        vocabulary=ARIMPORT_OPTIONS,
        widget=MultiSelectionWidget(
            visible=False,
            label=_("AR Import options"),
            description=_(
                "'Classic' indicates importing analysis requests per sample and "
                "analysis service selection. With 'Profiles', analysis profile keywords "
                "are used to select multiple analysis services together"),
        )
    ),
    StringField(
        'ARAttachmentOption',
        schemata="Analyses",
        default='p',
        vocabulary=ATTACHMENT_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("AR Attachment Option"),
            description=_(
                "The system wide default configuration to indicate "
                "whether file attachments are required, permitted or not "
                "per analysis request"),
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
    DurationField(
        'DefaultSampleLifetime',
        schemata="Analyses",
        required=1,
        default={"days": 30, "hours": 0, "minutes": 0},
        widget=DurationWidget(
            label=_("Default sample retention period"),
            description=_(
                "The number of days before a sample expires and cannot be "
                "analysed any more. This setting can be overwritten per "
                "individual sample type in the sample types setup"),
        )
    ),
    DurationField(
        'DefaultTurnaroundTime',
        schemata="Analyses",
        required=1,
        default={"days": 5, "hours": 0, "minutes": 0},
        widget=DurationWidget(
            label=_("Default turnaround time for analyses."),
            description=_(
                "This is the default maximum time allowed for performing "
                "analyses.  It is only used for analyses where the analysis "
                "service does not specify a turnaround time."),
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
    IntegerField(
        'AutoImportInterval',
        schemata="Analyses",
        default="0",
        widget=IntegerWidget(
            label=_("Interval of Auto-Importing Files in minutes"),
            description=_("System will upload result files of different \
                          instruments/interfaces periodically in the interval \
                          of this value (Minutes). Any value below 10, will \
                          disable Auto-Importing.")
        )
    ),
    StringField(
        'WorksheetLayout',
        schemata="Analyses",
        default='1',
        vocabulary=WORKSHEET_LAYOUT_OPTIONS,
        widget=SelectionWidget(
            label=_("Default layout in worksheet view"),
            description=_("Preferred layout of the results entry table "
                          "in the Worksheet view. Classic layout displays "
                          "the Analysis Requests in rows and the analyses "
                          "in columns. Transposed layout displays the "
                          "Analysis Requests in columns and the analyses "
                          "in rows."),
            format='select',
        )
    ),
    BooleanField(
        'DashboardByDefault',
        schemata="Analyses",
        default=True,
        widget=BooleanWidget(
            label=_("Use Dashboard as default front page"),
            description=_("Select this to activate the dashboard as a default front page.")
        ),
    ),
    ReferenceField(
        'LandingPage',
        schemata="Analyses",
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
    StringField(
        'AutoPrintStickers',
        schemata="Stickers",
        vocabulary=STICKER_AUTO_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("Automatic sticker printing"),
            description=_(
                "Select 'Register' if you want stickers to be automatically printed when "
                "new ARs or sample records are created. Select 'Receive' to print stickers "
                "when ARs or Samples are received. Select 'None' to disable automatic printing"),
        )
    ),
    StringField(
        'AutoStickerTemplate',
        schemata="Stickers",
        vocabulary="getStickerTemplates",
        widget=SelectionWidget(
            format='select',
            label=_("Sticker templates"),
            description=_("Select which sticker to print when automatic sticker printing is enabled"),
        )
    ),
    StringField(
        'SmallStickerTemplate',
        schemata="Stickers",
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
        schemata="Stickers",
        vocabulary="getStickerTemplates",
        default="Code_128_1x72mm.pt",
        widget=SelectionWidget(
            format='select',
            label=_("Large sticker"),
            description=_("Select which sticker should be used as the 'large' sticker by default")
        )
    ),
    PrefixesField(
        'Prefixes',
        schemata="ID Server",
        default=[{'portal_type': 'ARImport', 'prefix': 'AI', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'AnalysisRequest', 'prefix': 'client', 'padding': '0', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'Client', 'prefix': 'client', 'padding': '0', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'Batch', 'prefix': 'batch', 'padding': '0', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'DuplicateAnalysis', 'prefix': 'DA', 'padding': '0', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'Invoice', 'prefix': 'I', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'ReferenceAnalysis', 'prefix': 'RA', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'ReferenceSample', 'prefix': 'RS', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'SupplyOrder', 'prefix': 'O', 'padding': '3', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'Worksheet', 'prefix': 'WS', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 {'portal_type': 'Pricelist', 'prefix': 'PL', 'padding': '4', 'separator': '-', 'sequence_start': '0'},
                 ],
        # fixedSize=8,
        widget=RecordsWidget(
            label=_("Prefixes"),
            description=_(
                "Define the prefixes for the unique sequential IDs the system issues for "
                "objects. In the 'Padding' field, indicate with how many leading zeros the "
                "numbers must be padded. E.g. a prefix of WS for worksheets with padding of "
                "4, will see them numbered from WS-0001 to WS-9999. Sequence Start "
                "indicates the number from which the next ID should start. This is "
                "set only if it is greater than existing id numbers. Note that the "
                "gap created by jumping IDs cannot be refilled. NB: Note that samples "
                "and analysis requests are prefixed with sample type abbreviations and are "
                "not configured in this table - their padding can be set in the specified "
                "fields below"),
            allowDelete=False,
        )
    ),
    BooleanField(
        'YearInPrefix',
        schemata="ID Server",
        default=False,
        widget=BooleanWidget(
            label=_("Include year in ID prefix"),
            description=_("Adds a two-digit year after the ID prefix")
        ),
    ),
    IntegerField(
        'SampleIDPadding',
        schemata="ID Server",
        required=1,
        default=4,
        widget=IntegerWidget(
            label=_("Sample ID Padding"),
            description=_("The length of the zero-padding for Sample IDs"),
        )
    ),
    IntegerField(
        'SampleIDSequenceStart',
        schemata="ID Server",
        required=1,
        default=0,
        widget=IntegerWidget(
            label=_("Sample ID Sequence Start"),
            description=_(
                "The number from which the next id should start. This "
                "is set only if it is greater than existing id numbers. "
                "Note that the resultant gap between IDs cannot be filled."),
        )
    ),
    IntegerField(
        'ARIDPadding',
        schemata="ID Server",
        required=1,
        default=2,
        widget=IntegerWidget(
            label=_("AR ID Padding"),
            description=_("The length of the zero-padding for the AR number in AR IDs"),
        )
    ),
    BooleanField(
        'ExternalIDServer',
        schemata="ID Server",
        default=False,
        widget=BooleanWidget(
            label=_("Use external ID server"),
            description=_(
                "Check this if you want to use a separate ID server. "
                "Prefixes are configurable separately in each Bika site")
        ),
    ),
    StringField(
        'IDServerURL',
        schemata="ID Server",
        widget=StringWidget(
            label=_("ID Server URL"),
            description=_("The full URL: http://URL/path:port")
        ),
    ),
    RecordsField(
        'RejectionReasons',
        schemata="Analyses",
        widget=RejectionSetupWidget(
            label=_("Enable the rejection workflow"),
            description=_("Select this to activate the rejection workflow "
                          "for Samples and Analysis Requests. A 'Reject' "
                          "option will be displayed in the actions menu for "
                          "these objects.")
        ),
    ),
    BooleanField(
        'NotifyOnRejection',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Email notification on rejection"),
            description=_("Select this to activate automatic notifications "
                          "via email to the Client when a Sample or Analysis "
                          "Request is rejected.")
        ),
    ),
    BooleanField(
        'AllowDepartmentFiltering',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Enable filtering by department"),
            description=_("When enabled, only those items belonging to the "
                          "same department as the logged user will be "
                          "displayed. Since a user can belong to more than "
                          "one department, a department filtering portlet "
                          "will be displayed too. By default, disabled.")
        )
    ),
    BooleanField(
        'DisplayAdvancedFilterBarForAnalysisRequests',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_(
                "Display an advanced filter bar in Analysis Requests lists"),
            description=_(
                "If enabled, the Analysis Requests Lists will"
                " display an additional filter bar which allows the user "
                "to filter the listed items by some several criteria."
                "Warning: This may affect the listing performance."),
        ),
    ),
    BooleanField(
        'DisplayAdvancedFilterBarForSamples',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Display an advanced filter bar in Samples lists"),
            description=_(
                "If enabled, the Samples Lists will"
                " display an additional filter bar which allows the user "
                "to filter the listed items by some several criteria."
                "Warning: This may affect the listing performance."),
        ),
    ),
    BooleanField(
        'DisplayAdvancedFilterBarForAnalyses',
        schemata="Analyses",
        default=False,
        widget=BooleanWidget(
            label=_("Display an advanced filter bar in Analyses lists"),
            description=_(
                "If enabled, the Analyses Lists will"
                " display an additional filter bar which allows the user "
                "to filter the listed items by some several criteria."
                "Warning: This may affect the listing performance."),
        ),
    ),
    IntegerField(
        'DefaultNumberOfARsToAdd',
        schemata="Analyses",
        required=0,
        default=4,
        widget=IntegerWidget(
            label=_("Default count of AR to add."),
            description=_("Default value of the 'AR count' when users click 'ADD' button to create new Analysis Requests"),
        )
    ),

    RecordsField(
        'DateFormats',
        schemata="default",
        required=0,
        subfields=('Type', 'Format'),
        default=[{'Type': 'date_format_long', 'Format': '%Y-%m-%d %H:%M'},
                 {'Type': 'date_format_short', 'Format': '%Y-%m-%d'},
                 {'Type': 'time_only', 'Format': '%H:%M'}],
        subfield_labels={'Type': _('Type'),
                         'Folder': _('String Format')},
        subfield_readonly={'Type': False,
                           'Format': False},
        widget=RecordsWidget(
            label=_("Date formats in String"),
            description=_("Define The String Formats of Date and Time values users prefer to use."),
            visible=True,
        ),
    ),
))

schema['title'].validators = ()
schema['title'].widget.visible = False
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class BikaSetup(folder.ATFolder):
    """
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
                     inactive_state='active')
        items = [(b.UID, b.Title) for b in brains]
        items.insert(0, ("", ""))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getPrefixFor(self, portal_type):
        """Return the prefix for a portal_type.
           If not found, simply uses the portal_type itself
        """
        prefix = [p for p in self.getPrefixes() if p['portal_type'] == portal_type]
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

    def _getNumberOfRequiredVerificationsVocabulary(self):
        """
        Returns a DisplayList with the available options for the
        multi-verification list: '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
            multi-verification list
        """
        items = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))

registerType(BikaSetup, PROJECTNAME)
