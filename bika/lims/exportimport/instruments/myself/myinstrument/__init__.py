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
