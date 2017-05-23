# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING, \
    CATALOG_WORKSHEET_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.upgrade import upgradestep
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

    UpdateIndexesAndMetadata(portal, ut)

    BaseAnalysisRefactoring(portal)

    # Throw out ARPriorities (the types have been removed, but the objects
    # themselves remain as p[ersistent broken)
    portal.bika_setup.manage_delObjects(['bika_arpriorities'])

    # Refresh affected catalogs
    ut.refreshCatalogs()

    # Clear and rebuild the reference catalog
    logger.info("Rebuilding reference_catalog")
    rc = get_tool(REFERENCE_CATALOG)
    rc.manage_rebuildCatalog()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def UpdateIndexesAndMetadata(portal, ut):

    # Add SearchableText index to analysis requests catalog
    ut.addIndex(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'SearchableText', 'ZCTextIndex')

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


def BaseAnalysisRefactoring(portal):
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

    Method -> Calculation (UIDReferenceField)
    Calculation -> DependentServices (UIDReferenceField)
    Instrument -> Method (UIDReferenceField)
    Worksheet -> WorksheetTemplate (UIDReferenceField)
    AnalysisRequest -> Priority (UIDReferenceField)
    AnalysisSpec -> SampleType (UIDReferenceField)
    """
    at = get_tool('archetype_tool')

    # Attachment indexing in portal_catalog is expensive and not used.
    logger.info('Removing Attachment portal_type from portal_catalog.')
    at.setCatalogsByType('Attachment', [])

    # - XXX CAMPBELL OriginalAnalysisReflectedAnalysis

    # I'm using the backreferences below for discovering objects to migrate.
    # This will work, because reference_catalog has not been rebuilt yet.

    # Analysis Services ========================================================
    bsc = get_tool('bika_setup_catalog')
    brains = bsc(portal_type='AnalysisService')
    for brain in brains:
        srv = brain.getObject()
        logger.info('Migrating Analysis Service schema for %s' % srv.Title())
        touidref(srv, srv, 'AnalysisServiceInstrument', 'Instrument')
        touidref(srv, srv, 'AnalysisServiceInstruments', 'Instruments')
        touidref(srv, srv, 'AnalysisServiceMethod', 'Method')
        touidref(srv, srv, 'AnalysisServiceMethods', 'Methods')
        touidref(srv, srv, 'AnalysisServiceCalculation', 'Calculation')
        touidref(srv, srv, 'AnalysisServiceAnalysisCategory', 'Category')
        touidref(srv, srv, 'AnalysisServiceDepartment', 'Department')
        touidref(srv, srv, 'AnalysisServicePreservation', 'Preservation')
        touidref(srv, srv, 'AnalysisServiceContainer', 'Container')

        # Analyses =============================================================
        ans = srv.getBRefs(relationship='AnalysisAnalysisService')
        if ans:
            logger.info('Migrating %s analyses on %s' % (len(ans), srv))
        for an in ans:
            # retain analysis.ServiceUID
            an.setAnalysisService(srv)
            # Migrate refs to UIDReferenceField
            touidref(an, an, 'AnalysisInstrument', 'Instrument')
            touidref(an, an, 'AnalysisMethod', 'Method')
            an.setCategory(srv.getCategory())
            an.setDepartment(srv.getDepartment())
            touidref(an, an, 'AnalysisAttachment', 'Attachment')
            touidref(an, an, 'AnalysisSamplePartition', 'SamplePartition')
            touidref(an, an, 'OriginalAnalysisReflectedAnalysis',
                     'OriginalReflexedAnalysis')
            touidref(an, an, 'AnalysisReflectedAnalysis', 'ReflexAnalysisOf')

            # Duplicates of this analysis:
            # ==================================================================
            dups = an.getBRefs(relationship='DuplicateAnalysisAnalysis')
            if dups:
                logger.info('%s has %s duplicates' % (an, len(dups)))
            for dup in dups:
                dup.setServiceUID(srv.UID())
                touidref(dup, dup, 'DuplicateAnalysisAnalysis', 'Analysis')
                touidref(dup, dup, 'DuplicateAnalysisAttachment', 'Attachment')
                touidref(dup, dup, 'AnalysisInstrument', 'Instrument')
                # Then scoop the rest of the fields out of service
                copy_field_values(srv, dup)
        # Reference Analyses
        # =============================================================
        ans = srv.getBRefs(relationship='ReferenceAnalysisAnalysisService')
        if ans:
            logger.info('Migrating %s references on %s' % (len(ans), srv))
        for an in ans:
            # retain analysis.ServiceUID
            an.setServiceUID(srv.UID())
            touidref(an, an, 'ReferenceAnalysisAnalysisService', 'Service')
            touidref(an, an, 'ReferenceAnalysisAttachment', 'Attachment')
            touidref(an, an, 'AnalysisInstrument', 'Instrument')
            touidref(an, an, 'AnalysisMethod', 'Method')
            # Then scoop the rest of the fields out of service
            copy_field_values(srv, an)

    # Removing some more HistoryAwareReferenceFields
    brains = bsc(portal_type='Method')
    for brain in brains:
        method = brain.getObject()
        touidref(method, method, 'MethodCalculation', 'Calculation')

    brains = bsc(portal_type='Calculation')
    for brain in brains:
        calc = brain.getObject()
        touidref(calc, calc, 'CalculationAnalysisService', 'DependentServices')

    brains = bsc(portal_type='Instrument')
    for brain in brains:
        instrument = brain.getObject()
        touidref(instrument, instrument, 'InstrumentMethod', 'Method')

    bc = get_tool('bika_catalog')
    brains = bc(portal_type='Worksheet')
    for brain in brains:
        ws = brain.getObject()
        touidref(ws, ws, 'WorksheetAnalysisTemplate', 'WorksheetTemplate')

    brains = bc(portal_type='AnalysisSpec')
    for brain in brains:
        spec = brain.getObject()
        touidref(spec, spec, 'AnalysisSpecSampleType', 'SampleType')

def touidref(src, dst, src_relation, fieldname):
    """Convert an archetypes reference in src/src_relation to a UIDReference
    in dst/fieldname.
    """
    refs = src.getRefs(relationship=src_relation)
    if len(refs) == 1:
        value = get_uid(refs[0])
    elif len(refs) > 1:
        value = filter(lambda x: x, [get_uid(ref) for ref in refs])
    else:
        value = ''
    field = dst.getField(fieldname)
    if not field:
        raise Exception('Cannot find field %s/%s' % (fieldname, src))
    if field.required and not value:
        raise Exception('Required field %s/%s has no value' % (src, fieldname))
    field.set(src, value)


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
                           'uid_catalog or in the portal_archivist history!' %
                           (value.portal_type, value.Title()))
    if len(brains) > 1:
        # Found multiple objects, this is a failure
        raise RuntimeError('Searching for %s/%s returned multiple objects.' %
                           (value.portal_type, value.Title()))
    return brains[0].UID
