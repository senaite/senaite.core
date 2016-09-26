# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

## Script (Python) "guard_retract_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from bika.lims.permissions import Retract

workflow = context.portal_workflow
checkPermission = context.portal_membership.checkPermission

# Can't do anything to the object if it's cancelled
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

if checkPermission(Retract, context):
    return True

return False
