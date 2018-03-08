# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, registerType
from bika.lims import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IRoutineAnalysis, ISamplePrepWorkflow
from bika.lims.workflow import getCurrentState, in_state
from bika.lims.workflow.analysis import STATE_RETRACTED, STATE_REJECTED
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
    def getSiblings(self, retracted=False):
        """
        Returns the list of analyses of the Analysis Request to which this
        analysis belongs to, but with the current analysis excluded.
        :param retracted: If false, retracted/rejected siblings are dismissed
        :type retracted: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        request = self.getRequest()
        if not request:
            return []

        siblings = []
        retracted_states = [STATE_RETRACTED, STATE_REJECTED]
        ans = request.getAnalyses(full_objects=True)
        for sibling in ans:
            if sibling.UID() == self.UID():
                # Exclude me from the list
                continue

            if retracted is False and in_state(sibling, retracted_states):
                # Exclude retracted analyses
                continue

            siblings.append(sibling)

        return siblings

    def workflow_script_publish(self):
        """
        If this is not here, acquisition causes recursion into
        AR workflow_script_publish method and, if there are enough
        analyses, it will result in "RuntimeError: maximum recursion
        depth exceeded"
        """ 
        pass

registerType(Analysis, PROJECTNAME)
