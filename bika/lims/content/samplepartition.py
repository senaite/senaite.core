# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from bika.lims import deprecated
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISamplePartition, ISamplePrepWorkflow
from bika.lims.workflow import doActionFor
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow import skip
from DateTime import DateTime
from datetime import timedelta
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.api.portal import get_tool
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('Container',
        allowed_types=('Container',),
        relationship='SamplePartitionContainer',
        required=1,
        multiValued=0,
    ),
    ReferenceField('Preservation',
        allowed_types=('Preservation',),
        relationship='SamplePartitionPreservation',
        required=0,
        multiValued=0,
    ),
    BooleanField('Separate',
        default=False
    ),
    ReferenceField('Analyses',
        allowed_types=('Analysis',),
        relationship='SamplePartitionAnalysis',
        required=0,
        multiValued=1,
    ),
    DateTimeField('DatePreserved',
    ),
    StringField('Preserver',
        searchable=True
    ),
    DurationField('RetentionPeriod',
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
)
)

schema['title'].required = False


class SamplePartition(BaseContent, HistoryAwareMixin):
    implements(ISamplePartition, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')

    @security.public
    def getAnalyses(self):
        """Returns a list of analyses linked to this sample Partition
        TODO: Refactor to only return full objects if requested!
        """
        bac = get_tool('bika_analysis_catalog')
        brains = bac(portal_type='Analysis', getSamplePartitionUID=self.UID())
        analyses = [b.getObject() for b in brains]
        return analyses

    @security.public
    def current_date(self):
        """ return current date """
        return DateTime()

    @security.public
    def disposal_date(self):
        """ return disposal date """

        DateSampled = self.getDateSampled()

        # fallback to sampletype retention period
        st_retention = self.aq_parent.getSampleType().getRetentionPeriod()

        # but prefer retention period from preservation
        pres = self.getPreservation()
        pres_retention = pres and pres.getRetentionPeriod() or None

        rp = pres_retention and pres_retention or None
        rp = rp or st_retention

        td = timedelta(
            days='days' in rp and int(rp['days']) or 0,
            hours='hours' in rp and int(rp['hours']) or 0,
            minutes='minutes' in rp and int(rp['minutes']) or 0)

        dis_date = DateSampled and dt2DT(DT2dt(DateSampled) + td) or None
        return dis_date

    def workflow_script_preserve(self):
        workflow = getToolByName(self, 'portal_workflow')
        sample = self.aq_parent
        # Transition our analyses
        analyses = self.getAnalyses()
        if analyses:
            for analysis in analyses:
                doActionFor(analysis, "preserve")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved', ]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "preserve")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "preserve")

    def workflow_transition_expire(self):
        self.setDateExpired(DateTime())
        self.reindexObject(idxs=["review_state", "getDateExpired", ])

    def workflow_script_sample(self):
        if skip(self, "sample"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getAnalyses()
        for analysis in analyses:
            doActionFor(analysis, "sample")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', ]
            escalate = True
            for part in parts:
                pstate = workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "sample")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "sample")

    def workflow_script_to_be_preserved(self):
        if skip(self, "to_be_preserved"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getAnalyses()
        for analysis in analyses:
            doActionFor(analysis, "to_be_preserved")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved', ]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "to_be_preserved")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "to_be_preserved")

    def workflow_script_sample_due(self):
        if skip(self, "sample_due"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getAnalyses()
        for analysis in analyses:
            doActionFor(analysis, "sample_due")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_preserved', ]
            escalate = True
            for part in parts:
                pstate = workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "sample_due")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "sample_due")

    @deprecated('05-2017. Use after_receive_transition_event instead')
    def workflow_script_receive(self):
        self.after_receive_transition_event()

    @security.public
    def after_receive_transition_event(self):
        """Method triggered after a 'receive' transition for the current Sample
        Partition is performed. Stores value for "Date Received" field and also
        triggers the 'receive' transition for depedendent objects, such as
        Analyses associated to this Sample Partition. If all Sample Partitions
        that belongs to the same sample as the current Sample Partition have
        been transitioned to the "received" state, promotes to Sample
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        self.setDateReceived(DateTime())
        self.reindexObject(idxs=["getDateReceived", ])

        # Transition our analyses
        for analysis in self.getAnalyses():
            doActionFor(analysis, "receive")

        # If all sibling partitions are received, promote sample
        sample = self.aq_parent
        parts = sample.objectValues("SamplePartition")
        recep = [sp for sp in parts if wasTransitionPerformed(sp, 'receive')]
        if len(parts) == len(recep):
            doActionFor(sample, "receive")

    def workflow_script_reinstate(self):
        if skip(self, "reinstate"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are active, activate sample
        if not skip(sample, "reinstate", peek=True):
            cancelled = [sp for sp in sample.objectValues("SamplePartition")
                         if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']
            if sample_c_state == 'cancelled' and not cancelled:
                workflow.doActionFor(sample, 'reinstate')

    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are cancelled, cancel sample
        if not skip(sample, "cancel", peek=True):
            active = [sp for sp in sample.objectValues("SamplePartition")
                      if workflow.getInfoFor(sp, 'cancellation_state') == 'active']
            if sample_c_state == 'active' and not active:
                workflow.doActionFor(sample, 'cancel')

    def workflow_script_reject(self):
        workflow = getToolByName(self, 'portal_workflow')
        sample = self.aq_parent
        self.reindexObject(idxs=["review_state", ])
        sample_r_state = workflow.getInfoFor(sample, 'review_state')
        # if all sibling partitions are cancelled, cancel sample
        not_rejected = [sp for sp in sample.objectValues("SamplePartition")
                  if workflow.getInfoFor(sp, 'review_state') != 'rejected']
        if sample_r_state != 'rejected':
            workflow.doActionFor(sample, 'reject')

registerType(SamplePartition, PROJECTNAME)
