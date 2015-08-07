from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import ISample
from bika.lims.utils import tmpID
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
from Products.CMFPlone.utils import _createObjectByType


def create_analysisrequest(
    context,
    request,
    values,
    analyses=[],
    partitions=None,
    specifications=None,
    prices=None
):
    # Gather neccesary tools
    workflow = getToolByName(context, 'portal_workflow')
    bc = getToolByName(context, 'bika_catalog')

    # Create new sample or locate the existing for secondary AR
    if values.get('Sample'):
        secondary = True
        if ISample.providedBy(values['Sample']):
            sample = values['Sample']
        else:
            sample = bc(UID=values['Sample'])[0].getObject()
        workflow_enabled = sample.getSamplingWorkflowEnabled()
    else:
        secondary = False
        workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
        sample = create_sample(context, request, values)

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', context, tmpID())
    ar.setSample(sample)

    # processform renames the sample, this requires values to contain the Sample.
    values['Sample'] = sample
    ar.processForm(REQUEST=request, values=values)

    # Object has been renamed
    ar.edit(RequestID=ar.getId())

    # Set initial AR state
    workflow_action = 'sampling_workflow' if workflow_enabled \
        else 'no_sampling_workflow'
    workflow.doActionFor(ar, workflow_action)

    # Set analysis request analyses
    analyses = ar.setAnalyses(analyses, prices=prices, specs=specifications)

    if secondary:
        # Only 'sample_due' and 'sample_recieved' samples can be selected
        # for secondary analyses
        doActionFor(ar, 'sample')
        doActionFor(ar, 'sample_due')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        if sample_state == 'sample_received':
            doActionFor(ar, 'receive')

        for analysis in ar.getAnalyses(full_objects=1):
            doActionFor(analysis, 'sample')
            doActionFor(analysis, 'sample_due')
            analysis_transition_ids = [t['id'] for t in workflow.getTransitionsFor(analysis)]
            if 'receive' in analysis_transition_ids and sample_state == 'sample_received':
                doActionFor(analysis, 'receive')

    if not secondary:
        # Create sample partitions
        if not partitions:
            partitions = [{'services':analyses}]
        for n, partition in enumerate(partitions):
            # Calculate partition id
            partition_prefix = sample.getId() + "-P"
            partition_id = '%s%s' % (partition_prefix, n + 1)
            partition['part_id'] = partition_id
            # Point to or create sample partition
            if partition_id in sample.objectIds():
                partition['object'] = sample[partition_id]
            else:
                partition['object'] = create_samplepartition(
                    sample,
                    partition,
                    analyses
                )
        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not workflow_enabled:
            to_be_preserved = []
            sample_due = []
            lowest_state = 'sample_due'
            for p in sample.objectValues('SamplePartition'):
                if p.getPreservation():
                    lowest_state = 'to_be_preserved'
                    to_be_preserved.append(p)
                else:
                    sample_due.append(p)
            for p in to_be_preserved:
                doActionFor(p, 'to_be_preserved')
            for p in sample_due:
                doActionFor(p, 'sample_due')
            doActionFor(sample, lowest_state)
            doActionFor(ar, lowest_state)

        # Transition pre-preserved partitions
        for p in partitions:
            if 'prepreserved' in p and p['prepreserved']:
                part = p['object']
                state = workflow.getInfoFor(part, 'review_state')
                if state == 'to_be_preserved':
                    workflow.doActionFor(part, 'preserve')

    # Return the newly created Analysis Request
    return ar
