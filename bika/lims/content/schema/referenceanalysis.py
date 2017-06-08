# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from bika.lims.config import STD_TYPES
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.schema import Storage
from plone.app.blob.field import BlobField

ReferenceType = StringField(
    'ReferenceType',
    storage=Storage(),
    vocabulary=STD_TYPES,
)

RetractedAnalysesPdfReport = BlobField(
    'RetractedAnalysesPdfReport',
    storage=Storage(),
)

ReferenceAnalysesGroupID = StringField(
    'ReferenceAnalysesGroupID',
    storage=Storage(),
)

schema = schema.copy() + Schema((
    ReferenceType,
    RetractedAnalysesPdfReport,
    ReferenceAnalysesGroupID
))
