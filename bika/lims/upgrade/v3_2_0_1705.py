# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, \
    TRIGGER_USER_ACTION
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.catalog import getCatalogDefinitions, setup_catalogs
from bika.lims.catalog.catalog_utilities import _cleanAndRebuildIfNeeded
from bika.lims.interfaces import IWorksheet
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.upgrade.utils import migrate_to_blob
from plone.api.portal import get_tool

product = 'bika.lims'
version = '3.2.0.1705'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info('Skipping upgrade of {0}: {1} > {2}'.format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info('Upgrading {0}: {1} -> {2}'.format(product, ufrom, version))

    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')

    # Updating catalogs from dependant add-ons (health) if there are changes
    # This block copied from 1704.  Running 1704 is not advised at this point,
    # 1705 should do the job of both.
    logger.info("Updating catalog structures from bika.lims...")
    catalog_definitions = getCatalogDefinitions()
    clean_and_rebuild = setup_catalogs(
        portal, catalog_definitions, force_no_reindex=True)
    logger.info("Catalogs updated (not rebuilt or refreshed)")

    UpdateIndexesAndMetadata(ut)

    # Remove duplicate attachments made by instrument imports
    remove_attachment_duplicates()

    # Migrating ataip.FileField to blob.FileField
    migrateFileFields(portal)

    # Deleting 'Html' field from ARReport objects.
    removeHtmlFromAR(portal)

    RemoveARPriorities(portal)

    BaseAnalysisRefactoring()

    RemoveVersionableTypes()

    FixBrokenActionExpressions()

    # Remove workflow automatic transitions no longer used
    removeWorkflowsAutoTransitions(portal)

    # Fix problem with empty actbox_name in transitions
    fixWorkflowsActBoxName(portal)

    # Set all transitions to be triggered manually
    to_manual_transitions(portal)

    # Remove unused guard expressions from some transitions
    remove_guard_expressions(portal)

    # Replace target states from some transitions
    replace_target_states(portal)

    # Refresh affected catalogs
    _cleanAndRebuildIfNeeded(portal, clean_and_rebuild)
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def FixBrokenActionExpressions():
    """These are fixed in the xml, but I'm fixing them manually here.
    """
    pt = get_tool('portal_types')
    for t in pt:
        actions = t.listActions() if hasattr(t, 'listActions') else []
        for a in actions:
            expr = a.getActionExpression()
            if 'object/aq_parent/absolute_url' in expr:
                # This is from Campbell 2012 and makes problems.
                logger.info("%s.setActioExpression('string:${object_url}')")
                a.setActionExpression('string:${object_url}')


def RemoveVersionableTypes():
    # Remove versionable typesa
    logger.info("Removing versionable types...")
    portal_repository = get_tool('portal_repository')
    non_versionable = ['AnalysisSpec',
                       'ARPriority',
                       'Method',
                       'SamplePoint',
                       'SampleType',
                       'StorageLocation',
                       'WorksheetTemplate', ]
    versionable = list(portal_repository.getVersionableContentTypes())
    vers = [ver for ver in versionable if ver not in non_versionable]
    portal_repository.setVersionableContentTypes(vers)
    logger.info("Versionable types updated: {0}".format(', '.join(vers)))


def UpdateIndexesAndMetadata(ut):

    # Add getDepartmentUIDs to CATALOG_WORKSHEET_LISTING
    ut.addIndexAndColumn(
        CATALOG_WORKSHEET_LISTING, 'getDepartmentUIDs', 'KeywordIndex')

    # Removed ARPriority completely
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getPriority')
    ut.delColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPriority')
    ut.delIndex(CATALOG_WORKSHEET_LISTING, 'getPriority')

    # Add getId column to bika_catalog
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getNumberOfVerifications')
    # Add SearchableText index to analysis requests catalog
    ut.addIndex(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'SearchableText', 'ZCTextIndex')
    # For reference samples
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getParentUID')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getDateSampled')

    # Reindexing bika_catalog_analysisrequest_listing in order to obtain the
    # correct getDateXXXs
    ut.addIndexAndColumn(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'getDateVerified', 'DateIndex')

    # Reindexing bika_analysis_catalog in order to fix busted date indexes
    ut.addIndexAndColumn(
        CATALOG_ANALYSIS_LISTING, 'getDueDate', 'DateIndex')

    # Unify naming and cleanup of Method/Instrument indexes
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getAllowedInstrumentsUIDs')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getAllowedMethodsUIDs')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getAllowedInstrumentUIDs')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getAllowedMethodUIDs')
    ut.addIndex('bika_setup_catalog', 'getAvailableMethodUIDs', 'KeywordIndex')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getAllowedMethodsAsTuples')

    # Added by myself and pau independently
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getNumberOfVerifications')

    # Renamed/refactored
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getResultOptionsFromService')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getResultOptions')

    # Renamed/refactored
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getResultsRangeNoSpecs')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getResultsRange')

    # these were kind of useless
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getServiceDefaultInstrumentTitle')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getServiceDefaultInstrumentUID')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getServiceDefaultInstrumentURL')

    # to replace a backreference for AnalysisSamplePartition
    ut.addIndex(CATALOG_ANALYSIS_LISTING, 'getSamplePartitionUID', 'FieldIndex')

    # replaced by title of analysis, same as service title
    ut.delIndexAndColumn(CATALOG_ANALYSIS_LISTING, 'getServiceTitle')
    ut.delIndexAndColumn('bika_catalog', 'getServiceTitle')
    ut.delIndexAndColumn('bika_setup_catalog', 'getServiceTitle')

    # Required in a few places.  nihadness used getDeparthentTitle as a
    # workaround which is fine, but not for long.
    ut.delIndexAndColumn('bika_setup_catalog', 'getDepartmentUID')

    # factored out
    ut.delIndexAndColumn('bika_catalog', 'getAnalysisCategory')

    # Try to avoid refreshing these two if not required.  We can tell because
    # using a None in a date index used as a sort_on key, causes these objects
    # not to be returned at all.
    query = {'query': [DateTime('1999/01/01 00:00'),
                       DateTime('2024/01/01 23:59')],
             'range': 'min:max'}

    cat = get_tool(CATALOG_ANALYSIS_LISTING)
    brains = cat(portal_type='Analysis', review_state='received')
    filtered = cat(portal_type='Analysis', review_state='received',
                   getDueDate=query)
    if len(filtered) != len(brains) \
            and CATALOG_ANALYSIS_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_LISTING)

    cat = get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    brains = cat(portal_type='AnalysisRequest', review_state='verified')
    filtered = cat(portal_type='AnalysisRequest', review_state='verified',
                   getDateVerified=query)
    if len(filtered) != len(brains) \
            and CATALOG_ANALYSIS_REQUEST_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_REQUEST_LISTING)


