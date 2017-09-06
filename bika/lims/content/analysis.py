# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, registerType
from bika.lims import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IRoutineAnalysis, ISamplePrepWorkflow
from zope.interface import implements

schema = schema.copy() + Schema((

))


class Analysis(AbstractRoutineAnalysis):
    implements(IRoutineAnalysis, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getSample(self):
        ar = self.aq_parent
        if ar:
            sample = ar.getSample()
            return sample

    @security.public
    def getClientSampleID(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            return sample.getClientSampleID()

    @security.public
    def getSiblings(self):
        """Returns the list of analyses of the Analysis Request to which this
        analysis belongs to, but with the current analysis excluded
        """
        siblings = []
        request = self.getRequest()
        if request:
            ans = request.getAnalyses(full_objects=True)
            siblings = [an for an in ans if an.UID() != self.UID()]
        return siblings


registerType(Analysis, PROJECTNAME)
