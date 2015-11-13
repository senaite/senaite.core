from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import ManageInvoices, ManageBika, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInvoice
from DateTime import DateTime
from decimal import Decimal
from persistent.mapping import PersistentMapping
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.CMFCore.permissions import View
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('Client',
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Client',),
        relationship='ClientInvoice',
    ),
    ReferenceField('AnalysisRequest',
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('AnalysisRequest',),
        relationship='AnalysisRequestInvoice',
    ),
    ReferenceField('SupplyOrder',
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('SupplyOrder',),
        relationship='SupplyOrderInvoice',
    ),
    DateTimeField('InvoiceDate',
        required=1,
        default_method='current_date',
        widget=DateTimeWidget(
            label=_("Date"),
        ),
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
    ComputedField('Subtotal',
        expression='context.getSubtotal()',
        widget=ComputedWidget(
            label=_("Subtotal"),
            visible=False,
        ),
    ),
    ComputedField('VATAmount',
        expression='context.getVATAmount()',
        widget=ComputedWidget(
            label=_("VAT Total"),
            visible=False,
        ),
    ),
    ComputedField('Total',
        expression='context.getTotal()',
        widget=ComputedWidget(
            label=_("Total"),
            visible=False,
        ),
    ),
    ComputedField('ClientUID',
        expression='here.getClient() and here.getClient().UID()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField('InvoiceSearchableText',
        expression='here.getInvoiceSearchableText()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
),
)

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False


class InvoiceLineItem(PersistentMapping):
    pass


class Invoice(BaseFolder):
    implements(IInvoice)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Invoice Id as title """
        return safe_unicode(self.getId()).encode('utf-8')

    security.declareProtected(View, 'getSubtotal')

    def getSubtotal(self):
        """ Compute Subtotal """
        return sum([float(obj['Subtotal']) for obj in self.invoice_lineitems])

    security.declareProtected(View, 'getVATAmount')

    def getVATAmount(self):
        """ Compute VAT """
        return Decimal(self.getTotal()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotal')

    def getTotal(self):
        """ Compute Total """
        return sum([float(obj['Total']) for obj in self.invoice_lineitems])

    security.declareProtected(View, 'getInvoiceSearchableText')

    def getInvoiceSearchableText(self):
        """ Aggregate text of all line items for querying """
        s = ''
        for item in self.invoice_lineitems:
            s = s + item['ItemDescription']
        return s

    # XXX workflow script
    def workflow_script_dispatch(self):
        """ dispatch order """
        self.setDateDispatched(DateTime())

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

registerType(Invoice, PROJECTNAME)
