# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

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

    # -------- ADD YOUR STUFF HERE --------

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
