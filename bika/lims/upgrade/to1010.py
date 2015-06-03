import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def addBatches(tool):
    """
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    workflowtool = getToolByName(portal, 'portal_workflow')
    setup = portal.portal_setup

    # reimport Types Tool to add BatchFolder and Batch
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # Changes to the catalogs
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Batch', ['bika_catalog', ])
    at.setCatalogsByType('BatchLabel', ['bika_setup_catalog', ])
    bc = getToolByName(portal, 'bika_catalog')

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
    proxies = portal_catalog(portal_type="AnalysiRequest")
    ars = (proxy.getObject() for proxy in proxies)
    for ar in ars:
        ar.setBatch(None)

    # reimport Workflows to add bika_batch_workflow
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    # reimport jsregistry.xml to add batch.js
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # reimport factorytool to add batch.js
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')

    # add new types not to list in nav
    # Batch
    portal_properties = getToolByName(portal, 'portal_properties')
    ntp = getattr(portal_properties, 'navtree_properties')
    types = list(ntp.getProperty('metaTypesNotToList'))
    types.append("Batch")
    types.append("BatchLabel")
    ntp.manage_changeProperties(MetaTypesNotToQuery=types)

    # Add Prefix for new type
    prefixes = portal.bika_setup.getPrefixes()
    if 'Batch' not in [p['portal_type'] for p in prefixes]:
        prefixes.append({'portal_type':'Batch', 'prefix':'B', 'padding':'3'})


    # batch permission defaults
    mp = portal.manage_permission
    mp(AddBatch, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)

    # /batches folder permissions
    mp = portal.batches.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Authenticated'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Authenticated'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
    portal.batches.reindexObject()

    # bug fix - view perms on bika_setup should be easier
    mp = portal.bika_setup.manage_permission
    mp('Access contents information', ['Authenticated'], 1)
    mp(permissions.View, ['Authenticated'], 1)
    portal.bika_setup.reindexObject()
    mp = portal.bika_setup.laboratory.manage_permission
    mp('Access contents information', ['Authenticated'], 1)
    mp(permissions.View, ['Authenticated'], 1)
    portal.bika_setup.laboratory.reindexObject()

    return True
