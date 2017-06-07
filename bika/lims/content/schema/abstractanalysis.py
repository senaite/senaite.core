# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Field import BooleanField, DateTimeField, \
    FixedPointField, IntegerField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.content.schema import Storage

# A link directly to the AnalysisService object used to create the analysis
AnalysisService = UIDReferenceField(
    'AnalysisService',
    storage=Storage,
)

# Overrides the AbstractBaseAnalysis. Analyses have a versioned link to the
# calculation as it was when created.
Calculation = HistoryAwareReferenceField(
    'Calculation',
    storage=Storage,
    allowed_types=('Calculation',),
    relationship='AnalysisCalculation',
    referenceClass=HoldingReference,
)

# Attachments which are added manually in the UI, or automatically when
# results are imported from a file supplied by an instrument.
Attachment = UIDReferenceField(
    'Attachment',
    storage=Storage,
    multiValued=1,
    allowed_types=('Attachment',),
)

# The final result of the analysis is stored here.  The field contains a
# String value, but the result itself is required to be numeric.  If
# a non-numeric result is needed, ResultOptions can be used.
Result = StringField(
    'Result',
    storage=Storage,
)

# When the result is changed, this value is updated to the current time.
# Only the most recent result capture date is recorded here and used to
# populate catalog values, however the workflow review_history can be
# used to get all dates of result capture
ResultCaptureDate = DateTimeField(
    'ResultCaptureDate',
    storage=Storage,
)

# If ReportDryMatter is True in the AnalysisService, the adjusted result
# is stored here.
ResultDM = StringField(
    'ResultDM',
    storage=Storage,
)

# If the analysis has previously been retracted, this flag is set True
# to indicate that this is a re-test.
Retested = BooleanField(
    'Retested',
    storage=Storage,
    default=False,
)

# When the AR is published, the date of publication is recorded here.
# It's used to populate catalog values.
DateAnalysisPublished = DateTimeField(
    'DateAnalysisPublished',
    storage=Storage,
    widget=DateTimeWidget(
        label=_("Date Published")
    ),
)

# If the result is outside of the detection limits of the method or instrument,
# the operand (< or >) is stored here.  For routine analyses this is taken
# from the Result, if the result entered explicitly startswith "<" or ">"
DetectionLimitOperand = StringField(
    'DetectionLimitOperand',
    storage=Storage,
)

# This is used to calculate turnaround time reports.
# The value is set when the Analysis is published.
Duration = IntegerField(
    'Duration',
    storage=Storage,
)

# This is used to calculate turnaround time reports. The value is set when the
# Analysis is published.
Earliness = IntegerField(
    'Earliness',
    storage=Storage,
)

# The ID of the logged in user who submitted the result for this Analysis.
Analyst = StringField(
    'Analyst',
    storage=Storage,
)

# The actual uncertainty for this analysis' result, populated from the ranges
# specified in the analysis service when the result is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    storage=Storage,
    precision=10,
)

# transitioned to a 'verified' state. This value is set automatically
# when the analysis is created, based on the value set for the property
# NumberOfRequiredVerifications from the Analysis Service
NumberOfRequiredVerifications = IntegerField(
    'NumberOfRequiredVerifications',
    storage=Storage,
    default=1,
)

# This field keeps the user_ids of members who verified this analysis.
# After each verification, user_id will be added end of this string
# seperated by comma- ',' .
Verificators = StringField(
    'Verificators',
    storage=Storage,
    default='',
)

schema = schema.copy() + Schema((
    AnalysisService,
    Analyst,
    Attachment,
    # Calculation overrides AbstractBaseClass
    Calculation,
    DateAnalysisPublished,
    DetectionLimitOperand,
    Duration,
    Earliness,
    # NumberOfRequiredVerifications overrides AbstractBaseClass
    NumberOfRequiredVerifications,
    Result,
    ResultCaptureDate,
    ResultDM,
    Retested,
    Uncertainty,
    Verificators
))
