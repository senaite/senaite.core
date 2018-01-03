# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, registerType
from Products.Archetypes.public import StringField
from bika.lims import deprecated
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.subscribers import skip
from bika.lims.workflow import in_state
from bika.lims.workflow.analysis import STATE_RETRACTED, STATE_REJECTED
from bika.lims.workflow.duplicateanalysis import events
from zope.interface import implements

# A reference back to the original analysis from which this one was duplicated.
Analysis = UIDReferenceField(
    'Analysis',
    required=1,
    allowed_types=('Analysis', 'ReferenceAnalysis'),
)

# TODO Analysis - Duplicates shouldn't have this attribute, only ReferenceAns
ReferenceAnalysesGroupID = StringField(
    'ReferenceAnalysesGroupID',
)

schema = schema.copy() + Schema((
    Analysis,
    ReferenceAnalysesGroupID,
))


class DuplicateAnalysis(AbstractRoutineAnalysis):
    implements(IDuplicateAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getRequest(self):
        """Returns the Analysis Request of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.getRequest()

    @security.public
    def getAnalysisPortalType(self):
        """This returns the portal_type of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.portal_type

    @security.public
    def getSample(self):
        """Returns the Sample of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.getSample()

    @security.public
    def getWorksheet(self):
        return self.aq_parent

    @security.public
    def getSiblings(self, retracted=False):
        """
        Return the list of duplicate analyses that share the same Request and
        are included in the same Worksheet as the current analysis. The current
        duplicate is excluded from the list.
        :param retracted: If false, retracted/rejected siblings are dismissed
        :type retracted: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        worksheet = self.getWorksheet()
        requestuid = self.getRequestUID()
        if not requestuid or not worksheet:
            return []

        siblings = []
        retracted_states = [STATE_RETRACTED, STATE_REJECTED]
        analyses = worksheet.getAnalyses()
        for analysis in analyses:
            if analysis.UID() == self.UID():
                # Exclude me from the list
                continue

            if IRequestAnalysis.providedBy(analysis) is False:
                # Exclude analyses that do not have an analysis request
                # associated
                continue

            if analysis.getRequestUID() != requestuid:
                # Exclude those analyses that does not belong to the same
                # analysis request I belong to
                continue

            if retracted is False and in_state(analysis, retracted_states):
                # Exclude retracted analyses
                continue

            siblings.append(analysis)

        return siblings

    @security.public
    def setAnalysis(self, analysis):
        # Copy all the values from the schema
        if not analysis:
            return
        discard = ['id', ]
        keys = analysis.Schema().keys()
        for key in keys:
            if key in discard:
                continue
            if key not in self.Schema().keys():
                continue
            val = analysis.getField(key).get(analysis)
            self.getField(key).set(self, val)
        self.getField('Analysis').set(self, analysis)

    def workflow_script_attach(self):
        events.after_attach(self)

    @security.public
    def workflow_script_retract(self):
        events.after_retract(self)

    @security.public
    def workflow_script_verify(self):
        events.after_verify(self)


registerType(DuplicateAnalysis, PROJECTNAME)
