# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IAnalysis, ISamplePrepWorkflow
from zope.interface import implements

schema = schema.copy() + Schema((

))


class Analysis(AbstractRoutineAnalysis):
    implements(IAnalysis, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getSample(self):
        ar = self.aq_parent
        if ar:
            sample = ar.getSample()
            return sample
