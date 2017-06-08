# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Field import BooleanField, FixedPointField, \
    StringField
from Products.Archetypes.Schema import Schema
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DecimalWidget
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.schema import Storage

# The physical sample partition linked to the Analysis.
SamplePartition = UIDReferenceField(
    'SamplePartition',
    storage=Storage(),
    required=0,
    allowed_types=('SamplePartition',),
)

# True if the analysis is created by a reflex rule
IsReflexAnalysis = BooleanField(
    'IsReflexAnalysis',
    storage=Storage(),
    default=False,
    required=0,
)

# This field contains the original analysis which was reflected
OriginalReflexedAnalysis = UIDReferenceField(
    'OriginalReflexedAnalysis',
    storage=Storage(),
    required=0,
    allowed_types=('Analysis',),
)

# This field contains the analysis which has been reflected following
# a reflex rule
ReflexAnalysisOf = UIDReferenceField(
    'ReflexAnalysisOf',
    storage=Storage(),
    required=0,
    allowed_types=('Analysis',),
)

# Which is the Reflex Rule action that has created this analysis
ReflexRuleAction = StringField(
    'ReflexRuleAction',
    storage=Storage(),
    required=0,
    default=0,
)

# Which is the 'local_id' inside the reflex rule
ReflexRuleLocalID = StringField(
    'ReflexRuleLocalID',
    storage=Storage(),
    required=0,
    default=0,
)

# Reflex rule triggered actions which the current analysis is responsible for.
# Separated by '|'
ReflexRuleActionsTriggered = StringField(
    'ReflexRuleActionsTriggered',
    storage=Storage(),
    required=0,
    default='',
)

# The actual uncertainty for this analysis' result, populated when the result
# is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    storage=Storage(),
    precision=10,
    widget=DecimalWidget(
        label=_("Uncertainty")
    ),
)

schema = schema.copy() + Schema((
    IsReflexAnalysis,
    OriginalReflexedAnalysis,
    ReflexAnalysisOf,
    ReflexRuleAction,
    ReflexRuleActionsTriggered,
    ReflexRuleLocalID,
    SamplePartition,
    Uncertainty,
))
