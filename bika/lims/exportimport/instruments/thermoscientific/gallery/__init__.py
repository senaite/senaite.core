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

""" Thermo Scientific 'Gallery'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class ThermoGalleryTSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, tsv):
        InstrumentCSVResultsFileParser.__init__(self, tsv)
        self._end_header = False
        self._columns = []

    def _parseline(self, line):
        sline = line.replace('"', '').strip()
        if self._end_header == False:
            return self.parse_headerline(sline)
        else:
            return self.parse_resultline(sline)

    def splitLine(self, line):
        return [token.strip() for token in line.split('\t')]

    def parse_headerline(self, line):
        """ Parses header lines

            Header example:
            Date    2012/11/15    User    anonymous
            Time    06:07:08PM    Software version: 4.0

            Example laboratory
            Arizona
        """
        if line.startswith('Date'):
            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Date'] = splitted[1]
                if len(splitted) > 2 and splitted[2] == 'User':
                    self._header['Date'] = splitted[1]
                    self._header['User'] = splitted[3] \
                        if len(splitted) > 3 else ''
                else:
                    self.warn("Unexpected header format", numline=self._numline)
            else:
                self.warn("Unexpected header format", numline=self._numline)

            return 0

        if line.startswith('Time'):
            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1]
            else:
                self.warn("Unexpected header format", numline=self._numline)

            return 0

        if line.startswith('Sample/ctrl'):
            # Sample/ctrl ID    Pat/Ctr/cAl    Test name    Test type
            if len(self._header) == 0:
                self.warn("No header found", numline=self._numline)
                return -1

            #Grab column names
            self._end_header = True
            self._columns = self.splitLine(line)
            return 1

    def parse_resultline(self, line):
        # Sample/ctrl ID    Pat/Ctr/cAl    Test name    Test type
        if not line.strip():
            return 0

        rawdict = {}
        splitted = self.splitLine(line)
        for idx, result in enumerate(splitted):
            if len(self._columns) <= idx:
                self.err("Orphan value in column ${index}",
                         mapping={"index":str(idx + 1)},
                         numline=self._numline)
                break
            rawdict[self._columns[idx]] = result

        acode = rawdict.get('Test name', '')
        if not acode:
            self.err("No Analysis Code defined",
                     numline=self._numline)
            return 0

        rid = rawdict.get('Sample/ctrl ID')
        if not rid:
            self.err("No Sample ID defined",
                     numline=self._numline)
            return 0

        errors = rawdict.get('Errors', '')
        errors = "Errors: %s" % errors if errors else ''
        notes = rawdict.get('Notes', '')
        notes = "Notes: %s" % notes if notes else ''
        rawdict[acode]=rawdict['Result']
        rawdict['DefaultResult'] = acode
        rawdict['Remarks'] = ' '.join([errors, notes])
        rawres = self.getRawResults().get(rid, [])
        raw = rawres[0] if len(rawres) > 0 else {}
        raw[acode] = rawdict
        self._addRawResult(rid, raw, True)
        return 0

class ThermoGalleryImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