def removeHtmlFromAR(portal):
    """
    'Html' StringField has been deleted from ARReport Schema.
    Now removing this attribute from old objects to save some memory.
    """
    uc = getToolByName(portal, 'uid_catalog')
    ar_reps = uc(portal_type='ARReport')
    f_name = 'Html'
    counter = 0
    for ar in ar_reps:
        obj = ar.getObject()
        if hasattr(obj, f_name):
            delattr(obj, f_name)
            counter += 1

    logger.info("'Html' attribute has been removed from %d ARReport objects."
                % counter)


def BaseAnalysisRefactoring():
    """The relationship between AnalysisService and the various types of
    Analysis has been refactored.  The class heirarchy now looks like this:

    - AbstractBaseAnalysis(BaseObject)
        Fields and methods common to to AnalysisService and all types of
        analysis
    - AbstractAnalysis(AbstractBaseAnalysis)
        Fields and methods common to all types of Analysis.
    - AbstractRoutineAnalysis(AbstractBaseAnalysis)
        Fields and methods common to Routine Analyses (Analysis, Duplicate).
    - AnalysisService(AbstractBaseAnalysis)
    - ReferenceAnalysis(AbstractAnalysis)
    - DuplicateAnalysis(AbstractRoutineAnalysis)
    - Analysis(AbstractRoutineAnalysis)
        In the final schema for Analysis objects, the following fields are
        removed to be replaced by accessor methods on the class:
            - Service
            - ClientUID
            - ClientTitle
            - SampleTypeUID
            - SamplePointUID
            - CategoryUID
            - MethodUID
            - InstrumentUID
            - DateReceived
            - DateSampled
            - InstrumentValid

    Many ReferenceFields and HistoryAwareReferenceFields were migrated to
    UIDReferenceField which uses simple StringFields to store the UIDs. After
    refactoring, the following references exist

    BaseAnalysis
    ============
        Instrument                (UIDReferenceField)
        Method                    (UIDReferenceField)
        Calculation               (UIDReferenceField
        Category                  (UIDReferenceField)
        Department                (UIDReferenceField)
    AnalysisService
    ===============
        Preservation              (UIDReferenceField)
        Container                 (UIDReferenceField)
        Instruments               (UIDReferenceField)
        Methods                   (UIDReferenceField)
        DeferredCalculation       -> removed
    Analysis
    ========
        Calculation               (HistoryAwareReferenceField
        Attachment                (UIDReferenceField)
        SamplePartition           (UIDReferenceField)
        OriginalReflexedAnalysis  (UIDReferenceField)
        ReflexAnalysisOf          (UIDReferenceField)
    ReferenceAnalysis
    =================
        Service                   (UIDReferenceField)
        Attachment                (UIDReferenceField)
        Instrument                (UIDReferenceField)
        Method                    (UIDReferenceField)
    DuplicateAnalysis
    =================
        Analysis                  (UIDReferenceField)
        Attachment                (UIDReferenceField)
        Instrument                (UIDReferenceField)

    The following references were also migrated:
    Method           -> Calculation        (MethodCalculation)
    Calculation      -> DependentServices  (CalculationAnalysisService)
    Instrument       -> Method             (InstrumentMethod)
    Instrument       -> Analyses           (InstrumentAnalyses)
    Worksheet        -> WorksheetTemplate  (WorksheetAnalysisTemplate)
    AnalysisSpec     -> SampleType         (AnalysisSpecSampleType)
    AnalysisRequest  -> Priority           (AnalysisRequestPriority)
    AnalysisRequest  -> Contact            (AnalysisRequestContact)
    ARReport         -> AnalysisRequest    (ReportAnalysisRequest)
    Attachment       -> AttachmentType     (AttachmentAttachmentType)
    SamplePartition  -> Analyses           (SamplePartitionAnalysis)
                                            field removed, added accessor method
    """
    at = get_tool('archetype_tool')

    # XXX CAMPBELL PAU I need some help with OriginalAnalysisReflectedAnalysis.

    # I'm using the backreferences below for discovering objects to migrate.
    # This will work, because reference_catalog has not been rebuilt yet.

    # Analysis Services
    # =================
    bsc = get_tool('bika_setup_catalog')
    brains = bsc(portal_type='AnalysisService')
    for srv_brain in brains:
        srv = srv_brain.getObject()
        # migrate service refs first!
        touidref(srv, srv, 'AnalysisServiceAnalysisCategory', 'Category')
        touidref(srv, srv, 'AnalysisServiceDepartment', 'Department')
        touidref(srv, srv, 'AnalysisServiceInstrument', 'Instrument')
        touidref(srv, srv, 'AnalysisServiceMethod', 'Method')

        # Routine Analyses
        # ==================
        ans = srv.getBRefs(relationship='AnalysisAnalysisService')
        if ans:
            logger.info('Migrating schema of %s analyses of type %s' %
                        (len(ans), srv.Title()))
        for an in ans:
            # retain analysis Service in a newly named UIDReferenceField
            an.setAnalysisService(srv.UID())
            # Set service references as analysis reference values
            an.setCategory(srv.getCategory())
            an.setDepartment(srv.getDepartment())
            # Copy field values from service to analysis
            copy_field_values(srv, an)

            # Duplicate Analyses
            # ==================
            dups = an.getBRefs(relationship='DuplicateAnalysisAnalysis')
            if dups:
                logger.info('Migrating schema for %s duplicates on %s' %
                            (len(dups), an))
            for dup in dups:
                # retain analysis Service in a newly named UIDReferenceField
                dup.setAnalysisService(srv)
                # Copy field values from the migrated analysis to the duplicate
                copy_field_values(an, dup)

        # Reference Analyses
        # ==================
        ans = srv.getBRefs(relationship='ReferenceAnalysisAnalysisService')
        if ans:
            logger.info('Migrating schema for %s references on %s' %
                        (len(ans), srv))
        for ran in ans:
            # retain analysis Service in a newly named UIDReferenceField
            ran.setAnalysisService(srv)
            # Copy field values from service into reference analysis
            copy_field_values(srv, ran)

    # Now migrate all AT ReferenceFeld -> UIDReferenceField.

    # The AnalysisInstrument and AnalysisMethod relations are used in fields
    # on routine, reference and/or duplicate analyses.  We are lucky
    # that the fieldnames are Instrument and Method respectively in all
    # applicable objects, so migrate_refs does not need to care about which
    # portal_type is the target.
    migrate_refs('AnalysisInstrument', 'Instrument')
    migrate_refs('AnalysisMethod', 'Method')

    # The remaining reference relations are named correctly based on source
    # and destination type:
    migrate_refs('AnalysisAttachment', 'Attachment')
    migrate_refs('AnalysisSamplePartition', 'SamplePartition')
    migrate_refs('OriginalAnalysisReflectedAnalysis',
                 'OriginalReflexedAnalysis')
    migrate_refs('AnalysisReflectedAnalysis', 'ReflexAnalysisOf')
    migrate_refs('DuplicateAnalysisAnalysis', 'Analysis')
    migrate_refs('DuplicateAnalysisAttachment', 'Attachment')
    migrate_refs('ReferenceAnalysisAnalysisService', 'Service')
    migrate_refs('ReferenceAnalysisAttachment', 'Attachment')
    migrate_refs('AnalysisServiceInstrument', 'Instrument')
    migrate_refs('AnalysisServiceInstruments', 'Instruments')
    migrate_refs('AnalysisServiceMethod', 'Method')
    migrate_refs('AnalysisServiceMethods', 'Methods')
    migrate_refs('AnalysisServiceCalculation', 'Calculation')
    migrate_refs('AnalysisServiceAnalysisCategory', 'Category')
    migrate_refs('AnalysisServiceDepartment', 'Department')
    migrate_refs('AnalysisServicePreservation', 'Preservation')
    migrate_refs('AnalysisServiceContainer', 'Container')
    migrate_refs('MethodCalculation', 'Calculation')
    migrate_refs('CalculationAnalysisService', 'DependentServices')
    migrate_refs('InstrumentMethod', 'Method')
    # InstrumentAnalyses gets deleted.  Instruments can use the index
    # 'getInstrumentUID' in bika_analysis_catalog for the same purposes.
    # migrate_refs('InstrumentAnalyses', 'Analyses')
    migrate_refs('WorksheetAnalysisTemplate', 'WorksheetTemplate')
    migrate_refs('AnalysisSpecSampleType', 'SampleType')
    migrate_refs('AnalysisRequestContact', 'Contact')
    migrate_refs('ReportAnalysisRequest', 'AnalysisRequest')
    migrate_refs('AttachmentAttachmentType', 'AttachmentType')

    refs_removed = 0
    for rel in ['AnalysisInstrument',
                'AnalysisMethod',
                'AnalysisAttachment',
                'AnalysisSamplePartition',
                'OriginalAnalysisReflectedAnalysis',
                'AnalysisReflectedAnalysis',
                'AnalysisAnalysisService',
                'AnalysisAnalysisPartition',
                'ReferenceAnalysisAnalysisService',
                'ReferenceAnalysisAttachment',
                'AnalysisInstrument',
                'AnalysisMethod',
                'AnalysisServiceAnalysisCategory',
                'AnalysisServiceDepartment',
                'AnalysisServiceInstruments',
                'AnalysisServiceInstruments',
                'AnalysisServiceInstrument',
                'AnalysisServiceMethods',
                'AnalysisServiceMethod',
                'AnalysisServiceCalculation',
                'AnalysisServiceDeferredCalculation',
                'AnalysisServicePreservation',
                'AnalysisServiceContainer',
                'DuplicateAnalysisAnalysis',
                'DuplicateAnalysisAttachment',
                'AnalysisInstrument',
                'MethodCalculation',
                'CalculationAnalysisService',
                'InstrumentMethod',
                'InstrumentAnalyses',
                'WorksheetAnalysisTemplate',
                'AnalysisSpecSampleType',
                # AnalysisRequestPriority: field is removed completely.
                'AnalysisRequestPriority',
                'AnalysisRequestContact',
                'ReportAnalysisRequest',
                'AttachmentAttachmentType',
                # SamplePartitionAnalysis: field is removed completely.
                'SamplePartitionAnalysis',
                ]:
        refs_removed += del_at_refs(rel)
    if refs_removed:
        logger.info("Total reference objects removed: %s" % refs_removed)


