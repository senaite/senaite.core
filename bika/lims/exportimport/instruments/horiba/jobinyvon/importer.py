#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" HoribaJobinYvon
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter


class HoribaJobinYvonImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
