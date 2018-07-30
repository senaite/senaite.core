# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" Beckman Couter Access
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class TaqMan96DNA212BSCSVParser(InstrumentCSVResultsFileParser):
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
        #print self._columns
        rawdict = {}
        for idx, result in enumerate(sline):
            rawdict[self._columns[idx]] = result
        # Getting key values
        resid = rawdict['Sample ID']
        del rawdict['Sample ID']
        testname = rawdict['Test']
        del rawdict['Test']

        # Building the new dict
        rawdict['DefaultResult'] = 'Result'
        rawdict['Remarks'] = rawdict['Comment']
        del rawdict['Comment']
        print rawdict

        self._addRawResult(resid, {testname: rawdict}, False)
        return 0


class TaqMan96DNA212BSImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
