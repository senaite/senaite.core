from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import ISample
from bika.lims.utils import tmpID
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
from Products.CMFPlone.utils import _createObjectByType


def create_analysisrequest(context, request, values):
    """Create an AR.

    :param context the container in which the AR will be created (Client)
    :param request the request object
    :param values a dictionary containing fieldname/value pairs, which
           will be applied.  Some fields will have specific code to handle them,
           and others will be directly written to the schema.
    :return the new AR instance

    Special keys present (or required) in the values dict, which are not present
    in the schema:

        - Partitions: data about partitions to be created, and the
                      analyses that are to be assigned to each.

        - Prices: custom prices set in the HTML form.

        - ResultsRange: Specification values entered in the HTML form.

    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()
    >>> from plone.app.testing import SITE_OWNER_NAME
    >>> from plone.app.testing import SITE_OWNER_PASSWORD
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from zope.publisher.browser import TestRequest

    Now our "values" will contain a bunch of UID references, so we must create
    this variable by looking up UIDs for existing objects.
    >>> client = portal.clients.objectValues()[0]
    >>> services = [x.getObject() for x in bsc(portal:type="AnalysisService")[:5]]
    >>> containers = [x.getObject() for x in bsc(portal:type="Container")]
    >>> preservations = [x.getObject() for x in bsc(portal:type="Preservation")]
    >>> values = {'Analyses':services,
    ...           'ResultsRange': [{'uid':service, 'min':9, 'max':11, 'error':10} for service in services],
    ...           'Partitions': [
    ...             {u'part_id': u'part-1',
    ...              u'container': containers[0],
    ...              u'preservation': preservations[0],
    ...              u'services': services[:1]},
    ...             {u'part_id': u'part-2',
    ...              u'container': u'containers[1]',
    ...              u'preservation': preservations[1],
    ...              u'services': services[1:]}
    ...           ]
    ...          }

    >>> fake_request = TestRequest()
    >>> ar = create_analysisrequest(client, fake_request, values)

    >>> import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()

    """
    # Gather neccesary tools
    workflow = getToolByName(context, 'portal_workflow')
    bc = getToolByName(context, 'bika_catalog')

    # Create new sample or locate the existing for secondary AR
    if values['Sample']:
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
    ar.setAnalyses(values['Analyses'],
                   prices=values.get("Prices", []),
                   specs=values.get('ResultsRange', []))
    analyses = ar.getAnalyses(full_objects=True)

    skip_receive = ['to_be_sampled', 'sample_due', 'sampled', 'to_be_preserved']
    if secondary:
        # Only 'sample_due' and 'sample_recieved' samples can be selected
        # for secondary analyses
        doActionFor(ar, 'sampled')
        doActionFor(ar, 'sample_due')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        if sample_state not in skip_receive:
            doActionFor(ar, 'receive')

    for analysis in analyses:
        doActionFor(analysis, 'sample_due')
        analysis_state = workflow.getInfoFor(analysis, 'review_state')
        if analysis_state not in skip_receive:
            doActionFor(analysis, 'receive')

    if not secondary:
        # Create sample partitions
        partitions = []
        for n, partition in enumerate(values['Partitions']):
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
                    partition
                )
            # now assign analyses to this partition.
            obj = partition['object']
            for analysis in analyses:
                if analysis.getService().UID() in partition['services']:
                    analysis.setSamplePartition(obj)

            partitions.append(partition)

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
