#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Rigaku Supermini
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class RigakuSuperminiCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []  # The different columns names
        self._end_header = False
        # This list contains all the rows without interesting data
        self.extrainfolist = ['Number', 'Average', 'Maximum', 'Minimum', 'Range', 'Std dev.',
                              'RSD(%)']

    def _parseline(self, line):
        sline = line.split(',')
        if len(sline) > 0 and not self._end_header:
            self._columns = sline[4:]
            self._end_header = True
            return 1
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
        if len(sline[4:]) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return -1

        resid = sline[0]
        analysis = {}
        date = sline[3]
        if sline[0] in self.extrainfolist:
            return 0
        for idx, result in enumerate(sline[4:]):
            if result != '':
                analysis[self._columns[idx]] = {
                    'result': result,
                    'DefaultResult': 'result',
                    'DateTime': date,
                }
        self._addRawResult(resid, analysis, False)
        return 0


class RigakuSuperminiImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
