# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
