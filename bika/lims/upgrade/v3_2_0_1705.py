# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
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

    BaseAnalysisRefactoring(portal)

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True

def BaseAnalysisRefactoring(portal):
    """Upgrade steps to be taken after radical Abstract analysis class
    refactoring, also with migration from ReferenceField to UIDReferenceField.

    References that exist before Abstract* analysis refactoring:
    
    AnalysisService
    ===============
        Ref=Instruments               rel=AnalysisServiceInstruments
        Hist=Instrument               rel=AnalysisServiceInstrument
        Ref=Methods                   rel=AnalysisServiceMethods
        Ref=_Method                   rel=AnalysisServiceMethod
        Ref=_Calculation              rel=AnalysisServiceCalculation
        Ref=DeferredCalculation       rel=AnalysisServiceDeferredCalculation
        Ref=Category                  rel=AnalysisServiceAnalysisCategory
        Ref=Department                rel=AnalysisServiceDepartment
        Ref=Preservation              rel=AnalysisServicePreservation
        Ref=Container                 rel=AnalysisServiceContainer
    Analysis
    ========
        Hist=Service                  rel=AnalysisAnalysisService
        Hist=Calculation              rel=AnalysisCalculation
        Ref=Attachment                rel=AnalysisAttachment
        Ref=Instrument                rel=AnalysisInstrument
        Ref=Method                    rel=AnalysisMethod
        Ref=SamplePartition           rel=AnalysisSamplePartition
        Ref=OriginalReflexedAnalysis  rel=OriginalAnalysisReflectedAnalysis
        Ref=ReflexAnalysisOf          rel=AnalysisReflectedAnalysis
    ReferenceAnalysis
    =================
        Hist=Service                  rel=ReferenceAnalysisAnalysisService
        Ref=Attachment                rel=ReferenceAnalysisAttachment
        Ref=Instrument                rel=AnalysisInstrument
        Ref=Method                    rel=AnalysisMethod
    DupplicateAnalysis
    ==================
        Ref=Analysis                  rel=DuplicateAnalysisAnalysis
        Ref=Attachment                rel=DuplicateAnalysisAttachment

    After refactoring, the following references exist

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

    """
    ut = UpgradeUtils(portal)
    at = get_tool('archetype_tool')

    # Attachment indexing in portal_catalog is expensive and not used.
    logger.info('Removing Attachment portal_type from portal_catalog.')
    at.setCatalogsByType('Attachment', [])

    # Miscellaneous index and column updates
    # getServiceDefaultInstrument* were not being used.
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentTitle')
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentUID')
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentURL')
    #
    ut.addColumn('bika_analysis_catalog', 'getNumberOfVerifications')
    # xxx
    ut.addColumn('bika_analysis_catalog', 'getAllowedInstrumentUIDs')
    # getAllowedMethodsAsTuples was used once; no negative impace from replacing
    # it's usage with the actual vocabulary instead of indexing the value.
    ut.delColumn('bika_analysis_catalog', 'getAllowedMethodsAsTuples')
    # getResultOptionsFromService is an alias for getResultOptions
    ut.delColumn('bika_analysis_catalog', 'getResultOptionsFromService')
    ut.addColumn('bika_analysis_catalog', 'getResultOptions')
    # getResultsRangeNoSpecs is an alias for getResultsRange
    ut.delColumn('bika_analysis_catalog', 'getResultsRangeNoSpecs')
    ut.addColumn('bika_analysis_catalog', 'getResultsRange')
    # Analysis Titles are identical to Service titles.
    ut.delIndexAndColumn('bika_analysis_catalog', 'getServiceTitle')
    ut.delIndexAndColumn('bika_setup_catalog', 'getServiceTitle')
    ut.delIndexAndColumn('bika_catalog', 'getServiceTitle')
    # This was not being used at all.
    ut.delIndexAndColumn('bika_catalog', 'getAnalysisCategory')

    # The following relations were used somewhere in the code for
    # backreferences and are refactored to use regular catalog searches on
    # either new or existing indexes (this is definitely going to be cheaper
    # than AT References):
    # - AnalysisServiceMethods
    #   Updated ReflexRuleValidator to use getAvailableMethodsUIDs index on AS.
    ut.addIndex('bika_setup_catalog', 'getAvailableMethodsUIDs', 'KeywordIndex')
    # - AnalysisServiceCalculation
    #   This was only referenced in a needless JSONReadExtender for ASes, which
    #   I removed.
    # - AnalysisAttachment
    # - DuplicateAnalysisAttachment
    #   These were used for cleaning up after attachment deletion But
    #   UIDReferenceField handles this on it's own, so I removed that code.
    #   Also used for generating attachment titles, ridiculous.
    # - AnalysisSamplePartition
    #   This is used quite a lot; I replaced it with a bika_analysis_catalog
    #   index getSamplePartitionUID, and fixed samplepartition.getAnalyses().
    ut.addIndex('bika_analysis_catalog', 'getSamplePartitionUID', 'FieldIndex')
    # - DuplicateAnalysisAnalysis
    #   It was used to remove Duplicates when an Analysis was unassigned from
    #   a worksheet.  So I replaced it with a simple loop.

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
            an.setServiceUID(srv.UID())
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
