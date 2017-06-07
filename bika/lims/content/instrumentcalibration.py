# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

Instrument = ReferenceField(
    'Instrument',
    allowed_types=('Instrument',),
    relationship='InstrumentCalibrationInstrument',
    widget=StringWidget(
        visible=False
    )
)

InstrumentUID = ComputedField(
    'InstrumentUID',
    expression='context.getInstrument() and context.getInstrument().UID() or '
               'None',
    widget=ComputedWidget(
        visible=False
    )
)

DateIssued = DateTimeField(
    'DateIssued',
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("Report Date"),
        description=_("Calibration report date")
    )
)

DownFrom = DateTimeField(
    'DownFrom',
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("From"),
        description=_("Date from which the instrument is under calibration")
    )
)

DownTo = DateTimeField(
    'DownTo',
    with_time=1,
    with_date=1,
    widget=DateTimeWidget(
        label=_("To"),
        description=_("Date until the instrument will not be available")
    )
)

Calibrator = StringField(
    'Calibrator',
    widget=StringWidget(
        label=_("Calibrator"),
        description=_("The analyst or agent responsible of the calibration")
    )
)

Considerations = TextField(
    'Considerations',
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Considerations"),
        description=_("Remarks to take into account before calibration")
    )
)

WorkPerformed = TextField(
    'WorkPerformed',
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Work Performed"),
        description=_("Description of the actions made during the calibration")
    )
)

Worker = ReferenceField(
    'Worker',
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
    )
)

ReportID = StringField(
    'ReportID',
    widget=StringWidget(
        label=_("Report ID"),
        description=_("Report identification number")
    )
)

Remarks = TextField(
    'Remarks',
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Remarks")
    )
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


class InstrumentCalibration(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = False

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        contacts = bsc(portal_type='LabContact',
                       inactive_state='active',
                       sort_on='sortable_title')
        for contact in contacts:
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)


atapi.registerType(InstrumentCalibration, PROJECTNAME)
