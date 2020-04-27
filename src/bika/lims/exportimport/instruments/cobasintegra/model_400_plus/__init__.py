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

""" Cobas Integra 400 plus
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class CobasIntegra400plusCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []  # The different columns names
        self._values = {}  # The analysis services from the same resid
        self._resid = ''  # A stored resid
        self._rownum = None
        self._end_header = False

    def _parseline(self, line):
        sline = line.split(',')
        if len(sline) > 0 and not self._end_header:
            self._columns = sline
            for i, column in enumerate(self._columns):
                column = column.strip()
                self._columns[i] = column
            self._end_header = True
            return 0
        elif sline > 0 and self._end_header:
            self.parse_data_line(sline)
        else:
            self.err("Unexpected data format", numline=self._numline)
            return -1

    def parse_data_line(self, sline):
        """
        Parses the data line and builds the dictionary.
        :param sline: a split data line to parse
        :returns: the number of rows to jump and parse the next data line or return the code error -1
        """
        # if there are less values founded than headers, it's an error
        if len(sline) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return -1
        rawdict = {}
        for idx, result in enumerate(sline):
            rawdict[self._columns[idx]] = result
        # Getting key values
        resid = rawdict['order_id']
        del rawdict['order_id']
        testname = rawdict['test_name']
        del rawdict['test_name']
        # Building the new dict
        rawdict['DefaultResult'] = 'result_concentration'
        self._addRawResult(resid, {testname: rawdict}, False)
        return 0


class CobasIntegra400plusImporter(AnalysisResultsImporter):
    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
