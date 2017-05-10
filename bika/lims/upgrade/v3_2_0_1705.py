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

    logger.info('{0} upgraded to version {1}'.format(product, version))
    return True


def BaseAnalysisRefactoring(portal):
    ut = UpgradeUtils(portal)
    """Upgrade steps to be taken after radical BaseAnalysis refactoring
    Includes migration of ReferenceField values to the new UIDReferenceField.

    Old-style references before BaseAnalysis refactoring:
    
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

    After refactoring, the following references exist

    BaseAnalysis
    ============
        Instrument                    (UIDReferenceField)
        Method                        (UIDReferenceField)
        Calculation                   (HistoryAwareReferenceField
        Category                      (UIDReferenceField)
        Department                    (UIDReferenceField)
    AnalysisService
    ===============
        Preservation                  (UIDReferenceField)
        Container                     (UIDReferenceField)
        Instruments                   (UIDReferenceField)
        Methods                       (UIDReferenceField)
    Analysis
    ========
        Attachment                    (UIDReferenceField)
        SamplePartition               (UIDReferenceField)
        OriginalReflexedAnalysis      (UIDReferenceField)
        ReflexAnalysisOf              (UIDReferenceField)
    """

    # Miscellaneous fixes
    logger.info('Removing bika_analysis_catalog/getServiceDefaultInstrument*')
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentTitle')
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentUID')
    ut.delColumn('bika_analysis_catalog', 'getServiceDefaultInstrumentURL')

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
        analyses = srv.getBRefs(relationship='AnalysisAnalysisService')
        logger.info('Migrating Analyses schema for %s analyses on %s'
                    % (len(analyses), srv.Title()))
        for an in analyses:
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
