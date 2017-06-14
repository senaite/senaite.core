# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Field import ComputedField, ReferenceField, \
    StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, ReferenceWidget, \
    StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ScheduleInputWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Instrument = ReferenceField(
    'Instrument',
    storage=Storage(),
    allowed_types=('Instrument',),
    relationship='InstrumentScheduledTaskInstrument',
    widget=StringWidget(
        visible=False
    ),
)

InstrumentUID = ComputedField(
    'InstrumentUID',
    expression='context.getInstrument().UID() '
               'if context.getInstrument() else None',
    widget=ComputedWidget(
        visible=False
    ),
)

Type = StringField(
    'Type',
    storage=Storage(),
    vocabulary="getTaskTypes",
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Task type", "Type")
    ),
)

ScheduleCriteria = RecordsField(
    'ScheduleCriteria',
    storage=Storage(),
    required=1,
    type='schedulecriteria',
    widget=ScheduleInputWidget(
        label=_("Criteria")
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
        description=_("Remarks to take into account before performing the task")
    ),
)

schema = BikaSchema.copy() + Schema((
    Instrument,
    InstrumentUID,
    Type,
    ScheduleCriteria,
    Considerations
))

IdField = schema['id']
schema['description'].required = False
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
schema.moveField('description', before='Considerations')

# Title is not needed to be unique
schema['title'].validators = ()
schema['title']._validationLayer()
