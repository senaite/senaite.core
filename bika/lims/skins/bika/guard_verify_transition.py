# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

## Script (Python) "guard_verify_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

checkPermission = context.portal_membership.checkPermission

if hasattr(context, 'guard_verify_transition'):
    return context.guard_verify_transition()

# Can't do anything to the object if it's cancelled
workflow = context.portal_workflow
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

return True
