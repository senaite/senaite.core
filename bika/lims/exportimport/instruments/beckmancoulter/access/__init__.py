#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Beckman Couter Access
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class BeckmancoulterAccessCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = {} #The diferents data columns names
        self._linedata = {}#The line with the data
        self._rownum = None
        self._isFirst = True #Used to know if is the first linedata



class BeckmancoulterAccessImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
