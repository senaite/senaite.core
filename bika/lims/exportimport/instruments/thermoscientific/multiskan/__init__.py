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

""" Thermo Scientific Multiskan GO
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class ThermoScientificMultiskanCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv, analysiskey):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._labels = False  # If true, we are in a line where are the sample names
        self._data = False  # If true, we are in a line where are the analysis results
        self._labels_values = {}  # The labels' values
        self.analysiskey = analysiskey  # The analysis key whose results will be related

    def _parseline(self, line):
        sline = line.split(';')
        if sline[0] == 'Sample':
            self._labels = True
            self._data = False
        elif sline[0] == 'Abs':
            self._labels = False
            self._data = True
        elif self._labels:
            self.parse_label(sline)
        elif self._data:
            self.parse_data(sline)
        return 0

    def parse_label(self, sline):
        """It saves the labels inside a dictionary with the follow format:
        {
        'A':['label1', 'label2', 'label3', ...],
        'B':[...]
        }
        :param sline: a list with the labels line parsed as ['A','label1','label2',...]
        """
        if sline[0] == '':
            return 0
        self._labels_values[sline[0]] = sline[1:]
        return 0

    def parse_data(self, sline):
        """This function builds the addRawResults dictionary using the header values of the labels section
        as sample Ids.
        """
        if sline[0] == '':
            return 0
        for idx, label in enumerate(self._labels_values[sline[0]]):
            if label != '':
                self._addRawResult(label.split(' ')[0], {self.analysiskey: sline[1:][idx]}, False)
        return 0


class ThermoScientificMultiskanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
