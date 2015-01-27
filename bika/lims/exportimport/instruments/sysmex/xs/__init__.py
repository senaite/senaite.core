"""Sysmex XS 500i
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class SysmexXSCSVParser(InstrumentCSVResultsFileParser):

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
        return 0
    def parse_resultline(self, line):
        return 0

class SysmexXSImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
                 AnalysisResultsImporter.__init__(self, parser, context,
                                                  idsearchcriteria, override,
                                                  allowed_ar_states,
                                                  allowed_analysis_states,
                                                  instrument_uid)
