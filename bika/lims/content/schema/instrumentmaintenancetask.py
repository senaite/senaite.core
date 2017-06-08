# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, ComputedField, \
    DateTimeField, FixedPointField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    DecimalWidget, ReferenceWidget, StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Instrument = ReferenceField(
    'Instrument',
    storage=Storage(),
    allowed_types=('Instrument',),
    relationship='InstrumentMaintenanceTaskInstrument',
    widget=StringWidget(
        visible=False
    ),
)

InstrumentUID = ComputedField(
    'InstrumentUID',
    storage=Storage(),
    expression='context.getInstrument().UID() '
               'if context.getInstrument() else None',
    widget=ComputedWidget(
        visible=False
    ),
)

Type = StringField(
    'Type',
    storage=Storage(),
    vocabulary="getMaintenanceTypes",
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Maintenance type",
                "Type")
    ),
)

DownFrom = DateTimeField(
    'DownFrom',
    storage=Storage(),
    with_time=1,
    with_date=1,
    required=1,
    widget=DateTimeWidget(
        label=_("From"),
        description=_("Date from which the instrument is under maintenance"),
        show_hm=True
    ),
)

DownTo = DateTimeField(
    'DownTo',
    storage=Storage(),
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("To"),
        description=_("Date until the instrument will not be available"),
        show_hm=True
    ),
)

Maintainer = StringField(
    'Maintainer',
    storage=Storage(),
    widget=StringWidget(
        label=_("Maintainer"),
        description=_("The analyst or agent responsible of the maintenance")
    ),
)

Considerations = TextField(
    'Considerations',
    storage=Storage(),
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Considerations"),
        description=_("Remarks to take into account for maintenance process")
    ),
)

WorkPerformed = TextField(
    'WorkPerformed',
    storage=Storage(),
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Work Performed"),
        description=_(
            "Description of the actions made during the maintenance process")
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Remarks")
    ),
)

Cost = FixedPointField(
    'Cost',
    storage=Storage(),
    default='0.00',
    widget=DecimalWidget(
        label=_("Price")
    ),
)

Closed = BooleanField(
    'Closed',
    storage=Storage(),
    default='0',
    widget=BooleanWidget(
        label=_("Closed"),
        description=_("Set the maintenance task as closed.")
    ),
)

schema = BikaSchema.copy() + Schema((
    Instrument,
    InstrumentUID,
    Type,
    DownFrom,
    DownTo,
    Maintainer,
    Considerations,
    WorkPerformed,
    Remarks,
    Cost,
    Closed
))

IdField = schema['id']
schema['description'].required = False
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

# Title is not needed to be unique
schema['title'].validators = ()
schema['title']._validationLayer()
