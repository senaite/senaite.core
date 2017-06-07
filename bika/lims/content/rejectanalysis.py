# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import Analysis
from bika.lims.content.schema.rejectanalysis import schema
from bika.lims.interfaces import IRejectAnalysis
from zope.interface import implements


class RejectAnalysis(Analysis):
    implements(IRejectAnalysis)
    security = ClassSecurityInfo()

    schema = schema

    @security.public
    def getSample(self):
        return self.aq_parent


registerType(RejectAnalysis, PROJECTNAME)
