#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" HoribaJobinYvon
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser

import csv
import re


class HoribaJobinYvonCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csvfile):
        InstrumentCSVResultsFileParser.__init__(self, csvfile)
        self._infile = csvfile
        self.headers = []  # The different columns names
        self._linedata = {}  # The line with the data
        self._resid = ''
        self._method = ''
        self._date = ''

    def _parseline(self, line):
        # skip these lines
        if line.startswith(',') or line.startswith('Print Date'):
            return 0
        # This line contains the resid (sample) and the date.
        elif line.startswith('Sample'):
            self.parse_sample_line(line)
            return 0
        # Contains header for a block of sample results
        elif line.startswith('LineName'):
            self.parse_line_headers(line)
        else:
            self.parse_data_line(line)

    def parse_sample_line(self, line):
        sline = line.split(',')
        for idx, e in enumerate(sline):
            if e == 'Sample:':
                self._resid = sline[idx + 1]
            elif e == 'Method:':
                self._method = sline[idx + 1]
            elif e == 'Measured:':
                self._date = self.csvDate2BikaDate(sline[idx + 1])
            return 0

    def parse_line_headers(self, line):
        """We must build headers carefully: there are multiple blank values
        in the header row, and the instrument may just add more for all
        we know.
        """
        headers = line.split(",")
        for i, v in enumerate(headers):
            if v:
                headers[i] = v
            else:
                headers[i] = str(i)
        self.headers = headers

    def _generate(self, string):
        """To emulate an iterator that csv.reader can request a line from
        """
        yield string

    def parse_data_line(self, line):
            """ Parses the data line into a dictionary for the importer
            """
            it = self._generate(line)
            reader = csv.DictReader(it, fieldnames=self.headers)
            values = reader.next()
            values['DefaultResult'] = 'ResidualError'
            values['LineName'] = re.sub(r'\W', '', values['LineName'].strip())
            values['Concentration'] = values['Cc'].strip()
            values['StandardDeviation'] = values['SD'].strip()
            values['ResidualError'] = values['RSD'].strip()
            values['NetIntensity'] = values['Net_Intensity'].strip().split('/')
            values['Remarks'] = ''
            values['TestLine'] = ''
            self._addRawResult(self._resid, {values['LineName']: values}, False)
            return 0

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M%S
        dtobj = datetime.strptime(DateTime, "%d.%m.%Y %H:%M")
        return dtobj.strftime("%Y%m%d %H:%M")
