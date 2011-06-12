import sys
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, ManageInvoices, ManageBika, PROJECTNAME

schema = BikaSchema.copy() + Schema((
    StringField('InvoiceNumber',
        required = 1,
        default_method = 'getId',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Invoice number',
            label_msgid = 'label_invoicenumber',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Client',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Client',),
        relationship = 'ClientInvoice',
    ),
    DateTimeField('InvoiceDate',
        required = 1,
        default_method = 'current_date',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date',
            label_msgid = 'label_invoicedate',
        ),
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes'
        )
    ),
    ComputedField('Subtotal',
        expression = 'context.getSubtotal()',
        widget = ComputedWidget(
            label = 'Subtotal',
            label_msgid = 'label_subtotal',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ComputedField('VAT',
        expression = 'context.getVAT()',
        widget = ComputedWidget(
            label = 'VAT',
            label_msgid = 'label_vat',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ComputedField('Total',
        expression = 'context.getTotal()',
        widget = ComputedWidget(
            label = 'Total',
            label_msgid = 'label_total',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.getClient() and here.getClient().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('InvoiceSearchableText',
        index = 'TextIndex',
        expression = 'here.getInvoiceSearchableText()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False

class Invoice(BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'Invoice'
    schema = schema
    content_icon = 'invoice.png'
    allowed_content_types = ('InvoiceLineItem',)
    immediate_view = 'base_view'
    use_folder_tabs = 0
    global_allow = 0

    actions = (
        {'id': 'printinvoice',
         'name': 'Print invoice',
         'action': 'string:${object_url}/invoice_print',
         'permissions': (View,),
        },
    )

    def Title(self):
        """ Return the InvoiceNumber as title """
        return self.getInvoiceNumber()

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal """
        return sum(
            [obj.getSubtotal() \
             for obj in self.objectValues('InvoiceLineItem')])

    security.declareProtected(View, 'getVAT')
    def getVAT(self):
        """ Compute VAT """
        return self.getTotal() - self.getSubtotal()

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """ Compute Total """
        return sum(
            [obj.getTotal() \
             for obj in self.objectValues('InvoiceLineItem')])

    security.declareProtected(View, 'getInvoiceSearchableText')
    def getInvoiceSearchableText(self):
        """ Aggregate text of all line items for querying """
        s = ''
        for item in self.objectValues('InvoiceLineItem'):
            s = s + item.getItemDescription()
        return s

    def workflow_script_dispatch(self, state_info):
        """ dispatch order """
        self.setDateDispatched(DateTime())

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(Invoice, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'syndication', 'references',
                       'metadata', 'localroles'):
            a['visible'] = 0
    return fti
