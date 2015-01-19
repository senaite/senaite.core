""" Biodrop
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
from datetime import datetime

class BioDropCSVParser(InstrumentCSVResultsFileParser):
    """

    currently requires services with keyword RNA and/or DNA to exist.

    possible interim field keywords in DNA/RNA calculation:
        A230, A260, A280, A320, A260/A230, A260/A280,
        Concentration, DilutionFactor
    """
    def __init__(self, csv, analysiskey):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self.data_header = None
        self.file_header = {}
        # Set this flag when we find the header-line beginning with "Date,".
        # Once this flag is set, all following lines are real data.
        self.main_data_found = False
        self.analysiskey = analysiskey

    def _parseline(self, line):
        if self.main_data_found:
            this_row = line.split(",")
            # if less values are found than headers, it's an error
            if len(this_row) != len(self.data_header):
                self.err("Data row number " + item_nr + " has the wrong number of items")
                return 0
            row_values = dict(zip(self.data_header, this_row))

            raw_result = {}
            for d in (row_values, self.file_header):
                raw_result.update(d)
            raw_result['DefaultResult'] = 'Concentration'
            raw_result = {self.analysiskey: raw_result};

            sample_id = row_values['Sample Name']
            self._addRawResult(sample_id, raw_result)

        elif line.startswith('Date,'):
            self.data_header = line.split(',')
            self.main_data_found = True

        elif not line.startswith(',,'):
            # Header
            splitted = line.split(",")
            if len(splitted) > 0:
                name = splitted[0].strip()
                val = splitted[1].strip() if len(splitted) > 1 else ''
                self.file_header[name]=val

        return 0

class BioDropImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)

