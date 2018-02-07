# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Agilent's 'Masshunter'
"""
from bika.lims import bikaMessageFactory as _
from datetime import datetime
import json
import re
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
import traceback

title = "Agilent - Masshunter"


def Import(context, request):
    """ Read Agilent Masshunter analysis results
    """
    form = request.form
    # TODO form['file'] sometimes returns a list
    infile = form['instrument_results_file'][0] if isinstance(
            form['instrument_results_file'], list) else \
        form['instrument_results_file']
    artoapply = form['artoapply']
    override = form['results_override']
    sample = form.get('sample', 'requestid')
    instrument = form.get('instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    parser = AgilentMasshunterParser(infile)

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

        sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getRequestID']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = AgilentMasshunterImporter(parser=parser,
                                             context=context,
                                             idsearchcriteria=sam,
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


class AgilentMasshunterParser(InstrumentCSVResultsFileParser):

    HEADERKEY_ANALYSISTIME = 'Analysis Time'
    HEADERKEY_ANALYSTNAME = 'Analyst Name'
    HEADERKEY_BATCHDATAPATH = 'Batch Data Path'
    HEADERKEY_BATCHNAME = 'Batch Name'
    HEADERKEY_BATCHSTATE = 'Batch State'
    HEADERKEY_LASTCALIBRATION = 'Calibration Last Updated Time'
    HEADERKEY_REPORTGENERATIONTIME = 'Report Generation Time'
    HEADERKEY_REPORTGENERATORNAME = 'Report Generator Name'
    HEADERKEY_REPORTRESULTSDATAPATH = 'Report Results Data Path'
    HEADERKEY_SCHEMAVERSION = 'SchemaVersion'
    HEADERKEY_QUANTBATCHVERSION = 'Quant Batch Version'
    HEADERKEY_QUANTREPORTVERSION = 'Quant Report Version'

    QUANTITATIONRESULTS_NUMERICHEADERS = ('CalculatedConcentration',
                                          'FinalConcentration',
                                          'FinalConcentration')
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

            Analysis Time	7/13/2017 9:55
            Analyst Name	MassHunter01\Agilent
            Batch Data Path	D:\MassHunter\GCMS\Terpenes\2017\July\20170711\
                    QuantResults\20170711 Sample Workup
            Batch Name	20170711 Sample Workup
            Batch State	Processed
            Calibration Last Updated Time	6/29/2017 15:57
            Report Generation Time	1/1/0001 12:00:00 AM
            Report Generator Name	None
            Report Results Data Path	None
            SchemaVersion	65586
            Quant Batch Version	B.08.00
            Quant Report Version	B.08.00
        """
        if self._end_header is True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split(self.COMMAS)]

        # Analysis Time	7/13/2017 9:55
        if splitted[0] == self.HEADERKEY_ANALYSISTIME:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%m/%d/%Y %H:%M")
                    self._header[self.HEADERKEY_ANALYSISTIME] = d
                except ValueError:
                    self.err("Invalid Output Time format",
                             numline=self._numline, line=line)
            else:
                self.warn("Output Time not found or empty",
                          numline=self._numline, line=line)
                d = datetime.strptime(splitted[1], "%I:%M %p")

        # Analyst Name	MassHunter01\Agilent
        elif splitted[0] == self.HEADERKEY_ANALYSTNAME:
            if self.HEADERKEY_ANALYSTNAME in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_ANALYSTNAME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Batch Data Path
        # D:\MassHunter\GCMS\Terpenes\2017\July\20170711\QuantResults\20170711
        elif splitted[0] == self.HEADERKEY_BATCHDATAPATH:
            if self.HEADERKEY_BATCHDATAPATH in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_BATCHDATAPATH] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Batch Name	20170711 Sample Workup
        elif splitted[0] == self.HEADERKEY_BATCHNAME:
            if self.HEADERKEY_BATCHNAME in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_BATCHNAME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Batch State	Processed
        elif splitted[0] == self.HEADERKEY_BATCHSTATE:
            if self.HEADERKEY_BATCHSTATE in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_BATCHNAME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Calibration Last Updated Time	6/29/2017 15:57
        elif splitted[0] == self.HEADERKEY_LASTCALIBRATION:
            if self.HEADERKEY_LASTCALIBRATION in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_LASTCALIBRATION] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Report Generation Time	1/1/0001 12:00:00 AM
        elif splitted[0] == self.HEADERKEY_REPORTGENERATIONTIME:
            if self.HEADERKEY_REPORTGENERATIONTIME in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_REPORTGENERATIONTIME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Report Generator Name	None
        elif splitted[0] == self.HEADERKEY_REPORTGENERATORNAME:
            if self.HEADERKEY_REPORTGENERATORNAME in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_REPORTGENERATORNAME] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Report Results Data Path	None
        elif splitted[0] == self.HEADERKEY_REPORTRESULTSDATAPATH:
            if self.HEADERKEY_REPORTRESULTSDATAPATH in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_REPORTRESULTSDATAPATH] = \
                    splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # SchemaVersion	65586
        elif splitted[0] == self.HEADERKEY_SCHEMAVERSION:
            if self.HEADERKEY_SCHEMAVERSION in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_SCHEMAVERSION] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Quant Batch Version	B.08.00
        elif splitted[0] == self.HEADERKEY_QUANTBATCHVERSION:
            if self.HEADERKEY_QUANTBATCHVERSION in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_QUANTBATCHVERSION] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Quant Report Version	B.08.00
        elif splitted[0] == self.HEADERKEY_QUANTREPORTVERSION:
            if self.HEADERKEY_QUANTREPORTVERSION in self._header:
                self.warn("Header File Data Name already found. Discarding",
                          numline=self._numline, line=line)
                return 0

            if splitted[1]:
                self._header[self.HEADERKEY_QUANTREPORTVERSION] = splitted[1]
            else:
                self.warn("File Data Name not found or empty",
                          numline=self._numline, line=line)

        # Blank lines
        if splitted[0] == '':
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

        if line == ',,,,,,,,,,,,,,,,,,':
            return 0

        if line.startswith('SampleID'):
            self._end_header = True
            self._quantitationresultsheader = [token.strip() for token
                                               in line.split(self.COMMAS)
                                               if token.strip()]
            return 0

        splitted = [token.strip() for token in line.split(self.COMMAS)]
        quantitation = {'DefaultResult': 'FinalConcentration'}
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

        d = datetime.strptime(quantitation['AcqDateTime'], "%m/%d/%Y %H:%M")
        quantitation['AcqDateTime'] = d
        val = re.sub(r"\W", "", quantitation['Compound'])
        self._addRawResult(quantitation['DataFileName'],
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


class AgilentMasshunterImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=''):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria,
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
