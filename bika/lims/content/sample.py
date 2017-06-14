# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Sample represents a physical sample submitted for testing
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.Archetypes import atapi
from Products.Archetypes.BaseFolder import BaseFolder
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import deprecated
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.sample import schema
from bika.lims.interfaces import ISample, ISamplePrepWorkflow
from bika.lims.utils import getUsers
from bika.lims.utils import to_unicode
from bika.lims.workflow.sample import events
from bika.lims.workflow.sample import guards
from zope.interface import implements


class Sample(BaseFolder, HistoryAwareMixin):
    implements(ISample, ISamplePrepWorkflow)
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

    def getSampleID(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')

    def Title(self):
        """ Return the Sample ID as title """
        return self.getSampleID()

    def getSamplingWorkflowEnabledDefault(self):
        return self.bika_setup.getSamplingWorkflowEnabled()

    def getContactTitle(self):
        return ""

    def getClientTitle(self):
        proxies = self.getAnalysisRequests()
        if not proxies:
            return ""
        value = proxies[0].aq_parent.Title()
        return value

    def getProfilesTitle(self):
        return ""

    def getAnalysisService(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.Title()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...

    def setSampleType(self, value, **kw):
        """ Accept Object, Title or UID, and convert SampleType title to UID
        before saving.
        """
        if hasattr(value, "portal_type") and value.portal_type == "SampleType":
            pass
        else:
            bsc = getToolByName(self, 'bika_setup_catalog')
            sampletypes = bsc(portal_type='SampleType', title=to_unicode(value))
            if sampletypes:
                value = sampletypes[0].UID
            else:
                sampletypes = bsc(portal_type='SampleType', UID=value)
                if sampletypes:
                    value = sampletypes[0].UID
                else:
                    value = None
        for ar in self.getAnalysisRequests():
            ar.Schema()['SampleType'].set(ar, value, **kw)
        return self.Schema()['SampleType'].set(self, value, **kw)

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSamplePoint(self, value, **kw):
        """ Accept Object, Title or UID, and convert SampleType title to UID
        before saving.
        """
        if hasattr(value, "portal_type") and value.portal_type == "SamplePoint":
            pass
        else:
            bsc = getToolByName(self, 'bika_setup_catalog')
            sampletypes = bsc(portal_type='SamplePoint', title=to_unicode(
                value))
            if sampletypes:
                value = sampletypes[0].UID
            else:
                sampletypes = bsc(portal_type='SamplePoint', UID=value)
                if sampletypes:
                    value = sampletypes[0].UID
                else:
                    value = None
        for ar in self.getAnalysisRequests():
            ar.Schema()['SamplePoint'].set(ar, value, **kw)
        return self.Schema()['SamplePoint'].set(self, value, **kw)

    def setClientReference(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['ClientReference'].set(ar, value, **kw)
        self.Schema()['ClientReference'].set(self, value, **kw)

    def setClientSampleID(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['ClientSampleID'].set(ar, value, **kw)
        self.Schema()['ClientSampleID'].set(self, value, **kw)

    def setAdHoc(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['AdHoc'].set(ar, value, **kw)
        self.Schema()['AdHoc'].set(self, value, **kw)

    def setComposite(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['Composite'].set(ar, value, **kw)
        self.Schema()['Composite'].set(self, value, **kw)

    security.declarePublic('getAnalysisRequests')

    def getAnalysisRequests(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        ars = []
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisRequestSample')]
        for uid in uids:
            reference = uid
            ar = tool.lookupObject(reference.sourceUID)
            ars.append(ar)
        return ars

    security.declarePublic('getAnalyses')

    def getAnalyses(self, contentFilter):
        """ return list of all analyses against this sample
        """
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += ar.getAnalyses(**contentFilter)
        return analyses

    def getSamplers(self):
        return getUsers(self, ['LabManager', 'Sampler'])

    def disposal_date(self):
        """ Calculate the disposal date by returning the latest
            disposal date in this sample's partitions """

        parts = self.objectValues("SamplePartition")
        dates = []
        for part in parts:
            date = part.getDisposalDate()
            if date:
                dates.append(date)
        if dates:
            dis_date = dt2DT(max([DT2dt(date) for date in dates]))
        else:
            dis_date = None
        return dis_date

    def getLastARNumber(self):
        ARs = self.getBackReferences("AnalysisRequestSample")
        prefix = self.getSampleType().getPrefix()
        ar_ids = sorted([AR.id for AR in ARs if AR.id.startswith(prefix)])
        try:
            last_ar_number = int(ar_ids[-1].split("-R")[-1])
        except (ValueError, TypeError):
            return 0
        return last_ar_number

    def getSampleState(self):
        """Returns the sample veiew_state
        """
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(self, 'review_state')

    def getPreparationWorkflows(self):
        """Return a list of sample preparation workflows.  These are identified
        by scanning all workflow IDs for those beginning with "sampleprep".
        """
        wf = self.portal_workflow
        ids = wf.getWorkflowIds()
        sampleprep_ids = [wid for wid in ids if wid.startswith('sampleprep')]
        prep_workflows = [['', ''], ]
        for workflow_id in sampleprep_ids:
            workflow = wf.getWorkflowById(workflow_id)
            prep_workflows.append([workflow_id, workflow.title])
        return DisplayList(prep_workflows)

    @deprecated('[1705] Use events.after_no_sampling_workflow from '
                'bika.lims.workflow.sample')
    @security.public
    def workflow_script_no_sampling_workflow(self):
        events.after_no_sampling_workflow(self)

    @deprecated('[1705] Use events.after_sampling_workflow from '
                'bika.lims.workflow.sample')
    @security.public
    def workflow_script_sampling_workflow(self):
        events.after_sampling_workflow(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_sample')
    @security.public
    def workflow_script_sample(self):
        events.after_sample(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_sample_due')
    @security.public
    def workflow_script_sample_due(self):
        events.after_sample_due(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_receive')
    @security.public
    def workflow_script_receive(self):
        events.after_receive(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_preserve')
    @security.public
    def workflow_script_preserve(self):
        events.after_preserve(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_expire')
    @security.public
    def workflow_script_expire(self):
        events.after_expire(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_dispose')
    @security.public
    def workflow_script_dispose(self):
        events.after_dispose(self)

    @deprecated('[1705] Use events.after_to_be_preserved from '
                'bika.lims.workflow.sample')
    @security.public
    def workflow_script_to_be_preserved(self):
        events.after_to_be_preserved(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_reinstate')
    @security.public
    def workflow_script_reinstate(self):
        events.after_reinstate(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_cancel')
    @security.public
    def workflow_script_cancel(self):
        events.after_cancel(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.events.after_reject')
    @security.public
    def workflow_script_reject(self):
        events.after_reject(self)

    @deprecated('[1705] Use events.after_schedule_sampling from '
                'bika.lims.workflow.sample')
    @security.public
    def workflow_script_schedule_sampling(self):
        events.after_schedule_sampling(self)

    @deprecated('[1705] Use guards.to_be_preserved from '
                'bika.lims.workflow.sample')
    @security.public
    def guard_to_be_preserved(self):
        return guards.to_be_preserved(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.guards.receive')
    @security.public
    def guard_receive_transition(self):
        return guards.receive(self)

    @deprecated('[1705] Use bika.lims.workflow.sample.guards.sample_prep')
    @security.public
    def guard_sample_prep_transition(self):
        return guards.sample_prep(self)

    @deprecated('[1705] Use guards.sample_prep_complete from '
                'bika.lims.workflow.sample')
    @security.public
    def guard_sample_prep_complete_transition(self):
        return guards.sample_prep_complete(self)

    @deprecated('[1705] Use guards.schedule_sampling from '
                'bika.lims.workflow.sample')
    @security.public
    def guard_schedule_sampling_transition(self):
        return guards.schedule_sampling(self)


atapi.registerType(Sample, PROJECTNAME)
