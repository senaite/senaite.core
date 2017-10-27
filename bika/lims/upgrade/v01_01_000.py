from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.config import  PROJECTNAME as product

from bika.lims.idserver import generateUniqueId

version = '1.1.0'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
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

    # Sync the empty number generator with existing content
    prepare_number_generator(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True

def prepare_number_generator(portal):
    # Load IDServer defaults

    config_map = [
        {'context': 'sample',
         'counter_reference': 'AnalysisRequestSample',
         'counter_type': 'backreference',
         'form': '{sampleId}-R{seq:02d}',
         'portal_type': 'AnalysisRequest',
         'prefix': '',
         'sequence_type': 'counter',
         'split_length': ''},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'B-{seq:03d}',
         'portal_type': 'Batch',
         'prefix': 'batch',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': '{sampleType}-{seq:04d}',
         'portal_type': 'Sample',
         'prefix': 'sample',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'WS-{seq:03d}',
         'portal_type': 'Worksheet',
         'prefix': 'worksheet',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'I-{seq:03d}',
         'portal_type': 'Invoice',
         'prefix': 'invoice',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'AI-{seq:03d}',
         'portal_type': 'ARImport',
         'prefix': 'arimport',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'QC-{seq:03d}',
         'portal_type': 'ReferenceSample',
         'prefix': 'refsample',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'SA-{seq:03d}',
         'portal_type': 'ReferenceAnalysis',
         'prefix': 'refanalysis',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': '',
         'counter_reference': '',
         'counter_type': '',
         'form': 'D-{seq:03d}',
         'portal_type': 'DuplicateAnalysis',
         'prefix': 'duplicate',
         'sequence_type': 'generated',
         'split_length': 1},
        {'context': 'sample',
         'counter_reference': 'SamplePartition',
         'counter_type': 'contained',
         'form': '{sampleId}-P{seq:d}',
         'portal_type': 'SamplePartition',
         'prefix': '',
         'sequence_type': 'counter',
         'split_length': ''}]
    # portal.bika_setup.setIDFormatting(config_map)

    # Regenerate every id to prime the number generator
    bsc = portal.bika_setup_catalog
    for brain in bsc():
        generateUniqueId(brain.getObject())

    pc = portal.portal_catalog
    for brain in pc():
        generateUniqueId(brain.getObject())