def RemoveARPriorities(portal):
    # Throw out persistent broken bika_arpriorities.
    logger.info('Removing bika_setup.bika_arpriorities')
    bs = get_tool('bika_setup')
    pc = get_tool('portal_catalog')
    cpl = get_tool('portal_controlpanel')

    # This lets ARPriorities load with BaseObject code since
    # bika_arpriorities.py has been eradicated.
    # stub('bika.lims.controlpanel.bika_arpriorities', 'ARPriorities',
    #      BaseContent)

    if 'bika_arpriorities' in portal.bika_setup:
        brain = pc(portal_type='ARPriorities')[0]
        # manually unindex object  --  pc.uncatalog_object(brain.UID())
        indexes = pc.Indexes.keys()
        rid = brain.getRID()
        for name in indexes:
            x = pc.Indexes[name]
            if hasattr(x, 'unindex_object'):
                x.unindex_object(rid)
        # Then remove as normal
        bs.manage_delObjects(['bika_arpriorities'])
        cpl.unregisterConfiglet('bika_arpriorities')


def touidref(src, dst, src_relation, fieldname):
    """Convert an archetypes reference in src/src_relation to a UIDReference
    in dst/fieldname.
    """
    field = dst.getField(fieldname)
    refs = src.getRefs(relationship=src_relation)
    if len(refs) == 1:
        value = get_uid(refs[0])
    elif len(refs) > 1:
        value = filter(lambda x: x, [get_uid(ref) for ref in refs])
    else:
        value = field.get(src)
    if not value:
        value = ''
    if not field:
        raise Exception('Cannot find field %s/%s' % (fieldname, src))
    if field.required and not value:
        logger.error('Required %s field %s/%s has no value' % (
            src.portal_type, src, fieldname))
    field.set(src, value)


