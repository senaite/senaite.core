""" Thermo Scientific 'Arena'
"""

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
            self._header['Instrument'] = line.strip(',')
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
            self._period.append(line.strip(','))
            return 0

        else:
            self.err('Unexpected header format', numline=self._numline)
            return -1

    def parse_resultline(self, line):
        sline = line.split(',')
        return 0


class ThermoArenaImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
                 AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
