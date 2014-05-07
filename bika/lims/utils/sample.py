
from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType


def create_sample(context, request, client, values):
    # Retrieve the required tools
    wftool = getToolByName(context, 'portal_workflow')
    uc = getToolByName(context, 'uid_catalog')
    # Determine if the sampling workflow is enabled
    workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
    # Create sample of refer to existing for secondary analysis request
    if values.get('Sample_uid', ''):
        sample = uc(UID=values['Sample'])[0].getObject()
    else:
        sample = _createObjectByType('Sample', client, tmpID())
        # Specifically set the sample type
        sample.setSampleType(values['SampleType'])
        # Specifically set the sample point
        if 'SamplePoint' in values:
            sample.setSamplePoint(values['SamplePoint'])
        # Specifically set the storage location
        if 'StorageLocation' in values:
            sample.setStorageLocation(values['StorageLocation'])
        # Update the created sample with indicated values
        sample.processForm(REQUEST=request, values=values)
        # Implement workflow if required
        if workflow_enabled:
            wftool.doActionFor(sample, 'sampling_workflow')
        else:
            wftool.doActionFor(sample, 'no_sampling_workflow')
            # Object has been renamed
        # Set the SampleID
        sample.edit(SampleID=sample.getId())
    # Return the newly created sample
    return sample

