# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import ReferenceField, Schema, registerType
from bika.lims.content.analysis import Analysis
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import schema as analysis_schema
from bika.lims.interfaces import IRejectAnalysis
from zope.interface import implements

schema = analysis_schema + Schema((
    # The analysis that was originally rejected
    ReferenceField(
        'Analysis',
        allowed_types=('Analysis',),
        relationship='RejectAnalysisAnalysis',
    ),
))


class RejectAnalysis(Analysis):
    implements(IRejectAnalysis)
    security = ClassSecurityInfo()

    schema = schema

    @security.public
    def getSample(self):
        return self.aq_parent


registerType(RejectAnalysis, PROJECTNAME)
