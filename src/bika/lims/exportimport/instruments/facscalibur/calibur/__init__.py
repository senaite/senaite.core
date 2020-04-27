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

""" Facs Calibur
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class FacsCaliburCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []  # The different columns names
        self._values = {}  # The analysis services from the same resid
        self._rownum = None
        self._end_header = False
        # self._includedcolumns =['Ca', 'Cu',
        #                         'Fe', 'Mg']
        self._includedcolumns = ['CD4_PERC', 'CD4',
                                  'CD8_PERC', 'CD8']

    def _parseline(self, line):
        sline = line.split(',')
        if len(sline) > 0 and not self._end_header:
            self._columns = sline
            for column in self._columns:
                self._columns = column.split('\t')
            #print(self._columns)
            self._end_header = True

            for i, j in enumerate(self._columns):
                if j.startswith('(Average)'):
                    j = j[len('(Average)')+1::]
                    self._columns[i] = j
                if 'CD3+CD4+ %Lymph' in self._columns:
                    self._columns[i] = 'CD4_PERC'
                elif 'CD3+CD4+ Abs Cnt' in self._columns:
                    self._columns[i] = 'CD4'
                elif 'CD3+CD8+ %Lymph' in self._columns:
                    self._columns[i] = 'CD8_PERC'
                elif 'CD3+CD8+ Abs Cnt' in self._columns:
                    self._columns[i] = 'CD8'
            return 0
        elif sline > 0 and self._end_header:
            self.parse_data_line(sline)
        else:
            self.err("Unexpected data format", numline=self._numline)
            return -1


    def parse_data_line(self, sline):
        """
        Parse the data line. If an AS was selected it can distinguish between data rows and information rows.
        :param sline: a split data line to parse
        :returns: the number of rows to jump and parse the next data line or return the code error -1
        """

        temp_line = sline
        sline_ = ''.join(temp_line)
        sline_ = sline_.split('\t')
        headerdict = {}
        datadict = {}
        for idx, result in enumerate(sline_):
            if self._columns[idx] in self._includedcolumns:
                datadict[self._columns[idx]] = {'Result': result, 'DefaultResult': 'Result'}
            else:
                headerdict[self._columns[idx]] = result
        resid = headerdict['Sample ID']
        print(datadict)
        self._addRawResult(resid, datadict, False)
        self._header = headerdict
        return 0


class FacsCaliburImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
