#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Roche Cobas Taqman 48
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class RocheCobasTaqmanRSFParser(InstrumentCSVResultsFileParser):
    def __init__(self, rsf):
        InstrumentCSVResultsFileParser.__init__(self, rsf)
        self._columns = []  # The different columns names
        self._values = {}  # The analysis services from the same resid
        self._resid = ''  # A stored resid
        self._rownum = None
        self._end_header = False

    def _parseline(self, line):
        sline = line.replace('"', '').split('\t')
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
        if resid == '' and rawdict['Order Number'] != '':
            # If Sample ID is void, we will use the OrderNumber as a reference.
            resid = rawdict['Order Number']
        elif resid == '' and rawdict['Order Number'] == '':
            # If there isn't Sample ID or Order Number
            self.err("Result identification not found.", numline=self._numline)
            return -1
        testname = rawdict['Test']
        if testname == '':
            # None test name found
            self.err("Result test name not found.", numline=self._numline)
            return -1
        del rawdict['Test']

        # Building the new dict
        rawdict['DefaultResult'] = 'Result'
        rawdict['Remarks'] = ''.join([rawdict['Result'], " on Order Number.", resid]) \
            if rawdict['Result'] == "Target Not Detected" else ''
        rawdict['DateTime'] = self.csvDate2BikaDate(rawdict['Accepted Date/Time'])
        self._addRawResult(resid, {testname: rawdict}, False)
        return 0

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        Date, Time = DateTime.split(' ')
        dtobj = datetime.strptime(Date + ' ' + Time, "%Y/%m/%d %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")


class RocheCobasTaqmanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
