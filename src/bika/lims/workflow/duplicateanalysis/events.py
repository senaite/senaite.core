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

import transaction

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IRetracted
from bika.lims.utils.analysis import create_retest
from bika.lims.utils.analysis import generate_analysis_id
from bika.lims.workflow import doActionFor
from bika.lims.workflow.analysis import events as analysis_events
from zope.interface import alsoProvides


def after_submit(duplicate_analysis):
    """Method triggered after a 'submit' transition for the duplicate analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    """
    analysis_events.after_submit(duplicate_analysis)


def after_verify(duplicate_analysis):
    """Function called after a 'verify' transition for the duplicate analysis
    passed in is performed
    Delegates to bika.lims.workflow.analysis.events.after_verify
    """
    analysis_events.after_verify(duplicate_analysis)


def after_unassign(duplicate_analysis):
    """Removes the duplicate from the system
    """
    analysis_events.after_unassign(duplicate_analysis)
    parent = duplicate_analysis.aq_parent
    logger.info("Removing duplicate '{}' from '{}'"
                .format(duplicate_analysis.getId(), parent.getId()))
    parent.manage_delObjects([duplicate_analysis.getId()])


def after_retract(duplicate_analysis):
    """Function triggered after a 'retract' transition for the duplicate passed
    in is performed. The duplicate transitions to "retracted" state and a new
    copy of the duplicate is created.
    """
    # Mark this duplicate as IRetracted
    alsoProvides(duplicate_analysis, IRetracted)

    # Rename the analysis to make way for it's successor
    parent = api.get_parent(duplicate_analysis)
    keyword = duplicate_analysis.getKeyword()
    duplicate_id = api.get_id(duplicate_analysis)
    retracted_id = generate_analysis_id(parent, keyword)

    # Rename the retracted duplicate
    # https://docs.plone.org/develop/plone/content/rename.html
    # _verifyObjectPaste permission check must be cancelled
    parent._verifyObjectPaste = str
    # Make sure all persistent objects have _p_jar attribute
    transaction.savepoint(optimistic=True)
    parent.manage_renameObject(duplicate_id, retracted_id)
    delattr(parent, '_verifyObjectPaste')

    # Find out the slot position of the duplicate in the worksheet
    worksheet = duplicate_analysis.getWorksheet()
    if not worksheet:
        logger.warn("Duplicate {} has been retracted, but without worksheet"
                    .format(duplicate_analysis.getId()))
        return

    dest_slot = worksheet.get_slot_position_for(duplicate_analysis)
    if not dest_slot:
        logger.warn("Duplicate {} has been retracted, but not found in any"
                    "slot of worksheet {}"
                    .format(duplicate_analysis.getId(), worksheet.getId()))
        return

    # Create a copy (retest) of the duplicate, but with results preserved
    kwargs = {
        "Result": duplicate_analysis.getResult(),
        "InterimFields": duplicate_analysis.getInterimFields()
    }
    retest = create_retest(duplicate_analysis, **kwargs)

    # Assign assign the retest to worksheet
    worksheet.addToLayout(retest, dest_slot)
    worksheet.setAnalyses(worksheet.getAnalyses() + [retest, ])

    # Reindex
    worksheet.reindexObject(idxs=["getAnalysesUIDs"])

    # Try to rollback the worksheet to prevent inconsistencies
    doActionFor(worksheet, "rollback_to_open")
