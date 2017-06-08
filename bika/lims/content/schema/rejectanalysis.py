# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.public import ReferenceField, Schema
from bika.lims.content.analysis import schema as analysis_schema
from bika.lims.content.schema import Storage

Analysis = ReferenceField(
    'Analysis',
    storage=Storage(),
    allowed_types=('Analysis',),
    relationship='RejectAnalysisAnalysis',
)

schema = analysis_schema.copy() + Schema((
    Analysis,
))
