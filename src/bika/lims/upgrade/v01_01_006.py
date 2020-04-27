# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils, migrate_to_blob
from bika.lims.utils import tmpID
from plone.api.portal import get_tool

version = '1.1.6'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Convert ReferenceField's values into UIDReferenceFields.
    UpgradeReferenceFields()

    # Calculations not triggered in manage results view
    # https://github.com/senaite/bika.lims/issues/355
    # Since we've already migrated the ReferenceField DependentServices from
    # Calculation (with relation name 'CalculationAnalysisService' above, this
    # wouldn't be strictly necessary, but who knows... maybe we've lost the
    # at_references too, so just do it.
    fix_broken_calculations()

    # Backward compatibility with < 1.0.0
    RemoveARPriorities(portal)
    RemoveVersionableTypes()
    handle_AS_wo_category(portal)
    migrateFileFields(portal)

    # Indexes and colums were changed as per
    # https://github.com/senaite/bika.lims/pull/353
    ut.delIndex(CATALOG_ANALYSIS_LISTING, 'getAnalysisRequestUID')
    ut.addIndex(CATALOG_ANALYSIS_LISTING, 'getRequestUID', 'FieldIndex')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getAnalysisRequestURL')
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getAnalysisRequestTitle')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getRequestURL')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getRequestTitle')
    ut.reindexIndex(CATALOG_ANALYSIS_LISTING, 'getPrioritySortkey')
    ut.refreshCatalogs()

    return True


def fix_broken_calculations():
    """Walks-through calculations associated to undergoing analyses and
    resets the value for DependentServices field"""

    logger.info("Fixing broken calculations (re-assignment of dependents)...")

    # Fetch only the subset of analyses that are undergoing.
    # Analyses that have been verified or published cannot be updated, so there
    # is no sense to check their calculations
    review_states = [
         'attachment_due',
         'not_requested',
         'rejected',
         'retracted',
         'sample_due',
         'sample_prep',
         'sample_received',
         'sample_received',
         'sample_registered',
         'sampled',
         'to_be_preserved',
         'to_be_sampled',
    ]
    uc = api.get_tool('uid_catalog')
    catalog = get_tool(CATALOG_ANALYSIS_LISTING)
    brains = catalog(portal_type='Analysis', review_state=review_states)
    for brain in brains:
        analysis = brain.getObject()
        calculation = analysis.getCalculation()
        if not calculation:
            continue

        dependents = calculation.getDependentServices()
        # We don't want eventualities such as [None,]
        dependents = filter(None, dependents)
        if not dependents:
            # Assign the formula again to the calculation. Note the function
            # setFormula inferes the dependent services (and stores them) by
            # inspecting the keywords set in the formula itself.
            # So, instead of doing this job here, we just let setFormula to work
            # for us.
            formula = calculation.getFormula()
            calculation.setFormula(formula)
            deps = calculation.getDependentServices()
            if not deps:
                # Ok, this calculation does not depend on the result of other
                # analyses, so we can omit this one, he is already ok
                continue

            deps = [dep.getKeyword() for dep in deps]
            deps = ', '.join(deps)
            arid = analysis.getRequestID()
            logger.info("Dependents for {}.{}.{}: {}".format(arid,
                                                          analysis.getKeyword(),
                                                          calculation.Title(),
                                                          deps))

            # Set the calculation to the analysis again (field Calculation is an
            # HistoryAwareReferenceField in Analyses that inherits from
            # AbstractRoutineAnalysis
            analysis.setCalculation(calculation)

            # Check if all is ok
            an_deps =  analysis.getCalculation().getDependentServices()
            if not an_deps:
                # Maybe the version of the calculation is an old one. If so, we
                # need to use the last version, cause HistoryAwareReferenceField
                # will always point to the version assigned to the calculation
                # that was associated to the analysis.
                uid = calculation.UID()
                target_version = analysis.reference_versions[uid]
                last_calc = uc(UID=uid)
                if not last_calc:
                    # This should not happen
                    logger.warn("No calculation found for %s" % uid)
                    continue
                last_calc = last_calc[0].getObject()
                if last_calc.version_id != target_version:
                    # Ok, this is another version. We have no choice here... we
                    # need to assign the latest version...
                    analysis.reference_versions[uid]=last_calc.version_id

            # Just in case
            analysis.reindexObject()


