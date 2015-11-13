""" FOSS 'Winescan'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter


class WinescanCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self.currentheader = None

    def _parseline(self, line):
        # Sample Id,,,Ash,Ca,Ethanol,ReducingSugar,VolatileAcid,TotalAcid
        # Sometimes it is: Id,,,Ash,Ca,Ethanol,ReducingSugar,VolatileAcid,TotalAcid
        if line.startswith('Sample Id') or line.startswith('ID'):
            self.currentheader = [token.strip() for token in line.split(',')]
            return 0

        if self.currentheader:
            # AR-01177-01,,,0.9905,22.31,14.11,2.95,0.25,5.11,3.54,3.26,-0.36
            splitted = [token.strip() for token in line.split(',')]
            resid = splitted[0]
            if not resid:
                self.err("No Sample ID found", numline=self.num_line)
                self.currentHeader = None
                return 0

            duplicated = []
            values = {}
            remarks = ''
            for idx, result in enumerate(splitted):
                if idx == 0:
                    continue

                if len(self.currentheader) <= idx:
                    self.err("Orphan value in column ${index}, line ${line_nr}",
                             mapping={"index": str(idx + 1),
                                      "line_nr": self._numline})
                    continue

                keyword = self.currentheader[idx]

                if not result and not keyword:
                    continue

                if result and not keyword:
                    self.err("Orphan value in column ${index}, line ${line_nr}",
                             mapping={"index": str(idx + 1),
                                      "line_nr": self._numline})
                    continue

                # Allow Bika to manage the Remark as an analysis Remark instead
                # of a regular result. Remarks field will be set for all
                # Analysis keywords.
                if keyword == 'Remark':
                    remarks = result
                    continue

                if not result:
                    self.warn("Empty result for ${analysis_keyword}, column ${index}",
                              mapping={"analysis_keyword": keyword,
                                       "index": str(idx + 1)},
                              numline=self._numline)

                if keyword in values.keys():
                    self.err("Duplicated result for ${analysis_keyword}",
                              mapping={"analysis_keyword": keyword},
                    numline=self._numline)
                    duplicated.append(keyword)
                    continue

                values[keyword] = {'DefaultResult': keyword,
                                   'Remarks': remarks,
                                   keyword: result}

            # Remove duplicated results
            outvals = dict([(key, value) for key, value in values.items() \
                       if key not in duplicated])

            # add result
            self._addRawResult(resid, outvals, True)
            self.currentHeader = None
            return 0

        self.err("No header found")
        return 0


class WinescanImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None, instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
