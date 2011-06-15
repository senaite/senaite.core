from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bika.lims.config import I18N_DOMAIN, ATTACHMENT_OPTIONS, \
    ARIMPORT_OPTIONS, PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBikaSettings
from bika.lims.utils import generateUniqueId
from plone.app.folder import folder
from zope.interface import implements
import sys

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
        })
    security = ClassSecurityInfo()

schema = BikaFolderSchema.copy() + Schema((
    IntegerField('PasswordLifetime',
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label = 'Password lifetime',
            label_msgid = 'label_password_lifetime',
            description = 'The number of days before a password expires. 0 disables password expiry.',
            description_msgid = 'help_password_lifetime',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('AutoLogOff',
        required = 1,
        default = 0,
        widget = IntegerWidget(
            label = 'Automatic log-off',
            label_msgid = 'label_auto_logoff',
            description = 'The number of minutes before a user is automatically logged off. 0 disable automatic log-off.',
            description_msgid = 'help_auto_logoff',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FixedPointField('MemberDiscount',
        default = '33.33',
        widget = DecimalWidget(
            label = 'Member discount %',
            label_msgid = 'label_memberdiscount_percentage',
            description = 'Enter percentage value eg. 33.0',
            description_msgid = 'help_memberdiscount_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FixedPointField('VAT',
        default = '14.00',
        widget = DecimalWidget(
            label = 'VAT %',
            label_msgid = 'label_vat_percentage',
            description = 'Enter percentage value eg. 14.0',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    IntegerField('MinimumResults',
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label = 'Minimum number of results',
            label_msgid = 'label_minimum_results',
            description = 'The minimum number of results before ' \
                        'QC statistics are shown',
            description_msgid = 'help_minimum_results',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('BatchEmail',
        required = 1,
        default = 5,
        widget = IntegerWidget(
            label = 'Maximum requests per results email',
            label_msgid = 'label_max_email',
            description = 'The maximum number of analysis requests per ' \
                        'results email',
            description_msgid = 'help_max_email',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('BatchFax',
        required = 1,
        default = 4,
        widget = IntegerWidget(
            label = 'Maximum requests per results fax',
            label_msgid = 'label_max_fax',
            description = 'The maximum number of analysis requests per ' \
                        'results fax',
            description_msgid = 'help_max_fax',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    # XXX stringfield, chars to strip from cell number
    StringField('SMSGatewayAddress',
        required = 0,
        widget = StringWidget(
            label = 'SMS Gateway Email Address',
            label_msgid = 'label_email2smsserver',
            description = 'The email to SMS Gateway address.  Either a complete email address, or just the domain, like this: "@2way.co.za"; in the second case, the contact\'s Mobile Phone number will be prepended.',
            description_msgid = 'help_email2smsaddress',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('DryMatterService',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'SettingsDryAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Dry matter analysis',
            label_msgid = 'label_dry_matter_analysis',
            description = 'The analysis to be used for determining dry matter',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('MoistureService',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'SettingsMoistAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Moisture analysis',
            label_msgid = 'label_moisture_analysis',
            description = 'The analysis to be used for determining moisture',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    LinesField('ARImportOption',
        vocabulary = ARIMPORT_OPTIONS,
        widget = MultiSelectionWidget(
            label = 'AR Import options',
            label_msgid = 'label_arimport_option',
        ),
    ),
    StringField('ARAttachmentOption',
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = 'AR Attachment option',
            label_msgid = 'label_attachment_option',
        ),
    ),
    StringField('AnalysisAttachmentOption',
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = 'Analysis Attachment option',
            label_msgid = 'label_attachment_option',
        ),
    ),
    IntegerField('DefaultSampleLifetime',
        required = 1,
        default = 30,
        widget = IntegerWidget(
            label = 'Default sample retention period',
            label_msgid = 'label_def_sample_life',
            description = 'The number of days from creation of analysis request ' \
                        'to diposal of sample',
            description_msgid = 'help_def_sample_life',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    PrefixesField('Prefixes'),
))


class BikaSettings(BrowserDefaultMixin, folder.ATFolder):
    security = ClassSecurityInfo()
    schema = schema
    implements(IBikaSettings)

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

registerType(BikaSettings, PROJECTNAME)
