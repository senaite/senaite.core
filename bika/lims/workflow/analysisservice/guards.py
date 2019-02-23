# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
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
    calc_status = api.get_workflow_status_of(calculation)
    if calc_status == "inactive":
        return False

    # All services that we depend on to calculate our result are active or we
    # don't depend on other services.
    dependencies = calculation.getDependentServices()
    for dependency in dependencies:
        status = api.get_workflow_status_of(dependency)
        if status == "inactive":
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