def migrate_refs(rel, fieldname, pgthreshold=100):
    rc = get_tool(REFERENCE_CATALOG)
    uc = get_tool('uid_catalog')
    refs = rc(relationship=rel)
    if refs:
        logger.info('Migrating %s references of %s' % (len(refs), rel))
    for i, ref in enumerate(refs):
        obj = uc(UID=ref[1])[0].getObject()
        if i and not divmod(i, pgthreshold)[1]:
            logger.info("%s/%s %s/%s" % (i, len(refs), obj, rel))
        touidref(obj, obj, rel, fieldname)


def del_at_refs(rel):
    # Remove this relation from at_references
    rc = get_tool(REFERENCE_CATALOG)
    refs = rc(relationship=rel)
    removed = 0
    size = 0
    if refs:
        logger.info("Found %s refs for %s" % (len(refs), rel))
        ref_dict = {ref[0]: ref.getObject() for ref in refs}
        for ref_id, ref_obj in ref_dict.items():
            removed += 1
            size += 1
            ref_obj.aq_parent.manage_delObjects([ref_id])
    if removed:
        logger.info("Performed %s deletions" % removed)
    return removed


def copy_field_values(src, dst):
    # These fields are not copied between objects.
    IGNORE_FIELDNAMES = ['UID', 'id']
    IGNORE_FIELDTYPES = ['reference']

    src_schema = src.Schema()
    dst_schema = dst.Schema()

    for field in src_schema.fields():
        fieldname = field.getName()
        if fieldname in IGNORE_FIELDNAMES \
                or field.type in IGNORE_FIELDTYPES \
                or fieldname not in dst_schema:
            continue
        value = field.get(src)
        if value:
            dst_schema[fieldname].set(dst, value)


