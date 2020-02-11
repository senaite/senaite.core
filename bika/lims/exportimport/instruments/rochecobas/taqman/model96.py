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

""" Roche Cobas Taqman 96
"""
import csv
from DateTime import DateTime

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Roche Cobas - Taqman - 96"

# see: https://jira.bikalabs.com/browse/HEALTH-568
NUM_FIELDS = ["Result", "CTM Elbow CH1", "CTM Elbow CH2", "CTM Elbow CH3",
              "CTM Elbow CH4", "CTM RFI CH1", "CTM RFI CH2",
              "CTM RFI CH3", "CTM RFI CH4", "CTM AFI CH1", "CTM AFI CH2",
              "CTM AFI CH3", "CTM AFI CH4", "CTM Calib Coeff a",
              "CTM Calib Coeff b", "CTM Calib Coeff c", "CTM Calib Coeff d",
              "CA Sample Value", "QS Copy #", "CA Target1", "CA Target2",
              "CA Target3", "CA Target4", "CA Target5", "CA Target6",
              "CA QS1", "CA QS2", "CA QS3", "CA QS4"]


class RocheCobasTaqmanRSFParser(InstrumentResultsFileParser):
    """ Parser for Roche Corbase Taqman 96
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'CSV')

    def parse_field(self, key, value):
        if value in ["-", ""]:
            return None
        if key in NUM_FIELDS:
            try:
                return float(value)
            except ValueError:
                return value

    def parse(self):
        reader = csv.DictReader(self.getInputFile(), delimiter=',')

        for n, row in enumerate(reader):
            resid = row.get("Sample ID", None)
            orderno = row.get("Order Number", None)

            # no resid and no orderno
            if not any([resid, orderno]):
                self.err("Result identification not found.", numline=n)
                continue

            testname = row.get("Test", None)
            if testname is None:
                self.err("Result test name not found.", numline=n)
                continue

            dt = row.get("Accepted Date/Time", None)
            if dt is not None:
                dt = DateTime(dt)

            remarks = ""
            result = row.get("Result")
            if result == "Target Not Detected":
                remarks = "".join([result, " on Order Number,", resid])

            rawdict = {}
            for k, v in row.iteritems():
                rawdict[k] = self.parse_field(k, v)

            rawdict['DefaultResult'] = 'Result'
            rawdict['Remarks'] = remarks
            rawdict['DateTime'] = dt

            self._addRawResult(resid, {testname: rawdict}, False)


class RocheCobasTaqmanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Beckman Coulter Access 2 analysis results
    """
    infile = request.form['rochecobas_taqman_model96_file']
    fileformat = request.form['rochecobas_taqman_model96_format']
    artoapply = request.form['rochecobas_taqman_model96_artoapply']
    override = request.form['rochecobas_taqman_model96_override']
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'rsf':
        parser = RocheCobasTaqmanRSFParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
        status = ['sample_received', 'attachment_due', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'attachment_due', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        importer = RocheCobasTaqmanImporter(parser=parser,
                                            context=context,
                                            allowed_ar_states=status,
                                            allowed_analysis_states=None,
                                            override=over,
                                            instrument_uid=instrument)
        tbex = ''
        try:
            importer.process()
        except:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)
