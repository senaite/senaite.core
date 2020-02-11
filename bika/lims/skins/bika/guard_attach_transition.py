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

## Script (Python) "guard_attach_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

if context.portal_type == "AnalysisRequest":
    # Allow transition to 'attach'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses(full_objects=True):
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            return False
    return True

if context.portal_type == "Worksheet":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses():
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            # Note: referenceanalyses and duplicateanalysis can
            # still have review_state = "assigned".
            return False

return True
