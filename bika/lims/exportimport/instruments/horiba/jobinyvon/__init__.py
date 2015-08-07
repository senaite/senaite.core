#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" HoribaJobinYvon
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class HoribaJobinYvonCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []  # The different columns names
        self._linedata = {}  # The line with the data
        self._resid = ''
        self._method = ''
        self._date = ''

    def _parseline(self, line):
        # Net intensity  has commas, but is a unique value
        if '"' in line:
            line_before, net_intensity, line_after = line.split('"')
            net_intensity = net_intensity.replace(',', '/')
            line = line_before + net_intensity + line_after
        # The spreadsheet creates a column for the measurement units, but is not needed anymore
        line = line.replace(',mg/l,', '')

        sline = line.split(',')
        if len(sline) > 0 and sline[0] == 'Sample:':
            # This line contains the resid (sample) and the date.
            for idx, e in enumerate(sline):
                if e == 'Sample:':
                    self._resid = sline[idx+1]
                elif e == 'Method:':
                    self._method = sline[idx+1]
                elif e == 'Measured:':
                    self._date = self.csvDate2BikaDate(sline[idx+1])
            return 1
        elif len(sline) > 0 and sline[0] == 'LineName':
            self._columns = sline
            return 0
        elif len(sline) > 0 and sline[0] != '':
            self.parse_data_line(sline)

    def parse_data_line(self, sline):
        """
        Parses the data line and builds the dictionary.
        :param sline: a split data line to parse
        :return: the number of rows to jump and parse the next data line or return the code error -1
        """
        values = {'Remarks': ''}
        name = ''
        test_line = ''
        for idx, result in enumerate(sline):
            if self._columns[idx] == 'LineName':
                # It's the analysis name
                name = result.split(' ')[0]
                test_line = result.split(' ')[1]
            elif self._columns[idx] == 'Cc':
                values['Concentration'] = sline[idx+2]
            elif self._columns[idx] == 'SD':
                values['StandardDeviation'] = sline[idx+2]
            elif self._columns[idx] == 'RSD':
                values['ResidualError'] = sline[idx+2]
            elif self._columns[idx] == 'Net_Intensity':
                values['NetIntensity'] = result.split('/')

        values['DefaultResult'] = 'Concentration'
        values['DateTime'] = self._date
        values['Method'] = self._method
        values['TestLine'] = test_line
        self._addRawResult(self._resid, {name: values}, False)
        return 0

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M%S
        dtobj = datetime.strptime(DateTime, "%d.%m.%Y %H:%M")
        return dtobj.strftime("%Y%m%d %H:%M")


class HoribaJobinYvonImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
