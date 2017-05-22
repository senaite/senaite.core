# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Field import BooleanField, FixedPointField, \
    StringField
from Products.Archetypes.Schema import Schema
from bika.lims import bikaMessageFactory as _, logger
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DecimalWidget
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.interfaces import IAnalysis, IRoutineAnalysis, \
    ISamplePrepWorkflow
from bika.lims.workflow import getTransitionDate
from plone.api.portal import get_tool
from zope.interface import implements

# The physical sample partition linked to the Analysis.
SamplePartition = UIDReferenceField(
    'SamplePartition',
    required=0,
    allowed_types=('SamplePartition',)
)

# True if the analysis is created by a reflex rule
IsReflexAnalysis = BooleanField(
    'IsReflexAnalysis',
    default=False,
    required=0
)

# This field contains the original analysis which was reflected
OriginalReflexedAnalysis = UIDReferenceField(
    'OriginalReflexedAnalysis',
    required=0,
    allowed_types=('Analysis',)
)

# This field contains the analysis which has been reflected following
# a reflex rule
ReflexAnalysisOf = UIDReferenceField(
    'ReflexAnalysisOf',
    required=0,
    allowed_types=('Analysis',)
)

# Which is the Reflex Rule action that has created this analysis
ReflexRuleAction = StringField(
    'ReflexRuleAction',
    required=0,
    default=0
)

# Which is the 'local_id' inside the reflex rule
ReflexRuleLocalID = StringField(
    'ReflexRuleLocalID',
    required=0,
    default=0
)

# Reflex rule triggered actions which the current analysis is responsible for.
# Separated by '|'
ReflexRuleActionsTriggered = StringField(
    'ReflexRuleActionsTriggered',
    required=0,
    default=''
)

# The actual uncertainty for this analysis' result, populated when the result
# is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    precision=10,
    widget=DecimalWidget(
        label=_("Uncertainty")
    )
)

schema = schema.copy() + Schema((
    IsReflexAnalysis,
    OriginalReflexedAnalysis,
    ReflexAnalysisOf,
    ReflexRuleAction,
    ReflexRuleActionsTriggered,
    ReflexRuleLocalID,
    SamplePartition,
    Uncertainty,
))


class AbstractRoutineAnalysis(AbstractAnalysis):
    implements(IAnalysis, IRoutineAnalysis, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getRequest(self):
        """Returns the Analysis Request this analysis belongs to.
        Delegates to self.aq_parent
        """
        ar = self.aq_parent
        return ar

    @security.public
    def getRequestID(self):
        """Used to populate catalog values.
        Returns the ID of the parent analysis request.
        """
        ar = self.getRequest()
        if ar:
            return ar.getId()

    @security.public
    def getClientTitle(self):
        """Used to populate catalog values.
        Returns the Title of the client for this analysis' AR.
        """
        client = self.getRequest().getClient()
        if client:
            return client.Title()

    @security.public
    def getClientUID(self):
        """Used to populate catalog values.
        Returns the UID of the client for this analysis' AR.
        """
        client = self.getRequest().getClient()
        if client:
            return client.UID()

    @security.public
    def getClientURL(self):
        """This method is used to populate catalog values
        Returns the URL of the client for this analysis' AR.
        """
        client = self.getRequest().getClient()
        if client:
            return client.absolute_url_path()

    @security.public
    def getClientOrderNumber(self):
        """Used to populate catalog values.
        Returns the ClientOrderNumber of the associated AR
        """
        return self.getRequest().getClientOrderNumber()

    @security.public
    def getDateReceived(self):
        """Used to populate catalog values.
        Returns the date on which the "receive" transition was invoked on this
        analysis' Sample.
        """
        sample = self.getSample()
        if sample:
            getTransitionDate(self, 'receive')

    @security.public
    def getDateSampled(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            getTransitionDate(self, 'sample')

    @security.public
    def getSamplePartitionUID(self):
        part = self.getSamplePartition()
        if part:
            return part.UID()

    @security.public
    def getSamplePointUID(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            samplepoint = sample.getSamplePoint()
            if samplepoint:
                return samplepoint.UID()

    @security.public
    def getSamplePartitionID(self):
        """Used to populate catalog values.
        Returns the sample partition ID
        """
        partition = self.getSamplePartition()
        if partition:
            return partition.getId()
        return ''

    @security.public
    def getDueDate(self):
        """Used to populate getDueDate index and metadata.
        This calculates the difference between the time that the sample
        partition associated with this analysis was recieved, and the
        maximum turnaround time.
        """
        maxtime = self.getMaxTimeAllowed()
        if not maxtime:
            maxtime = get_tool('bika_setup').getDefaultTurnaroundTime()
        max_days = float(maxtime.get('days', 0)) + (
            (float(maxtime.get('hours', 0)) * 3600 +
             float(maxtime.get('minutes', 0)) * 60)
            / 86400
        )
        part = self.getSamplePartition()
        if part:
            starttime = part.getDateReceived()
            duetime = starttime + max_days if starttime else ''
            return duetime

    @security.public
    def getAnalysisRequestTitle(self):
        """This is a catalog metadata column
        """
        return self.getRequest().Title()

    @security.public
    def getAnalysisRequestUID(self):
        """This method is used to populate catalog values
        """
        return self.getRequest().UID()

    @security.public
    def getAnalysisRequestURL(self):
        """This is a catalog metadata column
        """
        return self.getRequest().absolute_url_path()

    @security.public
    def getSampleTypeUID(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            sampletype = sample.getSampleType()
            if sampletype:
                return sampletype.UID()

    @security.public
    def setReflexAnalysisOf(self, analysis):
        """Sets the analysis that has been reflexed in order to create this
        one, but if the analysis is the same as self, do nothing.
        :param analysis: an analysis object or UID
        """
        if not analysis or analysis.UID() == self.UID():
            pass
        else:
            self.getField('ReflexAnalysisOf').set(self, analysis)

    @security.public
    def addReflexRuleActionsTriggered(self, text):
        """This function adds a new item to the string field
        ReflexRuleActionsTriggered. From the field: Reflex rule triggered
        actions from which the current analysis is responsible of. Separated
        by '|'
        :param text: is a str object with the format '<UID>.<rulename>' ->
        '123354.1'
        """
        old = self.getReflexRuleActionsTriggered()
        self.setReflexRuleActionsTriggered(old + text + '|')
