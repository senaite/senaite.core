from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from bika.lims.browser.widgets import RecordsWidget
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.config import I18N_DOMAIN, ATTACHMENT_OPTIONS, \
    ARIMPORT_OPTIONS, PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSetup
from bika.lims.utils import generateUniqueId
from plone.app.folder import folder
from zope.interface import implements
import sys
from bika.lims import bikaMessageFactory as _

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
        'subfield_readonly':{'portal_type': True,
                             'prefix': False,
                             'padding': False,
                            },
        })
    security = ClassSecurityInfo()

schema = BikaFolderSchema.copy() + Schema((
    IntegerField('PasswordLifetime',
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label = _("Password lifetime"),
            description = _("The number of days before a password expires. 0 disables password expiry"),
        )
    ),
    IntegerField('AutoLogOff',
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label = _("Automatic log-off"),
            description = _("The number of minutes before a user is automatically logged off. "
                            "0 disables automatic log-off"),
        )
    ),
    FixedPointField('MemberDiscount',
        default = '33.33',
        widget = DecimalWidget(
            label = _("Member discount %"),
            description = _("The discount percentage entered here, is applied to the prices for Clients "
                            "flagged as 'members', normally co-operative members or associates deserving "
                            "of this discount"),
        ),
    ),
    FixedPointField('VAT',
        default = '14.00',
        widget = DecimalWidget(
            label = _("VAT %"),
            description = _("Enter percentage value eg. 14.0. This percentage is applied system wide "
                            "but can be overwrittem on individual items"),
            ),
        ),
    ),
    IntegerField('MinimumResults',
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label = _("Minimum number of results for QC stats calculations"),
            description = _("Using to few data points does not make statistical sense. "
                            "Set an acceaptable minimum number of results before QC statistics "
                            "calculated an plotted"),
        )
    ),
    IntegerField('BatchEmail',
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label = _("Maximum columns per results email"),
            description = _("Set the maximum number of analysis requests per results email. "
                            "Too many columns per email are difficult to read for many clients "
                            "who prefer fewer results per email"),
        )
    ),
    IntegerField('BatchFax',
        required = 1,
        default = 4,
        widget = IntegerWidget(
            label = _("Maximum columns per results fax"),
            description = _("Too AR columns per fax will see the font size minimised and could "
                            "render faxes illegible. 4 ARs maximum per page is recommended"),
        )
    ),
    # XXX stringfield, chars to strip from cell number
    StringField('SMSGatewayAddress',
        required = 0,
        widget = StringWidget(
            label = _("SMS Gateway Email Address"),
            description = _("The email to SMS Gateway address. Either a complete email address, "
                             "or just the domain, e.g. '@2way.co.za', the contact's mobile phone "
                             "number will be prepended to"),
        ),
    ),
    ReferenceField('DryMatterService',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'SetupDryAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Dry matter analysis"),
            description = _("The analysis to be used for determining dry matter."),
        )
    ),
    ReferenceField('MoistureService',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'SetupMoistAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Moisture analysis"),
            description = _("The analysis to be used for determining moisture"),
        )
    ),
    LinesField('ARImportOption',
        vocabulary = ARIMPORT_OPTIONS,
        widget = MultiSelectionWidget(
            label = _("AR Import options"),
            description = _("'Classic' indicates importing Analysis Requests per Sample and "
                            "Analysis Services selection. With 'Profiles', Analysis Profile keywords "
                            "are used to select multiple Analysis Services together"),
        ),
    ),
    StringField('ARAttachmentOption',
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = _("AR Attachment option"),
            description = _("The default configuration for used system wide to indicate "
                            "whether file attachments are required, permitted or not "
                            "per Analysis Request"),
        ),
    ),
    StringField('AnalysisAttachmentOption',
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = _("Analysis Attachment option"),
            description = _("Same as the above, but sets the default on Anlaysis Services. "
                            "This setting can be set per individual Analysis on its "
                            "own configuration"),
        ),
    ),
    IntegerField('DefaultSampleLifetime',
        required = 1,
        default = 30,
        widget = IntegerWidget(
            label = _("Default sample retention period"),
            description = _("The number of days before a Sample expires and cannot be analysed "
                            "any more. This setting can be overwritten per individual Sample Type "
                            "in the Sample Types setup"),
        )
    ),
    PrefixesField('Prefixes',
         fixedSize=8,
         widget=RecordsWidget(
            label = _("Prefixes"),
            description = _("Define the prefixes for the unique sequential IDs the system issus "
                            "for objects such as Samples and Analysis Requests. In the 'Padding' "
                            "field, indicate with how many leading zeros the numbers must be padded. "
                            "E.g. a prefix of AR with padding of 4 for Analysis requests, will see "
                            "them numbered from AR0001 to AR9999"),
            allowDelete=False),
        )  
    ),
))
schema['title'].validators = ()
schema['title'].widget.visible = False
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class BikaSetup(folder.ATFolder):
    security = ClassSecurityInfo()
    schema = schema
    implements(IBikaSetup)

    # XXX: Temporary workaround to enable importing of exported bika
    # instance. If '__replaceable__' is not set we get BadRequest, The
    # id is invalid - it is already in use.
    __replaceable__ = 1

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

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

registerType(BikaSetup, PROJECTNAME)
