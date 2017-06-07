# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Field import BooleanField, ComputedField, \
    DateTimeField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    FileWidget, StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField
from bika.lims.content.schema import Storage

TaskID = StringField(
    'TaskID',
    storage=Storage,
    widget=StringWidget(
        label=_('Task ID'),
        description=_("The instrument's ID in the lab's asset register")
    ),
)

Instrument = ReferenceField(
    'Instrument',
    storage=Storage,
    allowed_types=('Instrument',),
    relationship='InstrumentCertificationInstrument',
    widget=StringWidget(
        visible=False
    ),
)

InstrumentUID = ComputedField(
    'InstrumentUID',
    storage=Storage,
    expression='context.getInstrument().UID() '
               'if context.getInstrument() else None',
    widget=ComputedWidget(
        visible=False
    ),
)

# Set the Certificate as Internal
# When selected, the 'Agency' field is hidden
Internal = BooleanField(
    'Internal',
    storage=Storage,
    default=False,
    widget=BooleanWidget(
        label=_('Internal Certificate'),
        description=_('Select if is an in-house calibration certificate')
    ),
)

Agency = StringField(
    'Agency',
    storage=Storage,
    widget=StringWidget(
        label=_('Agency'),
        description=_(
            'Organization responsible of granting the calibration certificate')
    ),
)

Date = DateTimeField(
    'Date',
    storage=Storage,
    widget=DateTimeWidget(
        label=_('Date'),
        description=_('Date when the calibration certificate was granted')
    ),
)

ValidFrom = DateTimeField(
    'ValidFrom',
    storage=Storage,
    with_time=1,
    with_date=1,
    required=1,
    widget=DateTimeWidget(
        label=_('From'),
        description=_('Date from which the calibration certificate is valid')
    ),
)

ValidTo = DateTimeField(
    'ValidTo',
    storage=Storage,
    with_time=1,
    with_date=1,
    required=1,
    widget=DateTimeWidget(
        label=_('To'),
        description=_('Date until the certificate is valid')
    ),
)

Preparator = ReferenceField(
    'Preparator',
    storage=Storage,
    vocabulary='getLabContacts',
    allowed_types=('LabContact',),
    relationship='LabContactInstrumentCertificatePreparator',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_('Prepared by'),
        description=_(
            'The person at the supplier who prepared the certificate'),
        size=30,
        base_query={'inactive_state': 'active'},
        showOn=True,
        colModel=[{'columnName': 'UID',
                   'hidden': True},
                  {'columnName': 'JobTitle',
                   'width': '20',
                   'label': _('Job Title')},
                  {'columnName': 'Title',
                   'width': '80',
                   'label': _('Name')}
                  ]
    ),
)

Validator = ReferenceField(
    'Validator',
    storage=Storage,
    vocabulary='getLabContacts',
    allowed_types=('LabContact',),
    relationship='LabContactInstrumentCertificateValidator',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_('Approved by'),
        description=_(
            'The person at the supplier who approved the certificate'),
        size=30,
        base_query={'inactive_state': 'active'},
        showOn=True,
        colModel=[{'columnName': 'UID',
                   'hidden': True},
                  {'columnName': 'JobTitle',
                   'width': '20',
                   'label': _('Job Title')},
                  {'columnName': 'Title',
                   'width': '80',
                   'label': _('Name')}
                  ]
    ),
)

Document = BlobFileField(
    'Document',
    storage=Storage,
    widget=FileWidget(
        label=_('Report upload'),
        description=_('Load the certificate document here')
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage,
    searchable=True,
    default_content_type='text/x-web-intelligent',
    allowable_content_types=('text/plain',),
    default_output_type='text/plain',
    mode='rw',
    widget=TextAreaWidget(
        macro='bika_widgets/remarks',
        label=_('Remarks'),
        append_only=True
    ),
)

schema = BikaSchema.copy() + Schema((
    TaskID,
    Instrument,
    InstrumentUID,
    Internal,
    Agency,
    Date,
    ValidFrom,
    ValidTo,
    Preparator,
    Validator,
    Document,
    Remarks
))

schema['title'].widget.label = _("Certificate Code")
