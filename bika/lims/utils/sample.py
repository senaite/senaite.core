# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType


def create_sample(context, request, values):
    # Retrieve the required tools
    uc = getToolByName(context, 'uid_catalog')
    # Create sample or refer to existing for secondary analysis request
    if values.get('Sample_uid', ''):
        sample = uc(UID=values['Sample'])[0].getObject()
    else:
        sample = _createObjectByType('Sample', context, tmpID())
        # Determine if the sampling workflow is enabled
        workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
        sample.setSamplingWorkflowEnabled(workflow_enabled)
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
        # Set the SampleID
        sample.edit(SampleID=sample.getId())
    # Return the newly created sample
    return sample
