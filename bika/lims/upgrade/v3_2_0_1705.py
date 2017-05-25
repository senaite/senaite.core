# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.upgrade import stub, upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
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

    UpdateIndexesAndMetadata(ut)

    BaseAnalysisRefactoring()

    RemoveARPriorities(portal)

    RemoveVersionableTypes()

    # Refresh affected catalogs
    ut.refreshCatalogs()

    # logger.info("Rebuilding reference_catalog")
    # rc = get_tool(REFERENCE_CATALOG)
    # rc.manage_rebuildCatalog()

    # I want to be sure that bika_arpriorities are really removed.
    bsc = get_tool('bika_setup_catalog')
    bsc.clearFindAndRebuild()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def RemoveVersionableTypes():
    # Remove versionable types
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
    if CATALOG_ANALYSIS_REQUEST_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_REQUEST_LISTING)

    # Reindexing bika_analysis_catalog in order to fix busted date indexes
    ut.addIndexAndColumn(
        CATALOG_ANALYSIS_LISTING, 'getDueDate', 'DateIndex')
    if CATALOG_ANALYSIS_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_LISTING)

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

    # factored out
    ut.delIndexAndColumn('bika_catalog', 'getAnalysisCategory')

    # Removed ARPriority completely
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getPriority')
    ut.delColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPriority')
    ut.delIndex(CATALOG_WORKSHEET_LISTING, 'getPriority')


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

    # Attachment indexing in portal_catalog is expensive and not used.
    logger.info('Removing Attachment portal_type from portal_catalog.')
    at.setCatalogsByType('Attachment', [])

    # XXX CAMPBELL PAU I need some help with OriginalAnalysisReflectedAnalysis.

    # I'm using the backreferences below for discovering objects to migrate.
    # This will work, because reference_catalog has not been rebuilt yet.

    # Analysis Services
    # =================
    bsc = get_tool('bika_setup_catalog')
    brains = bsc(portal_type='AnalysisService')
    for srv_brain in brains:
        srv = srv_brain.getObject()

        # Routine Analyses
        # ==================
        ans = srv.getBRefs(relationship='AnalysisAnalysisService')
        if ans:
            logger.info('Migrating schema of %s analyses of type %s' %
                        (len(ans), srv.Title()))
        for an in ans:
            # retain analysis Service in a newly named UIDReferenceField
            an.setAnalysisService(srv)
            # Set service references as analysis reference values
            an.setCategory(srv.getCategory())
            an.setDepartment(srv.getDepartment())
            # Copy field values from service to analysis
            copy_field_values(srv, an)

            # Duplidate Analyses
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
    migrate_refs('InstrumentAnalyses', 'Analyses')
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
    # Throw out ARPriorities.  The types have been removed, but the objects
    # themselves remain as persistent broken objects, and at_references.
    logger.info('Removing bika_setup.bika_arpriorities')
    # Replace PersistentBroken ARPriority things with BaseContent
    stub('bika.lims.content.arpriority.ARPriority', 'ARPriority', BaseContent)
    stub('bika.lims.controlpanel.bika_arpriorities', 'ARPriorities',
         BaseContent)

    if 'bika_arpriorities' in portal.bika_setup:
        portal.bika_setup.manage_delObjects(['bika_arpriorities'])
    logger.info('Reindexing bika_setup object')
    portal.bika_setup.reindexObject()


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
        raise Exception(
            'Required field %s/%s has no value' % (src, fieldname))
    field.set(src, value)


def migrate_refs(rel, fieldname):
    rc = get_tool(REFERENCE_CATALOG)
    uc = get_tool('uid_catalog')
    refs = rc(relationship=rel)
    if refs:
        logger.info('Migrating %s references of %s' % (len(refs), rel))
    for i, ref in enumerate(refs):
        obj = uc(UID=ref[1])[0].getObject()
        if i and not divmod(i, 100)[1]:
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
