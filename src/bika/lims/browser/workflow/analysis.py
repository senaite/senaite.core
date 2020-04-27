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

import json
from collections import defaultdict

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IReferenceAnalysis
from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time


class WorkflowActionSubmitAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of submission of analyses
    """

    def __call__(self, action, objects):
        # Store invalid instruments-ref.analyses
        invalid_instrument_refs = defaultdict(set)

        # Get interims data
        interims_data = self.get_interims_data()

        for analysis in objects:

            # Using the global WF menu passes the AR as context
            # https://github.com/senaite/senaite.core/issues/1306
            if not IAnalysis.providedBy(analysis):
                continue

            uid = api.get_uid(analysis)

            # Need to save remarks?
            remarks = self.get_form_value("Remarks", uid, default="")
            analysis.setRemarks(remarks)

            # Need to save the instrument?
            instrument = self.get_form_value("Instrument", uid, None)
            if instrument is not None:
                # Could be an empty string
                instrument = instrument or None
                analysis.setInstrument(instrument)
                if instrument and IReferenceAnalysis.providedBy(analysis):
                    if is_out_of_range(analysis):
                        # This reference analysis is out of range, so we have
                        # to retract all analyses assigned to this same
                        # instrument that are awaiting for verification
                        invalid_instrument_refs[uid].add(analysis)
                    else:
                        # The reference result is valid, so make the instrument
                        # available again for further analyses
                        instrument.setDisposeUntilNextCalibrationTest(False)

            # Need to save the method?
            method = self.get_form_value("Method", uid, default=None)
            if method is not None:
                method = method or None
                analysis.setMethod(method)

            # Need to save analyst?
            analyst = self.get_form_value("Analyst", uid, default=None)
            if analyst is not None:
                analysis.setAnalyst(analyst)

            # Save uncertainty
            uncertainty = self.get_form_value("Uncertainty", uid, "")
            analysis.setUncertainty(uncertainty)

            # Save detection limit
            dlimit = self.get_form_value("DetectionLimitOperand", uid, "")
            analysis.setDetectionLimitOperand(dlimit)

            # Interim fields
            interims = interims_data.get(uid, analysis.getInterimFields())
            analysis.setInterimFields(interims)

            # Save Hidden
            hidden = self.get_form_value("Hidden", uid, "")
            analysis.setHidden(hidden == "on")

            # Only set result if it differs from the actual value to preserve
            # the result capture date
            result = self.get_form_value("Result", uid,
                                         default=analysis.getResult())
            if result != analysis.getResult():
                analysis.setResult(result)

        # Submit all analyses
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # If a reference analysis with an out-of-range result and instrument
        # assigned has been submitted, retract then routine analyses that are
        # awaiting for verification and with same instrument associated
        retracted = list()
        for invalid_instrument_uid in invalid_instrument_refs.keys():
            query = dict(getInstrumentUID=invalid_instrument_uid,
                         portal_type=['Analysis', 'DuplicateAnalysis'],
                         review_state='to_be_verified',)
            brains = api.search(query, CATALOG_ANALYSIS_LISTING)
            for brain in brains:
                analysis = api.get_object(brain)
                failed_msg = '{0}: {1}'.format(
                    ulocalized_time(DateTime(), long_format=1),
                    _("Instrument failed reference test"))
                an_remarks = analysis.getRemarks()
                analysis.setRemarks('. '.join([an_remarks, failed_msg]))
                retracted.append(analysis)

        # If some analyses have been retracted because instrument failed a
        # reference test, then generate a pdf report
        if self.do_action("retract", retracted):
            # Create the Retracted Analyses List
            portal_url = api.get_url(api.get_portal())
            report = AnalysesRetractedListReport(self.context, self.request,
                                                 portal_url,
                                                 'Retracted analyses',
                                                 retracted)

            # Attach the pdf to all ReferenceAnalysis that failed (accessible
            # from Instrument's Internal Calibration Tests list
            pdf = report.toPdf()
            for ref in invalid_instrument_refs.values():
                ref.setRetractedAnalysesPdfReport(pdf)

            # Send the email
            try:
                report.sendEmail()
            except Exception as err_msg:
                message = "Unable to send email: {}".format(err_msg)
                logger.warn(message)

        # Redirect to success view
        return self.success(transitioned)

    def get_interims_data(self):
        """Returns a dictionary with the interims data
        """
        form = self.request.form
        if 'item_data' not in form:
            return {}

        item_data = {}
        if type(form['item_data']) == list:
            for i_d in form['item_data']:
                for i, d in json.loads(i_d).items():
                    item_data[i] = d
            return item_data

        return json.loads(form['item_data'])
