# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.exportimport.instruments.resultsimport import InstrumentCSVResultsFileParser
from bika.lims.exportimport.instruments.instrument import GenericImport, getResultsInputFile

title = "My Instrument"

class MyInstrumentCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)

    def _parseline(self, line):
        if not line.startswith("SampleID"):
            sline = self.splitLine(line)
            raw = {sline[1]: {'DefaultResult': 'result',
                              'result': sline[2],
                              'DateTime': sline[3]}}
            self._addRawResult(sline[0], raw)
            return 0

def Import(context, request):
    infile = getResultsInputFile(request)
    parser = MyInstrumentCSVParser(infile)
    res = GenericImport(context, request, parser)
    return res
