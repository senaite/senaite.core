#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Beckman Couter Access
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class BeckmancoulterAccessCSVParser(InstrumentCSVResultsFileParser):
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
        :return: the number of rows to jump and parse the next data line or return the code error -1
        """
        # if there are less values founded than headers, it's an error
        if len(sline) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return -1
        rawdict = {}
        for idx, result in enumerate(sline):
            rawdict[self._columns[idx]] = result
        # Getting key values
        resid = rawdict['Sample ID']
        del rawdict['Sample ID']
        testname = rawdict['Test Name']
        del rawdict['Test Name']

        # Building the new dict
        rawdict['DefaultResult'] = 'Result'
        rawdict['Remarks'] = rawdict['Comments'].join(rawdict['Interpretation'])
        del rawdict['Comments']
        del rawdict['Interpretation']
        rawdict['DateTime'] = self.csvDate2BikaDate(rawdict['Load Date/Time'])
        self._addRawResult(resid, {testname: rawdict}, False)
        return 0

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        Date, Time = DateTime.split(' ')
        dtobj = datetime.strptime(Date + ' ' + Time, "%d/%m/%Y %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")


class BeckmancoulterAccessImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