refs_to_remove = []
objs_to_reindex = []

def UpgradeReferenceFields():
    """Convert all ReferenceField's values into UIDReferenceFields.

    These are not touched: HistoryAware to be removed:
      - Analysis.Calculation: HistoryAwareReferenceField (rel=
      AnalysisCalculation)
      - DuplicateAnalysis.Calculation: HistoryAwareReferenceField (rel=
      DuplicateAnalysisCalculation)
      - RejectAnalysis.Calculation: HistoryAwareReferenceField (rel=
      RejectAnalysisCalculation)

    These are not touched: They are deprecated and will be removed:
      - AnalysisRequest.Profile: ReferenceField (rel=AnalysisRequestProfile)
      - LabContact.Department ReferenceField (rel=LabContactDepartment)

    The remaining fields are listed below.
    """

    # Change these carefully
    # they were made slowly with love
    # still they may be wrong.

    for portal_type, fields in [
        # portal_type
        ['ARReport', [
            ('AnalysisRequest', 'ARReportAnalysisRequest')
        ]],

        ['Analysis', [
            # AbstractBaseAnalysis
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            # AbstractAnalysis
            ('AnalysisService', 'AnalysisAnalysisService'),
            ('Attachment', 'AnalysisAttachment'),
            # AbstractRoutineAnalysis
            ('OriginalReflexedAnalysis', 'AnalysisOriginalReflexedAnalysis'),
            ('ReflexAnalysisOf', 'AnalysisReflexAnalysisOf'),
            ('SamplePartition', 'AnalysisSamplePartition')
        ]],

        ['ReferenceAnalysis', [
            # AbstractBaseAnalysis
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            # AbstractAnalysis
            ('AnalysisService', 'AnalysisAnalysisService'),
            ('Attachment', 'AnalysisAttachment'),
        ]],

        ['DuplicateAnalysis', [
            # AbstractBaseAnalysis
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            # AbstractAnalysis
            ('AnalysisService', 'AnalysisAnalysisService'),
            ('Attachment', 'AnalysisAttachment'),
            # AbstractRoutineAnalysis
            ('OriginalReflexedAnalysis', 'AnalysisOriginalReflexedAnalysis'),
            ('ReflexAnalysisOf', 'AnalysisReflexAnalysisOf'),
            ('SamplePartition', 'AnalysisSamplePartition'),
            # DuplicateAnalysis
            ('Analysis', 'DuplicateAnalysisAnalysis'),
        ]],

        ['AnalysisService', [
            # AbstractBaseAnalysis
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            # AnalysisService
            ('Calculation', 'AnalysisServiceCalculation'),
            ('Container', 'AnalysisServiceContainer'),
            ('Instruments', 'AnalysisServiceInstruments'),
            ('Methods', 'AnalysisServiceMethods'),
            ('Preservation', 'AnalysisServicePreservation'),

            # Backward compatibility with < 1.0.0
            ('Calculation', 'AnalysisServiceCalculation'),
            ('Category',    'AnalysisServiceAnalysisCategory'),
            ('Department',  'AnalysisServiceDepartment'),
            ('Instrument',  'AnalysisServiceInstrument'),
            ('Instruments', 'AnalysisServiceInstruments'),
            ('Method',      'AnalysisServiceMethod'),
            ('Methods',     'AnalysisServiceMethods'),
            ('Preservation','AnalysisServicePreservation'),
            ('Container',   'AnalysisServiceContainer'),
        ]],

        ['AnalysisRequest', [
            ('Contact', 'AnalysisRequestContact'),
            ('Sample', 'AnalysisRequestSample'),
        ]],

        ['AnalysisSpec', [
            ('SampleType', 'AnalysisSpecSampleType')
        ]],

        ['Calculation', [
            ('DependentServices', 'CalculationDependentServices'),
            ('DependentServices', 'CalculationAnalysisService'),
        ]],

        ['Instrument', [
            ('Analyses', 'InstrumentAnalyses'),
            ('Method', 'InstrumentMethod'),
        ]],

        ['Method', [
            ('Calculation', 'MethodCalculation'),
        ]],

        ['SamplePartition', [
            ('Analyses', 'SamplePartitionAnalysis'),
        ]],

        ['Worksheet', [
            ('WorksheetTemplate', 'WorksheetAnalysisTemplate')
        ]]]:

        logger.info("Migrating references for portal_type: %s" % portal_type)

        for fieldname, relation in fields:
            if is_UIDReferenceField(portal_type, fieldname):
                migrate_refs(portal_type, relation, fieldname)

        # remove at refs
        for remove in refs_to_remove:
            del_at_refs(remove)

        # reindex objects
        for obj in objs_to_reindex:
            obj.reindexObject()


