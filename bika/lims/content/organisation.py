from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordWidget
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from plone.app.folder.folder import ATFolder
from bika.lims.browser.fields import AddressField
from bika.lims import bikaMessageFactory as _

schema = BikaFolderSchema.copy() + BikaSchema.copy() + ManagedSchema((
    StringField('Name',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator',),
    ),
    StringField('TaxNumber',
        widget = StringWidget(
            label = _("VAT number"),
        ),
    ),
    StringField('Phone',
        widget = StringWidget(
            label = _("Phone"),
        ),
    ),
    StringField('Fax',
            widget = StringWidget(
            label = _("Fax"),
        ),
    ),
    StringField('EmailAddress',
        schemata = 'Address',
        widget = StringWidget(
            label = _("Email address"),
        ),
        validators = ('isEmail',)
    ),
    AddressField('PhysicalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Physical address"),
        ),
    ),
    AddressField('PostalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Postal address"),
        ),
    ),
    AddressField('BillingAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Billing address"),
        ),
    ),
    StringField('AccountType',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account type"),
        ),
    ),
    StringField('AccountName',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account name"),
        ),
    ),
    StringField('AccountNumber',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account number"),
        ),
    ),
    StringField('BankName',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Bank name"),
        ),
    ),
    StringField('BankBranch',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Bank branch"),
        ),
    ),
),
)

IdField = schema['id']
IdField.widget.visible = {'edit': 'visible', 'view': 'invisible'}
# Don't make title required - it will be computed from the Organisation's
# Name
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Organisation(ATFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(CMFCorePermissions.View, 'getSchema')
    def getSchema(self):
        return self.schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress', 'BillingAddress']

registerType(Organisation, PROJECTNAME)
