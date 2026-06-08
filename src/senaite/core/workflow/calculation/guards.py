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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.catalog import SETUP_CATALOG


def guard_activate(calculation):
    """Return whether the transition "activate" can be performed or not.
    """
    # A calculation cannot be re-activated if services it depends on
    # are deactivated.
    services = calculation.getDependentServices()
    for service in services:
        if not api.is_active(service):
            return False
    return True


def guard_deactivate(calculation):
    """Return whether the transition "deactivate" can be performed or not.
    """
    # Calculation cannot be deactivated if used in active AnalysisService
    query = dict(portal_type="AnalysisService",
                 is_active=True)
    brains = api.search(query, SETUP_CATALOG)
    for brain in brains:
        service = api.get_object(brain)
        calc_uid = service.getRawCalculation()
        if calc_uid == calculation.UID():
            return False
    return True
