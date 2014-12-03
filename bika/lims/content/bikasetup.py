from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from bika.lims.browser.widgets import RecordsWidget
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.config import *
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSetup
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.fields import DurationField
from plone.app.folder import folder
from zope.interface import implements
import sys
from bika.lims.locales import COUNTRIES

class PrefixesField(RecordsField):
    """a list of prefixes per portal_type"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'prefixes',
        'subfields' : ('portal_type', 'prefix', 'padding'),
        'subfield_labels':{'portal_type': 'Portal type',
                           'prefix': 'Prefix',
                           'padding': 'Padding',
                           },
        'subfield_readonly':{'portal_type': False,
                             'prefix': False,
                             'padding': False,
                            },
        'subfield_sizes':{'portal_type':32,
                          'prefix': 12,
                          'padding':12},
    })
    security = ClassSecurityInfo()

LABEL_AUTO_OPTIONS = DisplayList((
    ('None', _('None')),
    ('register', _('Register')),
    ('receive', _('Receive')),
))

LABEL_AUTO_SIZES = DisplayList((
    ('small', _('Small')),
    ('normal', _('Normal')),
))

schema = BikaFolderSchema.copy() + Schema((
    IntegerField('PasswordLifetime',
        schemata = "Security",
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label=_("Password lifetime"),
            description=_("The number of days before a password expires. 0 disables password expiry"),
        )
    ),
    IntegerField('AutoLogOff',
        schemata = "Security",
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label=_("Automatic log-off"),
            description =_(
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
            description=_("If unticked, analysts will have access to all worksheets.")
        )
    ),
    BooleanField(
        'RestrictWorksheetManagement',
        schemata="Security",
        default=True,
        widget=BooleanWidget(
            label=_("Only lab managers can create and manage worksheets"),
            description=_("If unticked, analysts and lab clerks will "
                          "be able to manage Worksheets, too. If the "
                          "users have restricted access only to those "
                          "worksheets for which they are assigned, "
                          "this option will be ticked and readonly.")
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
    StringField('Currency',
        schemata = "Accounting",
        required = 1,
        vocabulary = CURRENCIES,
        default = 'ZAR',
        widget = SelectionWidget(
            label=_("Currency"),
            description=_("Select the currency the site will use to display prices."),
            format='select',
        )
    ),
    StringField('DefaultCountry',
        schemata = "Accounting",
        required = 1,
        vocabulary = 'getCountries',
        default = '',
        widget = SelectionWidget(
            label=_("Country"),
            description=_("Select the country the site will show by default"),
            format='select',
        )
    ),
    FixedPointField('MemberDiscount',
        schemata = "Accounting",
        default = '33.33',
        widget = DecimalWidget(
            label=_("Member discount %"),
            description =_(
                "The discount percentage entered here, is applied to the prices for clients "
                "flagged as 'members', normally co-operative members or associates deserving "
                "of this discount"),
        )
    ),
    FixedPointField('VAT',
        schemata = "Accounting",
        default = '14.00',
        widget = DecimalWidget(
            label=_("VAT %"),
            description=_(
                "Enter percentage value eg. 14.0. This percentage is applied system wide "
                "but can be overwrittem on individual items"),
        )
    ),
    StringField('DecimalMark',
        schemata = "Results Reports",
        vocabulary=DECIMAL_MARKS,
        default = ".",
        widget = SelectionWidget(
            label=_("Default decimal mark"),
            description=_("Preferred decimal mark for reports."),
            format = 'select',
        )
    ),
    StringField('ScientificNotationReport',
        schemata = "Results Reports",
        default = '1',
        vocabulary = SCINOTATION_OPTIONS,
        widget = SelectionWidget(
            label=_("Default scientific notation format for reports"),
            description =_("Preferred scientific notation format for reports"),
            format='select',
        )
    ),
    IntegerField('MinimumResults',
        schemata = "Results Reports",
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label=_("Minimum number of results for QC stats calculations"),
            description=_(
                "Using too few data points does not make statistical sense. "
                "Set an acceptable minimum number of results before QC statistics "
                "will be calculated and plotted"),
            )
    ),
    BooleanField('IncludePreviousFromBatch',
        schemata = "Results Reports",
        default = False,
        widget = BooleanWidget(
            label=_("Include Previous Results From Batch"),
            description=_(
                "If there are previous results for a service in the "
                "same batch of Analysis Requests, they will be displayed "
                "in the report.")
        )
    ),
    IntegerField('BatchEmail',
        schemata = "Results Reports",
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label=_("Maximum columns per results email"),
            description=_(
                "Set the maximum number of analysis requests per results email. "
                "Too many columns per email are difficult to read for some clients "
                "who prefer fewer results per email"),
        )
    ),
    TextField('ResultFooter',
        schemata = "Results Reports",
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        default="",
        widget = TextAreaWidget(
            label=_("Result Footer"),
            description=_("This text will be appended to results reports."),
            append_only = False,
        ),
    ),
##    IntegerField('BatchFax',
##        schemata = "Results Reports",
##        required = 1,
##        default = 4,
##        widget = IntegerWidget(
##            label=_("Maximum columns per results fax"),
##            description = "Too many AR columns per fax will see the font size minimised and could "
##                            "render faxes illegible. 4 ARs maximum per page is recommended",
##        )
##    ),
##    StringField('SMSGatewayAddress',
##        schemata = "Results Reports",
##        required = 0,
##        widget = StringWidget(
##            label=_("SMS Gateway Email Address"),
##            description = "The email to SMS gateway address. Either a complete email address, "
##                            "or just the domain, e.g. '@2way.co.za', the contact's mobile phone "
##                            "number will be prepended to",
##        )
##    ),
    BooleanField('SamplingWorkflowEnabled',
        schemata = "Analyses",
        default = False,
        widget = BooleanWidget(
            label=_("Enable the Sampling workflow"),
            description=_("Select this to activate the sample collection workflow steps.")
        ),
    ),
    BooleanField(
        'ShowPartitions',
        schemata = "Analyses",
        default = True,
        widget = BooleanWidget(
            label=_("Display individual sample partitions "),
            description=_("Turn this on if you want to work with sample partitions")
        ),
    ),
    BooleanField('CategoriseAnalysisServices',
        schemata = "Analyses",
        default = False,
        widget = BooleanWidget(
            label=_("Categorise analysis services"),
            description=_("Group analysis services by category in the LIMS tables, helpful when the list is long")
        ),
    ),
    BooleanField('EnableARSpecs',
        schemata = "Analyses",
        default = True,
        widget = BooleanWidget(
            label=_("Enable AR Specifications"),
            description=_(
                "Analysis specifications which are edited directly on the "
                "Analysis Request."),
        ),
    ),
    StringField('DefaultARSpecs',
        schemata = "Analyses",
        default = 'ar_specs',
        vocabulary = DEFAULT_AR_SPECS,
        widget = SelectionWidget(
            label=_("Default AR Specifications"),
            description = _(
                "Choose the default specifications used for all AR views "
                "to display alerts and notifications.  These will also be "
                "applied when an AR is published in permanent media, "
                "e.g. PDF."),
            format='select',
        )
    ),
    IntegerField('ExponentialFormatThreshold',
        schemata = "Analyses",
        required = 1,
        default = 7,
        widget = IntegerWidget(
        label=_("Exponential format threshold"),
        description=_(
            "Result values with at least this number of significant "
            "digits are displayed in scientific notation using the "
            "letter 'e' to indicate the exponent.  The precision can be "
            "configured in individual Analysis Services."),
        )
    ),
    BooleanField('EnableAnalysisRemarks',
        schemata = "Analyses",
        default = False,
        widget = BooleanWidget(
            label=_("Add a remarks field to all analyses"),
        ),
    ),
    ReferenceField('DryMatterService',
        schemata = "Analyses",
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'SetupDryAnalysisService',
        vocabulary = 'getAnalysisServices',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label=_("Dry matter analysis"),
            description=_("The analysis to be used for determining dry matter."),
        )
    ),
    LinesField('ARImportOption',
        schemata = "Analyses",
        vocabulary = ARIMPORT_OPTIONS,
        widget = MultiSelectionWidget(
            visible = False,
            label=_("AR Import options"),
            description = _(
                "'Classic' indicates importing analysis requests per sample and "
                "analysis service selection. With 'Profiles', analysis profile keywords "
                "are used to select multiple analysis services together"),
        )
    ),
    StringField('ARAttachmentOption',
        schemata = "Analyses",
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label=_("AR Attachment Option"),
            description =_(
                "The system wide default configuration to indicate "
                "whether file attachments are required, permitted or not "
                "per analysis request"),
            format='select',
        )
    ),
    StringField('AnalysisAttachmentOption',
        schemata = "Analyses",
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label=_("Analysis Attachment Option"),
            description =_(
                "Same as the above, but sets the default on analysis services. "
                "This setting can be set per individual analysis on its "
                "own configuration"),
            format='select',
        )
    ),
    DurationField('DefaultSampleLifetime',
        schemata = "Analyses",
        required = 1,
        default = {"days":30, "hours":0, "minutes":0},
        widget = DurationWidget(
            label=_("Default sample retention period"),
            description =_(
                "The number of days before a sample expires and cannot be analysed "
                "any more. This setting can be overwritten per individual sample type "
                "in the sample types setup"),
        )
    ),
    StringField('ResultsDecimalMark',
        schemata = "Analyses",
        vocabulary=DECIMAL_MARKS,
        default = ".",
        widget = SelectionWidget(
            label=_("Default decimal mark"),
            description=_("Preferred decimal mark for results"),
            format = 'select',
        )
    ),
    StringField('ScientificNotationResults',
        schemata = "Analyses",
        default = '1',
        vocabulary = SCINOTATION_OPTIONS,
        widget = SelectionWidget(
            label=_("Default scientific notation format for results"),
            description =_("Preferred scientific notation format for results"),
            format='select',
        )
    ),
    StringField('AutoPrintLabels',
        schemata = "Labels",
        vocabulary = LABEL_AUTO_OPTIONS,
        widget = SelectionWidget(
            format = 'select',
            label=_("Automatic label printing"),
            description=_(
                "Select 'Register' if you want labels to be automatically printed when "
                "new ARs or sample records are created. Select 'Receive' to print labels "
                "when ARs or Samples are received. Select 'None' to disable automatic printing"),
        )
    ),
    StringField('AutoLabelSize',
        schemata = "Labels",
        vocabulary = LABEL_AUTO_SIZES,
        widget = SelectionWidget(
            format = 'select',
            label=_("Label sizes"),
            description=_("Select the which label to print when automatic label printing is enabled"),
        )
    ),
    PrefixesField('Prefixes',
        schemata = "ID Server",
        default = [{'portal_type': 'ARImport', 'prefix': 'AI', 'padding': '4'},
                   {'portal_type': 'AnalysisRequest', 'prefix': 'client', 'padding': '0'},
                   {'portal_type': 'Client', 'prefix': 'client', 'padding': '0'},
                   {'portal_type': 'Batch', 'prefix': 'batch', 'padding': '0'},
                   {'portal_type': 'DuplicateAnalysis', 'prefix': 'DA', 'padding': '0'},
                   {'portal_type': 'Invoice', 'prefix': 'I', 'padding': '4'},
                   {'portal_type': 'ReferenceAnalysis', 'prefix': 'RA', 'padding': '4'},
                   {'portal_type': 'ReferenceSample', 'prefix': 'RS', 'padding': '4'},
                   {'portal_type': 'SupplyOrder', 'prefix': 'O', 'padding': '3'},
                   {'portal_type': 'Worksheet', 'prefix': 'WS', 'padding': '4'},
                   {'portal_type': 'Pricelist', 'prefix': 'PL', 'padding': '4'},
                   ],
#        fixedSize=8,
        widget=RecordsWidget(
            label=_("Prefixes"),
            description=_(
                "Define the prefixes for the unique sequential IDs the system issues for "
                "objects. In the 'Padding' field, indicate with how many leading zeros the "
                "numbers must be padded. E.g. a prefix of WS for worksheets with padding of "
                "4, will see them numbered from WS-0001 to WS-9999. NB: Note that samples "
                "and analysis requests are prefixed with sample type abbreviations and are "
                "not configured in this table - their padding can be set in the specified "
                "fields below"),
            allowDelete=False,
        )
    ),
    BooleanField('YearInPrefix',
        schemata = "ID Server",
        default = False,
        widget = BooleanWidget(
            label=_("Include year in ID prefix"),
            description=_("Adds a two-digit year after the ID prefix")
        ),
    ),
    IntegerField('SampleIDPadding',
        schemata = "ID Server",
        required = 1,
        default = 4,
        widget = IntegerWidget(
            label=_("Sample ID Padding"),
            description=_("The length of the zero-padding for Sample IDs"),
        )
    ),
    IntegerField('ARIDPadding',
        schemata = "ID Server",
        required = 1,
        default = 2,
        widget = IntegerWidget(
            label=_("AR ID Padding"),
            description=_("The length of the zero-padding for the AR number in AR IDs"),
        )
    ),
    BooleanField('ExternalIDServer',
        schemata = "ID Server",
        default = False,
        widget = BooleanWidget(
            label=_("Use external ID server"),
            description = _(
                "Check this if you want to use a separate ID server. "
                "Prefixes are configurable separately in each Bika site")
        ),
    ),
    StringField('IDServerURL',
        schemata = "ID Server",
        widget = StringWidget(
            label=_("ID Server URL"),
            description=_("The full URL: http://URL/path:port")

        ),
    ),
))

schema['title'].validators = ()
schema['title'].widget.visible = False
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()

class BikaSetup(folder.ATFolder):
    security = ClassSecurityInfo()
    schema = schema
    implements(IBikaSetup, IHaveNoBreadCrumbs)

    def getAttachmentsPermitted(self):
        """ are any attachments permitted """
        if self.getARAttachmentOption() in ['r', 'p'] \
        or self.getAnalysisAttachmentOption() in ['r', 'p']:
            return True
        else:
            return False

    def getARAttachmentsPermitted(self):
        """ are AR attachments permitted """
        if self.getARAttachmentOption() == 'n':
            return False
        else:
            return True

    def getAnalysisAttachmentsPermitted(self):
        """ are analysis attachments permitted """
        if self.getAnalysisAttachmentOption() == 'n':
            return False
        else:
            return True

    def getAnalysisServices(self):
        """
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in
                               bsc(portal_type='AnalysisService',
                                   inactive_state = 'active')]
        items.sort(lambda x,y: cmp(x[1], y[1]))
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
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return items


registerType(BikaSetup, PROJECTNAME)
