import zope.event

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import _createObjectByType



def create_analysis(context, service, keyword, interim_fields):
    # Determine if the sampling workflow is enabled
    workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
    # Create the analysis
    analysis = _createObjectByType("Analysis", context, keyword)
    analysis.setService(service)
    analysis.setInterimFields(interim_fields)
    analysis.setMaxTimeAllowed(service.getMaxTimeAllowed())
    analysis.unmarkCreationFlag()
    analysis.reindexObject()
    # Trigger the intitialization event of the new object
    zope.event.notify(ObjectInitializedEvent(analysis))
    # Perform the appropriate workflow action
    try:
        workflow_action =  'sampling_workflow' if workflow_enabled \
            else 'no_sampling_workflow'
        context.portal_workflow.doActionFor(analysis, workflow_action)
    except WorkflowException:
        # The analysis may have been transitioned already!
        # I am leaving this code here though, to prevent regression.
        pass
    # Return the newly created analysis
    return analysis
