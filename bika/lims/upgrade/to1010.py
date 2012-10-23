import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName

def addBatches(tool):
    """
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    setup = portal.portal_setup

    # reimport Types Tool to add BatchFolder and Batch
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    # reimport Workflows to add bika_batch_workflow
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    typestool = getToolByName(portal, 'portal_types')
    workflowtool = getToolByName(portal, 'portal_workflow')

    # Add the BatchFolder at /batches
    typestool.constructContent(type_name="BatchFolder",
                               container=portal,
                               id='batches',
                               title='Batches')
    obj = portal['batches']
    obj.unmarkCreationFlag()
    obj.reindexObject()

    # and place it after ClientFolder
    portal.moveObjectToPosition('batches', portal.objectIds().index('clients'))

    # add Batch to all AnalysisRequest objects.
    # When the objects are reindexed, BatchUID will also be populated
    proxies = portal_catalog(portal_type="AnalysiRequest")
    ars = (proxy.getObject() for proxy in proxies)
    for ar in ars:
        ar.setBatch(None)

    return True