def get_uid(value):
    """Takes a brain or object and returns a valid UID.
    In this case, the object may come from portal_archivist, so we will
    need to do a catalog query to get the UID of the current version
    """
    if not value:
        return ''
    # Is value a brain?
    if ICatalogBrain.providedBy(value):
        value = value.getObject()
    # validate UID
    uid = value.UID()
    uc = get_tool('uid_catalog')
    if uc(UID=uid):
        # The object is valid
        return uid
    # Otherwise the object is an old version
    brains = uc(portal_type=value.portal_type, Title=value.Title())
    if not brains:
        # Cannot find UID
        raise RuntimeError('The UID for %s/%s cannot be discovered in the '
                           'uid_catalog or in the portal_archivist '
                           'history!' %
                           (value.portal_type, value.Title()))
    if len(brains) > 1:
        # Found multiple objects, this is a failure
        raise RuntimeError(
            'Searching for %s/%s returned multiple objects.' %
            (value.portal_type, value.Title()))
    return brains[0].UID


def migrateFileFields(portal):
    """
    This function walks over all attachment types and migrates their FileField
    fields.
    """
    portal_types = [
        "Attachment",
        "ARImport",
        "Instrument",
        "InstrumentCertification",
        "Method",
        "Multifile",
        "Report",
        "ARReport",
        "SamplePoint"]

    for portal_type in portal_types:
        # Do the migration
        migrate_to_blob(
            portal,
            portal_type=portal_type,
            remove_old_value=True)


