""" Thermo Scientific 'Arena'
"""

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class ThermoArenaRPRCSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []

    def _parseline(self, line):
        # Process the line differently if it pertains at header or results block
        if self._end_header == False:
            sline = line.strip(',')
            return self.parse_headerline(sline)
        else:
            return self.parse_resultline(line)

    def parse_header(self,sline):
        return 0
    def parse_resultline(line):
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
