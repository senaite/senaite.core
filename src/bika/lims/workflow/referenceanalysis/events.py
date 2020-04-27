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
from bika.lims import logger
from bika.lims import workflow as wf
from bika.lims.workflow.analysis import events as analysis_events


def after_submit(reference_analysis):
    """Method triggered after a 'submit' transition for the reference analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    """
    analysis_events.after_submit(reference_analysis)


def after_verify(reference_analysis):
    """Function called after a 'verify' transition for the reference analysis
    passed in is performed
    Delegates to bika.lims.workflow.analysis.events.after_verify
    """
    analysis_events.after_verify(reference_analysis)


def after_unassign(reference_analysis):
    """Removes the reference analysis from the system
    """
    analysis_events.after_unassign(reference_analysis)
    ref_sample = reference_analysis.aq_parent
    ref_sample.manage_delObjects([reference_analysis.getId()])


def after_retract(reference_analysis):
    """Function triggered after a 'retract' transition for the reference
    analysis passed in is performed. The reference analysis transitions to
    "retracted" state and a new copy of the reference analysis is created
    """
    reference = reference_analysis.getSample()
    service = reference_analysis.getAnalysisService()
    worksheet = reference_analysis.getWorksheet()
    instrument = reference_analysis.getInstrument()
    if worksheet:
        # This a reference analysis in a worksheet
        slot = worksheet.get_slot_position_for(reference_analysis)
        refgid = reference_analysis.getReferenceAnalysesGroupID()
        ref = worksheet.add_reference_analysis(reference, service, slot, refgid)
        if not ref:
            logger.warn("Cannot add a retest for reference analysis {} into {}"
                        .format(reference_analysis.getId(), worksheet.getId()))
            return

        ref.setRetestOf(reference_analysis)
        ref.setResult(reference_analysis.getResult())
        if instrument:
            ref.setInstrument(instrument)
            instrument.reindexObject()

        # Try to rollback the worksheet to prevent inconsistencies
        wf.doActionFor(worksheet, "rollback_to_open")

    elif instrument:
        # This is an internal calibration test
        instrument.addReferences(reference, [api.get_uid(service)])
        instrument.reindexObject()
