# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import ReferenceField, Schema, registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import Analysis
from bika.lims.content.analysis import schema as analysis_schema
from bika.lims.interfaces import IRejectAnalysis
from zope.interface import implements


schema = analysis_schema.copy() + Schema((
    ReferenceField(
        'Analysis',
        allowed_types=('Analysis',),
        relationship='RejectAnalysisAnalysis'
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
