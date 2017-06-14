# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import registerType
from bika.lims import deprecated
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.schema.duplicateanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.workflow.duplicateanalysis import events
from zope.interface import implements


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
    def getSiblings(self):
        """Returns the list of duplicate analyses that share the same Request
        and are included in the same Worksheet as the current. The current
        duplicate is excluded from the list
        """
        worksheet = self.getWorksheet()
        requestuid = self.getRequestUID()
        if not requestuid or not worksheet:
            return []
        analyses = worksheet.getAnalyses()
        siblings = [an for an in analyses
                    if an.getRequestUID() == requestuid
                    and an.UID() != self.UID()]
        return siblings

    @security.public
    def setAnalysis(self, analysis):
        # Copy all the values from the schema
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

    @deprecated('[1705] Use events.after_attach from '
                'bika.lims.workflow.duplicateanalysis.events')
    def workflow_script_attach(self):
        events.after_attach(self)

    @deprecated('[1705] Use events.after_retract from '
                'bika.lims.workflow.duplicateanalysis.events')
    @security.public
    def workflow_script_retract(self):
        events.after_retract(self)

    @deprecated('[1705] Use events.after_verify from '
                'bika.lims.workflow.duplicateanalysis.events')
    @security.public
    def workflow_script_verify(self):
        events.after_verify(self)


registerType(DuplicateAnalysis, PROJECTNAME)