def remove_attachment_duplicates():
    """Visit every worksheet attachment, and remove duplicates.
    The duplicates are filtered by filename, but that's okay because the
    instrument import routine used filenames when it made them.
    """
    pc = get_tool('portal_catalog')

    # get all worksheets.
    brains = pc(portal_type='Attachment')

    # primaries contains non-duplicate attachments.  key is wsID:fn.
    # key used for filtering duplicates; same filename permitted on
    # separate worksheets.
    primaries = {}  # key -> primary_attachment
    dup_ans = {}  # key -> [dup_att,dup_att...]
    dup_count = 0

    for brain in brains:
        att = brain.getObject()
        if not IWorksheet.providedBy(att.aq_parent):
            continue
        ws = att.aq_parent
        ws_id = ws.getId()
        filename = att.getAttachmentFile().filename
        if not filename:
            continue
        key = "%s:%s" % (ws_id, filename)
        if key not in primaries:
            # first instance of this file on this worksheet.  Not a duplicate.
            primaries[key] = att
            continue
        # we are a duplicate.
        if key not in dup_ans:
            dup_ans[key] = []
        dup_ans[key].append(att)
        dup_count += 1

    if dup_ans:
        logger.info("Found {} duplicates of {} attachments".format(
            dup_count, len(primaries)))

    # Now.
    for key, dups in dup_ans.items():
        ws_id, filename = key.split(':')
        logger.info("Removing {} duplicates of {} from {}".format(
            len(dups), filename, ws_id))
        for dup in dups:
            ans = dup.getBackReferences()
            for an in ans:
                # remove the dup from analysis.Attachment field if it's there
                an_atts = [a for a in an.getAttachment()
                           if a.UID() != dup.UID()]
                an.setAttachment(an_atts)
                # manually delete references to this attachment in the Analysis
                refs = an.at_references.objectValues()
                for ref in refs:
                    if ref.targetUID == dup.UID():
                        an.at_references.manage_delObjects(ref.id)
            # force this object out of the catalogs
            path_uid = '/'.join(dup.getPhysicalPath())
            pc.uncatalog_object(path_uid)
            # Empty the file field valust just to be sure
            dup.getField('AttachmentFile').unset(dup)
            # Delete the attachment
            dup.aq_parent.manage_delObjects(dup.getId())


