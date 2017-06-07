# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.content.schema import Storage

# A reference back to the original analysis from which this one was duplicated.
Analysis = UIDReferenceField(
    'Analysis',
    storage=Storage,
    required=1,
    allowed_types=('Analysis', 'ReferenceAnalysis'),
)

# TODO Analysis - Duplicates shouldn't have this attribute, only ReferenceAns
ReferenceAnalysesGroupID = StringField(
    'ReferenceAnalysesGroupID',
    storage=Storage,
)

schema = schema.copy() + Schema((
    Analysis,
    ReferenceAnalysesGroupID,
))
