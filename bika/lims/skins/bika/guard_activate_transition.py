# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

## Script (Python) "guard_activate_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if context.portal_type == 'AnalysisService':
    workflow = context.portal_workflow
    calculation = context.getCalculation()
    if not calculation:
        return True

    # If the calculation is inactive, we cannot activate the service
    status = workflow.getInfoFor(calculation, 'inactive_state')
    if status and status == 'inactive':
        return False

    # All services that we depend on to calculate our result are active or we
    # don't depend on other services.
    dependencies = calculation.getDependentServices()
    for dependency in dependencies:
        status = workflow.getInfoFor(dependency, 'inactive_state')
        if status and status == 'inactive':
            return False
return True
