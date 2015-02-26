""" Thermo Scientific 'Arena'
"""
from datetime import datetime
from bika.lims import logger
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class ThermoArenaRPRCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []
        self._period = [False,''] # Variable to control results from period beginning and end.

    def _parseline(self, line):
        # Process the line differently if it pertains at header or results block
        if not self._end_header:
            return self.parse_headerline(line)
        else:
            return self.parse_resultline(line)

    def parse_headerline(self, line):

        if line.startswith('Arena'):
            self._header['ARId'] = line.strip(',')
            return 0

        elif line.startswith('Results from time'):
            self._period = [True, line.strip(',')]
            return 0

        elif line.startswith('Sample Id'):
            if self._period[0]:  # If there is a period, we should save it
                self._period[0] = False
                self._header[self._period[1]] = self._period[2:]

            self._end_header = True
            self._columns = line.split(',')

        elif self._period[0]:  # Is a date
            date = self.csvDate2BikaDate(line.strip(','))
            self._period.append(date)
            return 0

        else:
            self.err('Unexpected header format', numline=self._numline)
            return -1

    def parse_resultline(self, line):
        sline = line.split(',')
        if not sline:
            return 0

        rawdict = {}
        for idx, result in enumerate(sline):
            if len(self._columns) <= idx:
                self.err("Orphan value in column ${index}",
                         mapping={"index":str(idx + 1)},
                         numline=self._numline)
                break
            rawdict[self._columns[idx]] = result

        acode = rawdict.get('Test short name', '')
        if not acode:
            self.err("No Analysis Code defined",
                     numline=self._numline)
            return 0

        rid = rawdict.get('Sample Id', '')
        del(rawdict['Sample Id'])
        if not rid:
            self.err("No Sample ID defined",
                     numline=self._numline)
            return 0

        errors = rawdict.get('Errors', '')
        errors = "Errors: %s" % errors if errors else ''
        notes = rawdict.get('Notes', '')
        notes = "Notes: %s" % notes if notes else ''
        rawdict['DefaultResult'] = 'Result'
        rawdict['Remarks'] = ' '.join([errors, notes])
        raw = {}
        raw[acode] = rawdict
        self._addRawResult(rid, raw, False)
        return 0

    def csvDate2BikaDate(self,DateTime):
        #11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        try:
            dtobj = datetime.strptime(DateTime, "%a %b %d %H:%M:%S %Y")
            return dtobj.strftime("%Y%m%d %H:%M:%S")
        except ValueError:
            warn = "No date format known."
            logger.warning(warn)
            return DateTime


class ThermoArenaImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
                 AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
