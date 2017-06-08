# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime import DateTime
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import CalendarWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

BatchStartDate = DateTimeField(
    'BatchStartDate',
    storage=Storage(),
    required=1,
    default_method='current_date',
    widget=CalendarWidget(
        label=_("Start Date")
    ),
)

BatchEndDate = DateTimeField(
    'BatchEndDate',
    storage=Storage(),
    required=1,
    default_method='current_date',
    validators=('invoicebatch_EndDate_validator',),
    widget=CalendarWidget(
        label=_("End Date")
    ),
)

schema = BikaSchema.copy() + Schema((
    BatchStartDate,
    BatchEndDate
))

# noinspection PyCallingNonCallable
schema['title'].default = DateTime().strftime('%b %Y')
