""" Tescan TIMA
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
from datetime import datetime

class TimaCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []

    def _splitline(self, line):
        return [val.translate(None, '"').strip() for val in line.split(',')]

    # "AA00228","12/11/2003","20:49:24", ,0,"Cromo (Cr)","Cr",205.56,1.298161935e-003, ,"mg/muestra",
    # The above line shows the data row from the file however this method
    # is called it will not have any double quotes as they were removed in the _parseline step.
    def _parseline(self, line):
        if not self._columns:
            self._columns = self._splitline(line)
            return 0
        else:
            if not line.strip():
                return 0

            vals = dict(zip(self._columns, self._splitline(line)))

            rid = vals.get('Sample ID', '')
            if not rid:
                self.err("No Sample ID defined", numline=self._numline)
                return 0

            acode = vals.get('Elem','')
            if not acode:
                self.err("No analysis code defined", numline=self._numline)
                return 0

            vals['DefaultResult']='Conc (Samp)'
            try:
                # 12/11/2003 20:49:24
                dtstr = '%s %s' % (_values['Date'], _values['Time'])
                dtobj = datetime.strptime(dtstr, '%d/%m/%Y %H:%M:%S')
                vals['DateTime'] = dtobj.strftime("%Y%m%d %H:%M:%S")
            except:
                pass
            rawdict = {acode: vals}

            self._addRawResult(rid, rawdict)
            return 0


class TimaImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
