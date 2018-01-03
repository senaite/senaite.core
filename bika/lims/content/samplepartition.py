# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


from AccessControl import ClassSecurityInfo
from bika.lims import deprecated
from bika.lims.browser.fields import UIDReferenceField
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
    UIDReferenceField('Analyses',
        allowed_types=('Analysis',),
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

    def _cascade_promote_transition(self, actionid, targetstate):
        """ Performs the transition for the actionid passed in to its children
        (Analyses). If all sibling partitions are in the targe state, promotes
        the transition to its parent Sample
        """
        # Transition our analyses
        for analysis in self.getAnalyses():
            doActionFor(analysis, actionid)

        # If all sibling partitions are received, promote Sample. Sample
        # transition will, in turn, transition the Analysis Requests
        sample = self.aq_parent
        parts = sample.objectValues("SamplePartition")
        recep = [sp for sp in parts if wasTransitionPerformed(sp, targetstate)]
        if len(parts) == len(recep):
            doActionFor(sample, actionid)

    @security.public
    def after_no_sampling_workflow_transition_event(self):
        """Method triggered after a 'no_sampling_workflow' transition for the
        current Sample is performed. Triggers the 'no_sampling_workflow'
        transition for depedendent objects, such as Sample Partitions and
        Analysis Requests.
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        self._cascade_promote_transition('no_sampling_workflow', 'sampled')

    @security.public
    def after_sampling_workflow_transition_event(self):
        """Method triggered after a 'sampling_workflow' transition for the
        current Sample is performed. Triggers the 'sampling_workflow'
        transition for depedendent objects, such as Sample Partitions and
        Analysis Requests.
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        self._cascade_promote_transition('sampling_workflow', 'to_be_sampled')

    @security.public
    def after_sample_transition_event(self):
        """Method triggered after a 'sample' transition for the current
        SamplePartition is performed. Triggers the 'sample' transition for
        depedendent objects, such as Analyses
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        self._cascade_promote_transition('sample', 'sampled')

    @security.public
    def after_sample_due_transition_event(self):
        """Method triggered after a 'sample_due' transition for the current
        SamplePartition is performed. Triggers the 'sample_due' transition for
        depedendent objects, such as Analyses
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        self._cascade_promote_transition('sample_due', 'sample_due')

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
        self._cascade_promote_transition('receive', 'sample_received')

    def guard_to_be_preserved(self):
        """ Returns True if this Sample Partition needs to be preserved
        Returns false if no analyses have been assigned yet, or the Sample
        Partition has Preservation and Container objects assigned with the
        PrePreserved option set for the latter.
        """
        if not self.getPreservation():
            return False

        if not self.getAnalyses():
            return False

        container = self.getContainer()
        if container and container.getPrePreserved():
            return False

        return True

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
