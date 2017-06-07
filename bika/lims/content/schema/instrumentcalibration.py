# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Field import ComputedField, DateTimeField, \
    ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, StringWidget, \
    TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

Instrument = ReferenceField(
    'Instrument',
    storage=Storage,
    allowed_types=('Instrument',),
    relationship='InstrumentCalibrationInstrument',
    widget=StringWidget(
        visible=False
    ),
)

InstrumentUID = ComputedField(
    'InstrumentUID',
    storage=Storage,
    expression='context.getInstrument() and context.getInstrument().UID() or '
               'None',
    widget=ComputedWidget(
        visible=False
    ),
)

DateIssued = DateTimeField(
    'DateIssued',
    storage=Storage,
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("Report Date"),
        description=_("Calibration report date")
    ),
)

DownFrom = DateTimeField(
    'DownFrom',
    storage=Storage,
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("From"),
        description=_("Date from which the instrument is under calibration")
    ),
)

DownTo = DateTimeField(
    'DownTo',
    storage=Storage,
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("To"),
        description=_("Date until the instrument will not be available")
    ),
)

Calibrator = StringField(
    'Calibrator',
    storage=Storage,
    widget=StringWidget(
        label=_("Calibrator"),
        description=_("The analyst or agent responsible of the calibration")
    ),
)

Considerations = TextField(
    'Considerations',
    storage=Storage,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Considerations"),
        description=_("Remarks to take into account before calibration")
    ),
)

WorkPerformed = TextField(
    'WorkPerformed',
    storage=Storage,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Work Performed"),
        description=_("Description of the actions made during the calibration")
    ),
)

Worker = ReferenceField(
    'Worker',
    storage=Storage,
    vocabulary='getLabContacts',
    allowed_types=('LabContact',),
    relationship='LabContactInstrumentCalibration',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Performed by"),
        description=_("The person at the supplier who performed the task"),
        size=30,
        base_query={'inactive_state': 'active'},
        showOn=True,
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'JobTitle', 'width': '20',
                   'label': _('Job Title')},
                  {'columnName': 'Title', 'width': '80', 'label': _('Name')}
                  ]
    ),
)

ReportID = StringField(
    'ReportID',
    storage=Storage,
    widget=StringWidget(
        label=_("Report ID"),
        description=_("Report identification number")
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Remarks")
    ),
)

schema = BikaSchema.copy() + Schema((
    Instrument,
    InstrumentUID,
    DateIssued,
    DownFrom,
    DownTo,
    Calibrator,
    Considerations,
    WorkPerformed,
    Worker,
    ReportID,
    Remarks
))

schema['title'].widget.label = 'Task ID'
