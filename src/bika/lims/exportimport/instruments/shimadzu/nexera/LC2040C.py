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

""" Shimadzu HPLC-PDA Nexera-I LC2040C
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
        InstrumentCSVResultsFileParser, AnalysisResultsImporter
from datetime import datetime
import json
import traceback

title = "Shimadzu HPLC-PDA Nexera-I LC2040C"


def Import(context, request):
    """ Read Shimadzu HPLC-PDA Nexera-I LC2040C analysis results
    """
    form = request.form
    infile = form['instrument_results_file'][0] if \
        isinstance(form['instrument_results_file'], list) else \
        form['instrument_results_file']
    artoapply = form['artoapply']
    override = form['results_override']
    instrument = form.get('instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    parser = TSVParser(infile)

    if parser:
        # Load the importer
        status = ['sample_received', 'attachment_due', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'attachment_due', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        importer = LC2040C_Importer(parser=parser,
                                    context=context,
                                    allowed_ar_states=status,
                                    allowed_analysis_states=None,
                                    override=over,
                                    instrument_uid=instrument)
        tbex = ''
        try:
            importer.process()
        except:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


class TSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._currentresultsheader = []
        self._currentanalysiskw = ''
        self._numline = 0

    def _parseline(self, line):
        return self.parse_TSVline(line)

    def parse_TSVline(self, line):
        """ Parses result lines
        """

        split_row = [token.strip() for token in line.split('\t')]
        _results = {'DefaultResult': 'Conc.'}

        # ID# 1
        if split_row[0] == 'ID#':
            return 0
        # Name	CBDV - cannabidivarin
        elif split_row[0] == 'Name':
            if split_row[1]:
                self._currentanalysiskw = split_row[1]
                return 0
            else:
                self.warn("Analysis Keyword not found or empty",
                          numline=self._numline, line=line)
        # Data Filename	Sample Name	Sample ID	Sample Type	Level#
        elif 'Sample ID' in split_row:
            split_row.insert(0, '#')
            self._currentresultsheader = split_row
            return 0
        # 1	QC PREP A_QC PREP A_009.lcd	QC PREP
        elif split_row[0].isdigit():
            _results.update(dict(zip(self._currentresultsheader, split_row)))

            # 10/17/2016 7:55:06 PM
            try:
                da = datetime.strptime(
                    _results['Date Acquired'], "%m/%d/%Y %I:%M:%S %p")
                self._header['Output Date'] = da
                self._header['Output Time'] = da
            except ValueError:
                self.err("Invalid Output Time format",
                         numline=self._numline, line=line)

            result = _results[_results['DefaultResult']]
            column_name = _results['DefaultResult']
            result = self.zeroValueDefaultInstrumentResults(
                                                    column_name, result, line)
            _results[_results['DefaultResult']] = result

            self._addRawResult(_results['Sample ID'],
                               values={self._currentanalysiskw: _results},
                               override=False)

    def zeroValueDefaultInstrumentResults(self, column_name, result, line):
        result = str(result)
        if result.startswith('--') or result == '' or result == 'ND':
            return 0.0

        try:
            result = float(result)
            if result < 0.0:
                result = 0.0
        except ValueError:
            self.err(
                "No valid number ${result} in column (${column_name})",
                mapping={"result": result,
                         "column_name": column_name},
                numline=self._numline, line=line)
            return
        return result


class LC2040C_Importer(AnalysisResultsImporter):

    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=''):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
