# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, registerType
from Products.Archetypes.public import StringField
from bika.lims import api
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims import logger
from bika.lims.workflow import in_state
from bika.lims.workflow.analysis import STATE_RETRACTED, STATE_REJECTED
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
    def getWorksheet(self):
        return self.aq_parent

    @security.public
    def getSiblings(self, with_retests=False):
        """
        Return the list of duplicate analyses that share the same Request and
        are included in the same Worksheet as the current analysis. The current
        duplicate is excluded from the list.
        :param with_retests: If false, siblings with retests are dismissed
        :type with_retests: bool
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

            if not IRequestAnalysis.providedBy(analysis):
                # Exclude analyses that do not have an analysis request
                # associated
                continue

            if analysis.getRequestUID() != requestuid:
                # Exclude those analyses that does not belong to the same
                # analysis request I belong to
                continue

            if not with_retests:

                if in_state(analysis, retracted_states):
                    # Exclude retracted analyses
                    continue

                elif analysis.getRetest():
                    # Exclude analyses with a retest
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

    @security.public
    def getResultsRange(self):
        """Returns the valid result range for this analysis duplicate, based on
        both on the result and duplicate variation set in the original analysis

        A Duplicate will be out of range if its result does not match with the
        result for the parent analysis plus the duplicate variation in % as the
        margin error.

        If the duplicate is from an analysis with result options and/or string
        results enabled (with non-numeric value), returns an empty result range

        :return: A dictionary with the keys min and max
        :rtype: dict
        """
        # Get the original analysis
        original_analysis = self.getAnalysis()
        if not original_analysis:
            logger.warn("Orphan duplicate: {}".format(repr(self)))
            return {}

        # Return empty if results option enabled (exact match expected)
        if original_analysis.getResultOptions():
            return {}

        # Return empty if non-floatable (exact match expected)
        original_result = original_analysis.getResult()
        if not api.is_floatable(original_result):
            return {}

        # Calculate the min/max based on duplicate variation %
        specs = ResultsRangeDict(uid=self.getServiceUID())
        dup_variation = original_analysis.getDuplicateVariation()
        dup_variation = api.to_float(dup_variation, default=0)
        if not dup_variation:
            # We expect an exact match
            specs.min = specs.max = original_result
            return specs

        original_result = api.to_float(original_result)
        margin = abs(original_result) * (dup_variation / 100.0)
        specs.min = str(original_result - margin)
        specs.max = str(original_result + margin)
        return specs


registerType(DuplicateAnalysis, PROJECTNAME)