def is_UIDReferenceField(portal_type, fieldname):
    uc = get_tool('uid_catalog')
    brains = uc(portal_type=portal_type)
    if not brains:
        return False
    field = brains[0].getObject().getField(fieldname)
    if not field:
        logger.exception("Field not found: %s/%s" % (portal_type, fieldname))
        return None
    if field.type == 'uidreference':
        return True


def migrate_refs(portal_type, relation, fieldname, pgthreshold=100):
    rc = get_tool(REFERENCE_CATALOG)
    uc = get_tool('uid_catalog')
    refs = rc(relationship=relation)
    # Be sure there are no Nones
    refs = filter(None, refs)
    if not refs:
        return

    logger.info('Migrating %s references of %s' % (len(refs), relation))
    for i, ref in enumerate(refs):
        obj = uc(UID=ref[1])
        if obj:
            obj = obj[0].getObject()
            if i and not divmod(i, pgthreshold)[1]:
                logger.info("%s/%s %s/%s" % (i, len(refs), obj, relation))
            touidref(obj, obj, relation, portal_type, fieldname)
            refs_to_remove.append(relation)
            objs_to_reindex.append(obj)

def touidref(src, dst, src_relation, src_portal_type, fieldname):
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
        raise RuntimeError('Cannot find field %s/%s' % (fieldname, src))
    if field.required and not value:
        logger.exception('Required %s field %s/%s has no value' %
                         (src.portal_type, src, fieldname))
    field.set(src, value)


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
        raise RuntimeError('The UID for %s/%s cannot be found!' %
                           (value.portal_type, value.Title()))
    if len(brains) > 1:
        # Found multiple objects, this is a failure
        raise RuntimeError('Searching for %s/%s returned multiple objects.' %
                           (value.portal_type, value.Title()))
    return brains[0].UID


def del_at_refs(relation):
    # Remove this relation from at_references
    rc = get_tool(REFERENCE_CATALOG)
    refs = rc(relationship=relation)
    removed = 0
    size = 0
    if refs:
        logger.info("Found %s refs for %s" % (len(refs), relation))
        ref_dict = {ref[0]: ref.getObject() for ref in refs}
        for ref_id, ref_obj in ref_dict.items():
            removed += 1
            size += 1
            if ref_obj is not None:
                ref_obj.aq_parent.manage_delObjects([ref_id])
    if removed:
        logger.info("Performed %s deletions" % removed)
    return removed


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

def handle_AS_wo_category(portal):
    """
    Apparently, some of Analysis Services remained without category after
    migration.
    Creating a new Category ('unknown') and assigning those AS'es to it.
    """
    uc = getToolByName(portal, 'bika_setup_catalog')
    services = uc(portal_type='AnalysisService', getCategoryUID=None)
    if not services:
        logger.info("SKIPPING. There is no Analysis Service without category.")
        return

    # First , create a new 'Uknown' Category, if doesn't exist
    uc = getToolByName(portal, 'uid_catalog')
    acats = uc(portal_type='AnalysisCategory')
    for acat in acats:
        if acat.Title == 'Unknown':
            logger.info("Category 'Uknown' already exists...")
            category = acat.getObject()
            break
    else:
        category = _createObjectByType("AnalysisCategory",
                                       portal.bika_setup.bika_analysiscategories,
                                       tmpID())
        category.setTitle("Unknown")
        category._renameAfterCreation()
        category.reindexObject()
        logger.info("Category 'Unknown' was created...")

    counter = 0
    total = len(services)
    for s in services:
        obj = s.getObject()
        obj.setCategory(category)
        obj.reindexObject()
        counter += 1
        logger.info("Assigning Analysis Services to 'unknown' Category: %d of %d" % (counter, total))

    logger.info("Done! %d AnalysisServices were assigned to the Category 'unknown'."
                % counter)
