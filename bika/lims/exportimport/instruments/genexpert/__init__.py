# This file is part of Bika LIMS
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" GenExpert
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class GenExpertParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, csv)

    def _parseline(self, line):
        return 0


class GenExpertImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
