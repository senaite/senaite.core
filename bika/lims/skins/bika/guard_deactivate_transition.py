# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

## Script (Python) "guard_deactivate_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if context.portal_type == 'AnalysisService':
    # Return true only if there are no services that depend on us to calculate
    # their results or all them have been deactivated already.
    dependants = context.getServiceDependants()
    if not dependants:
        return True

    workflow = context.portal_workflow
    for dependant in dependants:
        status = workflow.getInfoFor(dependant, 'inactive_state')
        if status and status == 'active':
            return False
return True
