# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from sys import maxint

from Products.Archetypes.Field import ComputedField, ReferenceField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Client = ReferenceField(
    'Client',
    storage=Storage,
    required=1,
    vocabulary_display_path_bound=maxint,
    allowed_types=('Client',),
    relationship='ClientInvoice',
)

AnalysisRequest = ReferenceField(
    'AnalysisRequest',
    storage=Storage,
    required=1,
    vocabulary_display_path_bound=maxint,
    allowed_types=('AnalysisRequest',),
    relationship='AnalysisRequestInvoice',
)

SupplyOrder = ReferenceField(
    'SupplyOrder',
    storage=Storage,
    required=1,
    vocabulary_display_path_bound=maxint,
    allowed_types=('SupplyOrder',),
    relationship='SupplyOrderInvoice',
)

InvoiceDate = DateTimeField(
    'InvoiceDate',
    storage=Storage,
    required=1,
    default_method='current_date',
    widget=DateTimeWidget(
        label=_("Date")
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage,
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    ),
)

Subtotal = ComputedField(
    'Subtotal',
    storage=Storage,
    expression='context.getSubtotal()',
    widget=ComputedWidget(
        label=_("Subtotal"),
        visible=False
    ),
)

VATAmount = ComputedField(
    'VATAmount',
    storage=Storage,
    expression='context.getVATAmount()',
    widget=ComputedWidget(
        label=_("VAT Total"),
        visible=False
    ),
)

Total = ComputedField(
    'Total',
    storage=Storage,
    expression='context.getTotal()',
    widget=ComputedWidget(
        label=_("Total"),
        visible=False
    ),
)

ClientUID = ComputedField(
    'ClientUID',
    storage=Storage,
    expression="context.getClient().UID() if context.getClient() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

InvoiceSearchableText = ComputedField(
    'InvoiceSearchableText',
    storage=Storage,
    expression='context.getInvoiceSearchableText()',
    widget=ComputedWidget(
        visible=False
    ),
)

schema = BikaSchema.copy() + Schema((
    Client,
    AnalysisRequest,
    SupplyOrder,
    InvoiceDate,
    Remarks,
    Subtotal,
    VATAmount,
    Total,
    ClientUID,
    InvoiceSearchableText
))

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False
