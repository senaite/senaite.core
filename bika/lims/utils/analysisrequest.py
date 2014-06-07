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
    portal_workflow = context.portal_workflow
    # Determine if the sampling workflow is enabled
    workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
    # Create the sample
    sample = create_sample(context, request, values)
    values['Sample'] = sample
    values['Sample_uid'] = sample.UID()
    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', context, tmpID())
    ar.setSample(sample)
    ar.processForm(REQUEST=request, values=values)
    # Object has been renamed
    ar.edit(RequestID=ar.getId())
    # Set analysis request analyses
    analyses = ar.setAnalyses(analyses, prices=prices, specs=specifications)
    # Create sample partitions
    for n, partition in enumerate(partitions):
        # Calculate partition id
        partition_prefix = sample.getId() + "-P"
        partition_id = '%s%s' % (partition_prefix, n + 1)
        # Point to or create sample partition
        if partition_id in sample.objectIds():
            partition['object'] = sample[partition_id]
        else:
            partition['object'] = create_samplepartition(
                sample,
                partition,
                analyses
            )
    # Perform the appropriate workflow action
    workflow_action =  'sampling_workflow' if workflow_enabled \
        else 'no_sampling_workflow'
    portal_workflow.doActionFor(ar, workflow_action)
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
    # Receive secondary AR
    if values.get('Sample_uid', ''):
        doActionFor(ar, 'sampled')
        doActionFor(ar, 'sample_due')
        not_receive = [
            'to_be_sampled', 'sample_due', 'sampled', 'to_be_preserved'
        ]
        sample_state = portal_workflow.getInfoFor(sample, 'review_state')
        if sample_state not in not_receive:
            doActionFor(ar, 'receive')
        for analysis in ar.getAnalyses(full_objects=1):
            doActionFor(analysis, 'sampled')
            doActionFor(analysis, 'sample_due')
            if sample_state not in not_receive:
                doActionFor(analysis, 'receive')
    # Transition pre-preserved partitions
    for p in partitions:
        if 'prepreserved' in p and p['prepreserved']:
            part = p['object']
            state = portal_workflow.getInfoFor(part, 'review_state')
            if state == 'to_be_preserved':
                portal_workflow.doActionFor(part, 'preserve')
    # Return the newly created Analysis Request
    return ar
