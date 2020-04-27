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


def guard_activate(analysis_service):
    """Returns whether the transition activate can be performed for the
    analysis service passed in
    """
    calculation = analysis_service.getCalculation()
    if not calculation:
        return True

    # If the calculation is inactive, we cannot activate the service
    if not api.is_active(calculation):
        return False

    # All services that we depend on to calculate our result are active or we
    # don't depend on other services.
    dependencies = calculation.getDependentServices()
    for dependency in dependencies:
        if not api.is_active(dependency):
            return False

    return True


def guard_deactivate(analysis_service):
    """Returns whether the transition deactivate can be performed for the
    analysis service passed in
    """
    for dependant in analysis_service.getServiceDependants():
        status = api.get_workflow_status_of(dependant)
        if status == "active":
            return False

    return True
