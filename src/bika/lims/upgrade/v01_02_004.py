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

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING

version = '1.2.4'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Required to make filtering by department in worksheets work
    ut.addIndex(CATALOG_WORKSHEET_LISTING, 'getDepartmentUIDs', 'KeywordIndex')
    # Required by https://github.com/senaite/senaite.core/issues/683
    ut.addIndexAndColumn('bika_catalog', 'getBatchUIDs', 'KeywordIndex')
    # Required by https://github.com/senaite/senaite.core/pulls/752
    ut.delIndex(CATALOG_ANALYSIS_LISTING, 'getDateAnalysisPublished')

    ut.refreshCatalogs()

    # % Error subfield is meaningless in result ranges. Also, the system was
    # calculating the %Error based on the result (not based on the range), so
    # the shoulder from the left was always smaller than the shoulder from the
    # right. One could argue that this could be fixed easily by using the length
    # of the valid range to compute the shoulders by using the %error. Again,
    # this is a weak solution, cause in some cases the scale of the range might
    # be exponential, logaritmic (e.g. pH). Also, the sensitivity of the test
    # may differ when the result falls in one end or another. Thus, is for the
    # best interest of the labmanger to be able to set the shoulders (and
    # therefore, when the warnings must show up) manually.
    # See PR#694
    remove_error_subfield_from_analysis_specs(portal, ut)

    # Reindex ReferenceAnalysis because of Calculation and Interims fields have
    # been added to Controls and Blanks. Until now, only routine analyses allowed
    # Calculations and Interim fields
    # Required by https://github.com/senaite/senaite.core/issues/735
    reindex_reference_analysis(portal, ut)

    # reload type profiles so that the fix for
    # https://github.com/senaite/senaite.core/issues/590
    # becomes effective
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True

def remove_error_subfield_from_analysis_specs(portal, ut):
    # Update Analysis Specifications
    catalog = api.get_tool('bika_setup_catalog')
    brains = catalog(portal_type='AnalysisSpec')
    for brain in brains:
        specs = api.get_object(brain)
        specs_rr = specs.getResultsRange()
        for spec in specs_rr:
            min = spec.get('min', '')
            max = spec.get('max', '')
            error = api.to_float(spec.get('error', '0'), 0)
            if api.is_floatable(min) and api.is_floatable(max) and error > 0:
                # Add min_warn and max_warn fields
                min = api.to_float(min)
                max = api.to_float(max)
                warn_min = min - (abs(min) * (error/100.0))
                warn_max = max + (abs(max) * (error/100.0))
                spec['warn_min'] = str(warn_min)
                spec['warn_max'] = str(warn_max)
                del spec['error']
        specs.setResultsRange(specs_rr)


def reindex_reference_analysis(portal, ut):
    # Update ReferenceAnalysis because new fields(Calculation & InterimFields)
    # have been added on ReferenceAnalysis
    catalog = api.get_tool('bika_analysis_catalog')
    brains = catalog(portal_type='ReferenceAnalysis')
    exclude_states = ['to_be_verified', 'verified', 'published']
    for brain in brains:
        if brain.review_state in exclude_states:
            continue
        analysis = api.get_object(brain)
        # Assign calculation and interims
        service = analysis.getAnalysisService()
        service = api.get_object(service)
        calc = service.getCalculation()
        if not calc:
            # No calculation, no need to reindex!
            continue
        analysis.setCalculation(calc)
        analysis.setInterimFields(calc.getInterimFields())
        analysis.reindexObject()
        logger.info("Updated Analysis '%s'  with calculation '%s'" % (analysis.Title(), calc.Title()))
