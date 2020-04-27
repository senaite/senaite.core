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

""" Sysmex XT1800i
"""
import json
import traceback

from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import InstrumentTXTResultsFileParser
from bika.lims.exportimport.instruments.sysmex.xt import SysmexXTImporter
from bika.lims.utils import t

title = "Sysmex XT - 1800i"


def Import(context, request):
    """
    This function handles requests when user uploads a file and submits. Gets
    requests parameters, and creates a Parser object. Then based on that
    parser object, creates an Importer object and calls its importer.
    """
    infile = request.form['tx1800i_file']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']

    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []
    status_mapping = {
        'received': ['sample_received'],
        'received_tobeverified': ['sample_received', 'attachment_due', 'to_be_verified']
    }
    override_mapping = {
        'nooverride': [False, False],
        'override': [True, False],
        'overrideempty': [True, True]
    }

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'txt':
        parser = TX1800iParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))
    if parser:
        # Load the importer
        status = status_mapping.get(artoapply, ['sample_received', 'attachment_due', 'to_be_verified'])
        over = override_mapping.get(override, [False, False])
        importer = SysmexXTImporter(parser=parser,
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

SEPARATOR = '|'
SEGMENT_HEADER = 'H'
SEGMENT_OBSERVATION_ORDER = 'OBR'
SEGMENT_RESULT = 'OBX'
SEGMENT_EOF = 'L'
SEGMENT_COMMENT = 'C'


class TX1800iParser(InstrumentTXTResultsFileParser):

    def __init__(self, infile):
        InstrumentTXTResultsFileParser.__init__(self, infile, SEPARATOR, encoding="utf-8-sig")
        self._cur_res_id = ''  # Sample ID of the current record
        self._cur_values = {}  # 'values' dictionary of current sample

    def _parseline(self, line):
        """
        All lines come to this method.
        :param line: a to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        sline = line.split(SEPARATOR)
        segment = sline[0]
        handlers = {
            SEGMENT_HEADER: self._handle_header,
            SEGMENT_EOF: self._handle_eof,
            SEGMENT_RESULT: self._handle_result_line,
            SEGMENT_OBSERVATION_ORDER: self._handle_new_record
        }
        handler = handlers.get(segment)
        if handler:
            return handler(sline)
        return 0

    def _handle_header(self, sline):
        """
        From header line we don't need anything so far.
        """
        return 0

    def _handle_new_record(self, sline):
        """
        From header line we don't need anything so far.
        """
        self._submit_results()
        self._cur_res_id = sline[3]
        return 0

    def _handle_result_line(self, sline):
        """
        Parses the data line and adds to the dictionary.
        :param sline: a split data line to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        as_kw = sline[3]
        a_result = str(sline[5].split('^')[0])
        self._cur_values[as_kw] = {
            'DefaultResult': 'Result',
            'Result': a_result
        }
        return 0

    def _handle_eof(self, sline):
        """
        From header line we don't need anything so far.
        """
        self._submit_results()
        return 0

    def _submit_results(self):
        """
        Adding current values as a Raw Result and Resetting everything.
        """
        if self._cur_res_id and self._cur_values:
            # Setting DefaultResult just because it is obligatory.
            self._addRawResult(self._cur_res_id, self._cur_values)
            self._reset()

    def _reset(self):
        self._cur_res_id = ''
        self._cur_values = {}
