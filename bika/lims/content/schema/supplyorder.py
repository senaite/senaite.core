# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

from Products.Archetypes.Field import ComputedField, DateTimeField, \
    ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, StringWidget, \
    TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as BikaReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Contact = ReferenceField(
    'Contact',
    storage=Storage(),
    required=1,
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Contact',),
    referenceClass=HoldingReference,
    relationship='SupplyOrderContact',
    widget=BikaReferenceWidget(
        render_own_label=True,
        showOn=True,
        colModel=[
            {'columnName': 'UID', 'hidden': True},
            {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
            {'columnName': 'EmailAddress', 'width': '50',
             'label': _('Email Address')},
        ]
    )
)
OrderNumber = StringField(
    'OrderNumber',
    storage=Storage(),
    required=1,
    searchable=True,
    widget=StringWidget(
        label=_("Order Number")
    )
)
Invoice = ReferenceField(
    'Invoice',
    storage=Storage(),
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Invoice',),
    referenceClass=HoldingReference,
    relationship='OrderInvoice'
)
OrderDate = DateTimeField(
    'OrderDate',
    storage=Storage(),
    required=1,
    default_method='current_date',
    widget=DateTimeWidget(
        label=_("Order Date"),
        size=12,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'visible',
            'secondary': 'invisible'
        }
    )
)
DateDispatched = DateTimeField(
    'DateDispatched',
    storage=Storage(),
    widget=DateTimeWidget(
        label=_("Date Dispatched")
    )
)
Remarks = TextField(
    'Remarks',
    storage=Storage(),
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    )
)
ClientUID = ComputedField(
    'ClientUID',
    expression='here.aq_parent.UID()',
    widget=ComputedWidget(
        visible=False
    )
)
ProductUID = ComputedField(
    'ProductUID',
    expression='context.getProductUIDs()',
    widget=ComputedWidget(
        visible=False
    )
)

schema = BikaSchema.copy() + Schema((
    Contact,
    OrderNumber,
    Invoice,
    OrderDate,
    DateDispatched,
    Remarks,
    ClientUID,
    ProductUID
))

schema['title'].required = False
