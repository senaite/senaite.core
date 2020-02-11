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

from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.idserver import generateUniqueId
from bika.lims.interfaces import INumberGenerator
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from zope.component import getUtility

version = '1.1.5'
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

    # Sync the empty number generator with existing content
    prepare_number_generator(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True

def prepare_number_generator(portal):
    number_generator = getUtility(INumberGenerator)
    if len(number_generator.keys()) > 1:
        logger.info('Skip number generator initialisation')
        return

    logger.info('Initialise number generator')
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
