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

""" Shimadzu's 'GCMS QP2010 SE'
"""
from bika.lims import bikaMessageFactory as _
from datetime import datetime
import json
import re
from bika.lims.exportimport.instruments.resultsimport import \
        InstrumentCSVResultsFileParser, AnalysisResultsImporter
import traceback

title = "Shimadzu - GCMS-QP2010 SE"


def Import(context, request):
    """ Read Shimadzu GCMS-TQ8030 GC/MS/MS analysis results
    """
    form = request.form
    # TODO form['file'] sometimes returns a list
    infile = form['instrument_results_file'][0] if \
        isinstance(form['instrument_results_file'], list) \
        else form['instrument_results_file']
    override = form['results_override']
    artoapply = form['artoapply']
    instrument = form.get('instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    parser = GCMSQP2010SECSVParser(infile)

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

        importer = GCMSQP2010SEImporter(parser=parser,
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


class GCMSQP2010SECSVParser(InstrumentCSVResultsFileParser):

    HEADERTABLE_KEY = '[Header]'
    HEADERKEY_FILENAME = 'Data File Name'
    HEADERKEY_OUTPUTDATE = 'Output Date'
    HEADERKEY_OUTPUTTIME = 'Output Time'
    QUANTITATIONRESULTS_KEY = '[MS Quantitative Results]'
    QUANTITATIONRESULTS_NUMBEROFIDS = '# of IDs'
    QUANTITATIONRESULTS_HEADER_ID_NUMBER = 'ID#'
    QUANTITATIONRESULTS_NUMERICHEADERS = ('Mass', 'Height' 'Conc.',
                                          'Std.Ret.Time', '3rd', '2nd', '1st',
                                          'Constant', 'Ref.Ion Area',
                                          'Ref.Ion Height',
                                          'Ref.Ion Set Ratio',
                                          'Ref.Ion Ratio', 'Recovery',
                                          'SI', 'Ref.Ion1 m/z',
                                          'Ref.Ion1 Area', 'Ref.Ion1 Height',
                                          'Ref.Ion1 Set Ratio',
                                          'Ref.Ion1 Ratio', 'Ref.Ion2 m/z',
                                          'Ref.Ion2 Area', 'Ref.Ion2 Height',
                                          'Ref.Ion2 Set Ratio',
                                          'Ref.Ion2 Ratio', 'Ref.Ion3 m/z',
                                          'Ref.Ion3 Area', 'Ref.Ion3 Height',
                                          'Ref.Ion3 Set Ratio',
                                          'Ref.Ion3 Ratio',
                                          'Ref.Ion4 m/z', 'Ref.Ion4 Area',
                                          'Ref.Ion4 Height',
                                          'Ref.Ion4 Set Ratio',
                                          'Ref.Ion4 Ratio', 'Ref.Ion5 m/z',
                                          'Ref.Ion5 Area', 'Ref.Ion5 Height',
                                          'Ref.Ion5 Set Ratio',
                                          'Ref.Ion5 Ratio', 'S/N', 'Threshold',
                                          )
    SIMILARITYSEARCHRESULTS_KEY = \
        '[MS Similarity Search Results for Identified Results]'
    PEAK_TABLE_KEY = '[MC Peak Table]'
    COMMAS = ','

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._quantitationresultsheader = []
        self._numline = 0

    def _parseline(self, line):
        if self._end_header is False:
            return self.parse_headerline(line)
        else:
            return self.parse_quantitationesultsline(line)

    def parse_headerline(self, line):
        """ Parses header lines

            Header example:
            [Header]
            Data File Name,C:\GCMSsolution\Data\October\
                    1-16-02249-001_CD_10172016_2.qgd
            Output Date,10/18/2016
            Output Time,12:04:11 PM
        """
        if self._end_header is True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split('\t')]

        # [Header]
        if splitted[0] == self.HEADERTABLE_KEY:
            if self.HEADERTABLE_KEY in self._header:
                self.warn("Header [Header] Info already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            self._header[self.HEADERTABLE_KEY] = []
            for i in range(len(splitted) - 1):
                if splitted[i + 1]:
                    self._header[self.HEADERTABLE_KEY].append(splitted[i + 1])

        # Data File Name, C:\GCMSsolution\Data\October\
        # 1-16-02249-001_CD_10172016_2.qgd
        elif splitted[0] == self.HEADERKEY_FILENAME:
            if self.HEADERKEY_FILENAME in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_FILENAME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Output Date	10/18/2016
        elif splitted[0] == self.HEADERKEY_OUTPUTDATE:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%m/%d/%Y")
                    self._header[self.HEADERKEY_OUTPUTDATE] = d
                except ValueError:
                    self.err("Invalid Output Date format",
                             numline=self._numline, line=line)
            else:
                self.warn("Output Date not found or empty",
                          numline=self._numline, line=line)
                d = datetime.strptime(splitted[1], "%m/%d/%Y")

        # Output Time	12:04:11 PM
        elif splitted[0] == self.HEADERKEY_OUTPUTTIME:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%I:%M:%S %p")
                    self._header[self.HEADERKEY_OUTPUTTIME] = d
                except ValueError:
                    self.err("Invalid Output Time format",
                             numline=self._numline, line=line)
            else:
                self.warn("Output Time not found or empty",
                          numline=self._numline, line=line)
                d = datetime.strptime(splitted[1], "%I:%M %p")

        if line.startswith(self.QUANTITATIONRESULTS_KEY):
            self._end_header = True
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1
            return 0

        return 0

    def parse_quantitationesultsline(self, line):
        """ Parses quantitation result lines
            Please see samples/GC-MS output.txt
            [MS Quantitative Results] section
        """

        # [MS Quantitative Results]
        if line.startswith(self.QUANTITATIONRESULTS_KEY) \
                or line.startswith(self.QUANTITATIONRESULTS_NUMBEROFIDS) \
                or line.startswith(self.SIMILARITYSEARCHRESULTS_KEY) \
                or line.startswith(self.PEAK_TABLE_KEY):

            # Nothing to do, continue
            return 0

        # # of IDs \t23
        if line.startswith(self.QUANTITATIONRESULTS_HEADER_ID_NUMBER):
            self._quantitationresultsheader = [token.strip() for token
                                               in line.split('\t')
                                               if token.strip()]
            return 0

        # 1 \talpha-Pinene \tTarget \t0 \t93.00 \t7.738 \t7.680 \t7.795 \t2.480
        # \t344488 \t138926 \t0.02604 \tAuto \t2	\t7.812	\tLinear \t0 \t0
        # \t4.44061e+008	\t278569 \t0 \t0 \t38.94 \t38.58 \t0.00	\t98 \t92.00
        # \t0 \t0 \t38.94 \t38.58 \t91.00 \t0 \t0 \t38.93 \t40.02 \t0 \t0 \t0
        # \t0 \t0 \t0 \t0 #\t0 \t0 \t0 \t0 \t0 \t0 \t0 \t0 \t75.27 \tmg \t0.000
        splitted = [token.strip() for token in line.split('\t')]
        ar_id = self._header['Data File Name'].split('\\')[-1].split('.')[0]
        quantitation = {'DefaultResult': 'Conc.', 'AR': ar_id}
        for colname in self._quantitationresultsheader:
            quantitation[colname] = ''

        for i in range(len(splitted)):
            token = splitted[i]
            if i < len(self._quantitationresultsheader):
                colname = self._quantitationresultsheader[i]
                if colname in self.QUANTITATIONRESULTS_NUMERICHEADERS:
                    try:
                        quantitation[colname] = float(token)
                    except ValueError:
                        self.warn(
                            "No valid number ${token} in column "
                            "${index} (${column_name})",
                            mapping={"token": token,
                                     "index": str(i + 1),
                                     "column_name": colname},
                            numline=self._numline, line=line)
                        quantitation[colname] = token
                else:
                    quantitation[colname] = token

                # val = re.sub(r"\W", "", splitted[1])
                # self._addRawResult(quantitation['AR'],
                #                   values={val:quantitation},
                #                   override=False)
            elif token:
                self.err("Orphan value in column ${index} (${token})",
                         mapping={"index": str(i+1),
                                  "token": token},
                         numline=self._numline, line=line)

        result = quantitation[quantitation['DefaultResult']]
        column_name = quantitation['DefaultResult']
        result = self.zeroValueDefaultInstrumentResults(column_name,
                                                        result, line)
        quantitation[quantitation['DefaultResult']] = result

        val = re.sub(r"\W", "", splitted[1])
        self._addRawResult(quantitation['AR'],
                           values={val: quantitation},
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


class GCMSQP2010SEImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=''):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
