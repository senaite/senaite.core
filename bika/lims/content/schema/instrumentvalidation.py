# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

DateIssued = DateTimeField(
    'DateIssued',
    storage=Storage(),
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("Report Date"),
        description=_("Validation report date")
    ),
)

DownFrom = DateTimeField(
    'DownFrom',
    storage=Storage(),
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("From"),
        description=_("Date from which the instrument is under validation")
    ),
)

DownTo = DateTimeField(
    'DownTo',
    storage=Storage(),
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("To"),
        description=_("Date until the instrument will not be available")
    ),
)

Validator = StringField(
    'Validator',
    storage=Storage(),
    widget=StringWidget(
        label=_("Validator"),
        description=_("The analyst responsible of the validation"),
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
        description=_("Remarks to take into account before validation")
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
        description=_("Description of the actions made during the validation")
    ),
)

Worker = ReferenceField(
    'Worker',
    storage=Storage(),
    vocabulary='getLabContacts',
    allowed_types=('LabContact',),
    relationship='LabContactInstrumentValidation',
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
    storage=Storage(),
    widget=StringWidget(
        label=_("Report ID"),
        description=_("Report identification number"),
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

schema = BikaSchema.copy() + Schema((
    DateIssued,
    DownFrom,
    DownTo,
    Validator,
    Considerations,
    WorkPerformed,
    Worker,
    ReportID,
    Remarks
))

schema['title'].widget.label = 'Task ID'