def fixWorkflowsActBoxName(portal):
    """Walkthrough all the transitions from all workflows and sets actbox_name
    if empty. Although being valid, those transitions without actbox_name will
    never be returned by workflowtool.getTransitionsFor, so bika's workflow
    machinery fails"""
    logger.info('Fixing transition actbox_names...')
    wtool = getToolByName(portal, 'portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        for transid in transitions.objectIds():
            transition = transitions[transid]
            if not transition.actbox_name:
                transition.actbox_name = transition.id
                logger.info('Transition actbox_name fixed: {0}'.format(transid))


def removeWorkflowsAutoTransitions(portal):
    """Remove transitions that are triggered automatically, cause since this
    version are all managed manually: auto_preservation_required and
    auto_no_preservation_required
    """
    logger.info('Removing automatic transitions no longer used...')
    toremove = [{'id': 'auto_preservation_required',
                 'replacement': 'to_be_preserved'},
                {'id': 'auto_no_preservation_required',
                 'replacement': 'sample_due'}, ]
    wtool = getToolByName(portal, 'portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        # Walkthrough states, remove the transitions from there and be sure the
        # replacement (manual transition) is on place
        states = workflow.states
        for stateid in states.objectIds():
            state = states[stateid]
            strans = list(state.transitions)
            for remove in toremove:
                if remove['id'] in strans:
                    msg = 'Dettaching transition {0} from state {1} in {2}' \
                        .format(remove['id'], stateid, wfid)
                    logger.info(msg)
                    strans.remove(remove['id'])
                    if remove['replacement'] not in strans:
                        msg = 'Attaching transition {0} to state {1} from {2}' \
                            .format(remove['replacement'], stateid, wfid)
                        logger.info(msg)
                        strans.append(remove['replacement'])
                    state.transitions = tuple(strans)

        # Now, remove the transitions itself
        transitions = workflow.transitions
        transids = transitions.objectIds()
        for remove in toremove:
            if remove['id'] in transids:
                logger.info('Removing transition {0} from {1}'.format(
                    remove['id'], wfid))
                workflow.transitions.deleteTransitions([remove['id']])


def to_manual_transitions(portal):
    """Remove transitions that are triggered automatically, cause since this
    version are all managed manually: auto_preservation_required and
    auto_no_preservation_required
    """
    logger.info('Setting auto transitions to manual...')
    wtool = getToolByName(portal, 'portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        for transid in transitions.objectIds():
            transition = transitions[transid]
            if transition.trigger_type == TRIGGER_AUTOMATIC:
                transition.trigger_type = TRIGGER_USER_ACTION
                logger.info("Transition '{0}' from workflow '{1}' set to manual"
                            .format(wfid, transid))


def remove_guard_expressions(portal):
    """Remove guard expressions from some workflow statuses
    """
    logger.info('Removing unused guard expressions...')
    toremove = ['bika_worksheetanalysis_workflow.assign',
                'bika_worksheetanalysis_workflow.unassign']
    wtool = get_tool('portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        for transid in transitions.objectIds():
            for torem in toremove:
                tokens = torem.split('.')
                if tokens[0] == wfid and tokens[1] == transid:
                    transition = transitions[transid]
                    transition.guard = None
                    logger.info("Guard from transition '{0}.{1}' reset to None"
                                .format(wfid, transid))


def replace_target_states(portal):
    """Replace target states from some worklow statuses
    """
    logger.info('Replacing Target states for some workflow statuses...')
    tochange = [
            {'wfid': 'bika_duplicateanalysis_workflow',
             'trid': 'submit',
             'target': 'to_be_verified'},

            {'wfid': 'bika_referenceanalysis_workflow',
             'trid': 'submit',
             'target': 'to_be_verified'},

            {'wfid': 'bika_worksheet_workflow',
             'trid': 'submit',
             'target': 'to_be_verified'}
             ]
    wtool = get_tool('portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        for transid in transitions.objectIds():
            for item in tochange:
                itwfid = item.get('wfid', '')
                ittrid = item.get('trid', '')
                ittarg = item.get('target', '')
                if itwfid == wfid and ittrid == transid and ittarg:
                    transition = transitions[transid]
                    oldstate = transition.new_state_id
                    transition.new_state_id = ittarg
                    logger.info(
                        "Replacing target state '{0}' from '{1}.{2}' to {3}"
                        .format(oldstate, wfid, transid, ittarg)
                    )
