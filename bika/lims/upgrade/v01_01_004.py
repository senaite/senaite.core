from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from plone.api.portal import get_tool

version = '1.1.5'  # Remember version number in metadata.xml and setup.py
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

    UpgradeReferenceFields()

    return True


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
        ['Analysis', [
            # Fieldname          Relationship name
            #('AnalysisService', 'AnalysisAnalysisService'),
            ('Attachment', 'AnalysisAttachment'),
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            ('OriginalReflexedAnalysis', 'AnalysisOriginalReflexedAnalysis'),
            ('ReflexAnalysisOf', 'AnalysisReflexAnalysisOf'),
            ('SamplePartition', 'AnalysisSamplePartition')
        ]],
        ['AnalysisCategory', [
            ('Department', 'AnalysisCategoryDepartment')
        ]],
        ['AnalysisProfile', [
            ('Service', 'AnalysisProfileAnalysisService')
        ]],
        ['AnalysisRequest', [
            ('Attachment', 'AnalysisRequestAttachment'),
            ('Batch', 'AnalysisRequestBatch'),
            ('CCContact', 'AnalysisRequestCCContact'),
            ('ChildAnalysisRequest', 'AnalysisRequestChildAnalysisRequest'),
            ('Client', 'AnalysisRequestClient'),
            ('Contact', 'AnalysisRequestContact'),
            ('DefaultContainerType', 'AnalysisRequestContainerType'),
            ('Invoice', 'AnalysisRequestInvoice'),
            ('ParentAnalysisRequest', 'AnalysisRequestParentAnalysisRequest'),
            ('Profiles', 'AnalysisRequestAnalysisProfiles'),
            ('PublicationSpecification', 'AnalysisRequestPublicationSpec'),
            ('Sample', 'AnalysisRequestSample'),
            ('SamplingRound', 'AnalysisRequestSamplingRound'),
            ('Specification', 'AnalysisRequestAnalysisSpec'),
            ('SubGroup', 'AnalysisRequestSubGroup'),
            ('Template', 'AnalysisRequestARTemplate')
        ]],
        ['AnalysisService', [
            ('Calculation', 'AnalysisServiceCalculation'),
            ('Category', 'AnalysisServiceCategory'),
            ('Container', 'AnalysisServiceContainer'),
            ('Department', 'AnalysisServiceDepartment'),
            ('Instrument', 'AnalysisServiceInstrument'),
            ('Instruments', 'AnalysisServiceInstruments'),
            ('Method', 'AnalysisServiceMethod'),
            ('Methods', 'AnalysisServiceMethods'),
            ('Preservation', 'AnalysisServicePreservation')
        ]],
        ['AnalysisSpec', [
            ('SampleType', 'AnalysisSpecSampleType')
        ]],
        ['ARImport', [
            ('Batch', 'ARImportBatch'),
            ('Contact', 'ARImportContact')
        ]],
        ['ARReport', [
            ('AnalysisRequest', 'ARReportAnalysisRequest')
        ]],
        ['ARTemplate', [
            ('AnalysisProfile', 'ARTemplateAnalysisProfile'),
            ('SamplePoint', 'ARTemplateSamplePoint'),
            ('SampleType', 'ARTemplateSampleType')
        ]],
        ['Attachment', [
            ('AttachmentType', 'AttachmentAttachmentType')
        ]],
        ['AutoImportLog', [
            ('Instrument', 'InstrumentImportLogs')
        ]],
        ['Batch', [
            ('Client', 'BatchClient'),
            ('InheritedObjects', 'BatchInheritedObjects')
        ]],
        ['BikaSetup', [
            ('DryMatterService', 'SetupDryAnalysisService'),
            ('LandingPage', 'SetupLandingPage')
        ]],
        ['Calculation', [
            ('DependentServices', 'CalculationDependentServices')
        ]],
        ['Client', [
            ('DefaultCategories', 'ClientDefaultCategories'),
            ('RestrictedCategories', 'ClientRestrictedCategories')
        ]],
        ['Contact', [
            ('CCContact', 'ContactContact')
        ]],
        ['Container', [
            ('ContainerType', 'ContainerContainerType'),
            ('Preservation', 'ContainerPreservation')
        ]],
        ['Department', [
            ('Manager', 'DepartmentLabContact')
        ]],
        ['DuplicateAnalysis', [
            ('Analysis', 'DuplicateAnalysisAnalysis'),
            ('AnalysisService', 'DuplicateAnalysisAnalysisService'),
            ('Attachment', 'DuplicateAnalysisAttachment'),
            ('Category', 'DuplicateAnalysisCategory'),
            ('Department', 'DuplicateAnalysisDepartment'),
            ('Instrument', 'DuplicateAnalysisInstrument'),
            ('Method', 'DuplicateAnalysisMethod'),
            ('OriginalReflexedAnalysis',
             'DuplicateAnalysisOriginalReflexedAnalysis'),
            ('ReflexAnalysisOf', 'DuplicateAnalysisReflexAnalysisOf'),
            ('SamplePartition', 'DuplicateAnalysisSamplePartition')
        ]],
        ['Instrument', [
            ('_LatestReferenceAnalyses', 'InstrumentLatestReferenceAnalyses'),
            ('Analyses', 'InstrumentAnalyses'),
            ('InstrumentLocation', 'InstrumentInstrumentLocation'),
            ('InstrumentType', 'InstrumentInstrumentType'),
            ('Manufacturer', 'InstrumentManufacturer'),
            ('Method', 'InstrumentMethod'),
            ('Methods', 'InstrumentMethods'),
            ('Supplier', 'InstrumentSupplier')
        ]],
        ['InstrumentCalibration', [
            ('Instrument', 'InstrumentCalibrationInstrument'),
            ('Worker', 'LabContactInstrumentCalibration')
        ]],
        ['InstrumentCertification', [
            ('Instrument', 'InstrumentCertificationInstrument'),
            ('Preparator', 'LabContactInstrumentCertificatePreparator'),
            ('Validator', 'LabContactInstrumentCertificateValidator')
        ]],
        ['InstrumentMaintenanceTask', [
            ('Instrument', 'InstrumentMaintenanceTaskInstrument')
        ]],
        ['InstrumentScheduledTask', [
            ('Instrument', 'InstrumentScheduledTaskInstrument')
        ]],
        ['InstrumentValidation', [
            ('Worker', 'LabContactInstrumentValidation')
        ]],
        ['Invoice', [
            ('AnalysisRequest', 'AnalysisRequestInvoice'),
            ('Client', 'ClientInvoice'),
            ('SupplyOrder', 'SupplyOrderInvoice')
        ]],
        ['LabContact', [
            ('Departments', 'LabContactDepartment')
        ]],
        ['Laboratory', [
            ('Supervisor', 'LaboratorySupervisor')
        ]],
        ['Method', [
            ('Calculation', 'MethodCalculation')
        ]],
        ['ReferenceAnalysis', [
            ('AnalysisService', 'ReferenceAnalysisAnalysisService'),
            ('Attachment', 'ReferenceAnalysisAttachment'),
            #('Category', 'ReferenceAnalysisCategory'),
            #('Department', 'ReferenceAnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod')
        ]],
        ['ReferenceSample', [
            ('Manufacturer', 'ReferenceSampleManufacturer'),
            ('ReferenceDefinition', 'ReferenceSampleReferenceDefinition')
        ]],
        ['ReflexRule', [
            ('Method', 'ReflexRuleMethod')
        ]],
        ['RejectAnalysis', [
            ('Analysis', 'RejectAnalysisAnalysis'),
            ('AnalysisService', 'AnalysisAnalysisService'),
            ('Attachment', 'AnalysisAttachment'),
            ('Category', 'AnalysisCategory'),
            ('Department', 'AnalysisDepartment'),
            ('Instrument', 'AnalysisInstrument'),
            ('Method', 'AnalysisMethod'),
            ('OriginalReflexedAnalysis',
             'AnalysisOriginalReflexedAnalysis'),
            ('ReflexAnalysisOf', 'AnalysisReflexAnalysisOf'),
            ('SamplePartition', 'AnalysisSamplePartition')
        ]],
        ['Report', [
            ('Client', 'ReportClient')
        ]],
        ['Sample', [
            ('LinkedSample', 'SampleSample'),
            ('SampleCondition', 'SampleSampleCondition'),
            ('SamplePoint', 'SampleSamplePoint'),
            ('SampleType', 'SampleSampleType'),
            ('SamplingDeviation', 'SampleSamplingDeviation'),
            ('StorageLocation', 'AnalysisRequestStorageLocation')
        ]],
        ['SamplePartition', [
            ('Analyses', 'SamplePartitionAnalysis'),
            ('Container', 'SamplePartitionContainer'),
            ('Preservation', 'SamplePartitionPreservation')
        ]],
        ['SamplePoint', [
            ('SampleTypes', 'SamplePointSampleType')
        ]],
        ['SampleType', [
            ('ContainerType', 'SampleTypeContainerType'),
            ('SampleMatrix', 'SampleTypeSampleMatrix'),
            ('SamplePoints', 'SampleTypeSamplePoint')
        ]],
        ['SRTemplate', [
            ('ARTemplates', 'SRTemplateARTemplate'),
            ('Department', 'SRTemplateDepartment')
        ]],
        ['SupplyOrder', [
            ('Contact', 'SupplyOrderContact'),
            ('Invoice', 'OrderInvoice')
        ]],
        ['Worksheet', [
            ('Analyses', 'WorksheetAnalysis'),
            ('Instrument', 'WorksheetInstrument'),
            ('Method', 'WorksheetMethod'),
            ('WorksheetTemplate', 'WorksheetAnalysisTemplate')
        ]],
        ['WorksheetTemplate', [
            ('Instrument', 'WorksheetTemplateInstrument'),
            ('RestrictToMethod', 'WorksheetTemplateMethod'),
            ('Service', 'WorksheetTemplateAnalysisService')
        ]]]:

        logger.info("Migrating references for portal_type: %s" % portal_type)

        for fieldname, relation in fields:
            if is_UIDReferenceField(portal_type, fieldname):
                migrate_refs(portal_type, relation, fieldname)


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
    if refs:
        logger.info('Migrating %s references of %s' % (len(refs), relation))
    refs_to_remove = []
    for i, ref in enumerate(refs):
        obj = uc(UID=ref[1])
        if obj:
            obj = obj[0].getObject()
            if i and not divmod(i, pgthreshold)[1]:
                logger.info("%s/%s %s/%s" % (i, len(refs), obj, relation))
            touidref(obj, obj, relation, portal_type, fieldname)
            refs_to_remove.append(relation)


def touidref(src, dst, src_relation, src_portal_type, fieldname):
    """Convert an archetypes reference in src/src_relation to a UIDReference
    in dst/fieldname.
    """
    field = dst.getField(fieldname)
    refs = src.getRefs(relationship=src_relation)

    import pdb
    from commands import getoutput as go
    go("/usr/bin/play /home/rockfruit/pdb.wav")
    pdb.set_trace()
    print("Well, is the src portal_type a match for migrate_refs first arg?")
    print("reason I ask is, ReferenceAnalysis always subclassed Analysis,")
    print("and so the relation names are the same! Simply asking the reference")
    print("catalog for references of a certain relation name, won't work")

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
