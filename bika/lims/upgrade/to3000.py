"""Upgrades an instance from rc3.4 (1104) to v3 (3000)."""

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    at = getToolByName(portal, 'archetype_tool')
    bc = getToolByName(portal, 'bika_catalog')
    bac = getToolByName(portal, 'bika_analysis_catalog')
    bsc = getToolByName(portal, 'bika_setup_catalog')
    pc = getToolByName(portal, 'portal_catalog')
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    portal_groups = portal.portal_groups
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')
    wf = getToolByName(portal, 'portal_workflow')

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'repositorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'portlets', run_dependencies=False)
    setup.runImportStepFromProfile('profile-bika.lims:default', 'viewlets')
    setup.runImportStepFromProfile('profile-plone.app.jquery:default', 'jsregistry')

    # Add RegulatoryInspectors group and RegulatoryInspector role.
    # Fix permissions: LabClerks don't see analysis results
    role = 'RegulatoryInspector'
    group = 'RegulatoryInspectors'
    if role not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole(role)
        portal._addRole(role)

    if group not in portal_groups.listGroupIds():
        portal_groups.addGroup('RegulatoryInspectors',
                           title="Regulatory Inspectors",
                           roles=['Member', 'RegulatoryInspector', ])
    else:
        portal_groups.setRolesForGroup('RegulatoryInspectors',
                                       ['Member', 'RegulatoryInspector', ])

    # Add SampleConditions
    at.setCatalogsByType('SampleCondition', ['bika_setup_catalog'])
    if not portal['bika_setup'].get('bika_sampleconditions'):
        typestool.constructContent(type_name="SampleConditions",
                                   container=portal['bika_setup'],
                                   id='bika_sampleconditions',
                                   title='Sample Conditions')
    obj = portal['bika_setup']['bika_sampleconditions']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    # Add SampleCondition to all Sample objects
    proxies = portal_catalog(portal_type="Sample")
    samples = (proxy.getObject() for proxy in proxies)
    for sample in samples:
        sample.setSampleCondition(None)

    # Some catalog indexes were added or modified
    if 'getSampleTypeTitle' in bc.indexes():
        bc.delIndex('getSampleTypeTitle')
    if 'getSamplePointTitle' in bc.indexes():
        bc.delIndex('getSamplePointTitle')
    bc.addIndex('getSampleTypeTitle', 'KeywordIndex')
    bc.addIndex('getSamplePointTitle', 'KeywordIndex')

    if 'getClientSampleID' not in pc.indexes():
        pc.addIndex('getClientSampleID', 'FieldIndex')
        pc.addColumn('getClientSampleID')
    if 'getParentUID' not in pc.indexes():
        pc.addIndex('getParentUID', 'FieldIndex')
        pc.addColumn('getParentUID')
    if 'getReferenceAnalysesGroupID' not in bac.indexes():
        bac.addIndex('getReferenceAnalysesGroupID', 'FieldIndex')
        bac.addColumn('getReferenceAnalysesGroupID')

    # Fix broken template partition containers
    for p in bsc(portal_type='ARTemplate'):
        o = p.getObject()
        parts = o.getPartitions()
        for i, part in enumerate(parts):
            if 'container_uid' in part:
                container = bsc(portal_type='Container',
                                UID=part['container_uid'])
                if container:
                    container = container[0].getObject()
                    parts[i]['Container'] = container.Title()
            if 'preservation_uid' in p:
                preservation = bsc(portal_type='Preservation',
                                   UID=part['preservation_uid'])
                if preservation:
                    preservation = preservation[0].getObject()
                    parts[i]['Preservation'] = preservation.Title()

    # Populate ReferenceAnalysesGroupIDs for ReferenceAnalyses
    # https://github.com/bikalabs/Bika-LIMS/issues/931
    wss = bc(portal_type='Worksheet')
    for ws in wss:
        ws = ws.getObject()
        wsangroups = {}
        codes = {}

        # Reference Analyses (not duplicates)
        refanalyses = [an for an in ws.getAnalyses()
                       if an.portal_type == 'ReferenceAnalysis'
                       or an.portal_type == 'DuplicateAnalysis']
        layout = ws.getLayout()
        for lay in layout:
            for an in refanalyses:
                if lay['analysis_uid'] == an.UID():
                    position = lay['position']
                    if position not in wsangroups.keys():
                        wsangroups[position] = []
                    wsangroups[position].append(an)

        for position, wsgroup in wsangroups.iteritems():
            analysis = wsgroup[0]
            if analysis.portal_type == 'ReferenceAnalysis':
                refsampleid = wsgroup[0].aq_parent.id
            else:
                # Duplicate
                _analysis = wsgroup[0].getAnalysis()
                if _analysis.portal_type == 'ReferenceAnalysis':
                    refsampleid = _analysis.aq_parent.id
                else:
                    refsampleid = wsgroup[0].getSamplePartition().id
            codre = refsampleid
            codws = '%s_%s' % (refsampleid, ws.UID())
            codgr = '%s_%s_%s' % (refsampleid, ws.UID(), position)
            if codgr in codes.keys():
                postfix = codes[codgr]
            elif codws in codes.keys():
                postfix = codes[codws]
                codes[codgr] = postfix
                codes[codws] = postfix + 1
            elif codre in codes.keys():
                postfix = codes[codre]
                codes[codgr] = postfix
                codes[codws] = postfix + 1
                codes[codre] = postfix + 1
            else:
                postfix = 1
                codes[codre] = postfix + 1

            for an in wsgroup:
                if an.portal_type == 'DuplicateAnalysis':
                    postfix = str(postfix).zfill(int(2))
                    refgid = '%s-D%s' % (refsampleid, postfix)
                else:
                    postfix = str(postfix).zfill(int(3))
                    refgid = '%s-%s' % (refsampleid, postfix)
                an.setReferenceAnalysesGroupID(refgid)

    # Re-import the default permission maps
    gen = BikaGenerator()
    gen.setupPermissions(portal)

    logger.info("Updating workflow role/permission mappings")
    wf.updateRoleMappings()

    logger.info("Reindex added indexes in portal_catalog")
    pc.manage_reindexIndex(ids=['getClientSampleID', 'getParentUID',])

    logger.info("Reindex added indexes in bika_analysis_catalog")
    bac.manage_reindexIndex(ids=['getReferenceAnalysesGroupID',])

    logger.info("Reindex added indexes in bika_catalog")
    bc.manage_reindexIndex(ids=['getSampleTypeTitle', 'getSamplePointTitle',])

    return True
