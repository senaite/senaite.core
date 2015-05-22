#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Thermo Scientific Multiskan GO
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class ThermoScientificMultiskanCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []  # The different columns names
        self._linedata = {}  # The line with the data
        self._rownum = None
        self._end_header = False

    def _parseline(self, line):


    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        Date, Time, locale = DateTime.replace('.', '').split(' ')
        dtobj = datetime.strptime(Date + ' ' + Time + ' ' + locale, "%d/%m/%Y %H:%M %p")
        return dtobj.strftime("%Y%m%d %H:%M")


class ThermoScientificMultiskanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
