# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManageSuppliers
from bika.lims.content.organisation import Organisation
from bika.lims.content.schema import Storage

Remarks = TextField(
    'Remarks',
    storage=Storage,
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/html",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    )
)

Website = StringField(
    'Website',
    storage=Storage,
    searchable=1,
    required=0,
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('Website.')
    )
)

NIB = StringField(
    'NIB',
    storage=Storage,
    searchable=1,
    schemata='Bank details',
    required=0,
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('NIB')
    ),
    validators=('NIBvalidator',)
)

IBN = StringField(
    'IBN',
    storage=Storage,
    searchable=1,
    schemata='Bank details',
    required=0,
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('IBN')
    ),
    validators=('IBANvalidator',)
)

SWIFTcode = StringField(
    'SWIFTcode',
    storage=Storage,
    searchable=1,
    required=0,
    schemata='Bank details',
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('SWIFT code.')
    )
)

schema = Organisation.schema.copy() + Schema(())
schema['AccountNumber'].write_permission = ManageSuppliers
