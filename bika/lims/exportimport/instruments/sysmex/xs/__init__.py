"""Sysmex XS 500i
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class SysmexXSCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv, analysiskey=None, defaultresult=None):
        # analysiskey contains the value of the selected AS or None
        # defaultresult contains the data column key which will be tagged as DefaultResult in the AS results dictionary.
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []
        # When AS isn't selected we need to know which columns don't contain data. Since we don't know in
        # which order this columns could be, we need to write an ugly list with the possible columns names to exclude.
        self._excludedcolumns = ['Instrument ID', 'Analysis Date', 'Analysis Time', 'Rack No.', 'Tube Pos.',
                                 'Sample ID No', 'Sample ID Info', 'Analysis Mode', 'Patient ID', 'Analysis Info.',
                                 'Sample Judgment Info.', 'Positive(Diff)', 'Positive(Morph)', 'Positive(Count)',
                                 'Error(Func)', 'Error(Result)', 'Order Info.', 'WBC Abnormal', 'WBC Suspect',
                                 'RBC Abnormal', 'RBC Suspect', 'PLT Abnormal', 'PLT Suspect', 'Unit Info.',
                                 'Validate', 'Action Message(Diff)', 'Action Message(Delta)', 'Sample Comment',
                                 'Patient Name', 'Date of Birth', 'Sex', 'Patient comment', 'Ward', 'Doctor',
                                 'Transmitted Parameters', 'Sequence No.']
        self.analysiskey = analysiskey
        self.defaultresult = defaultresult

    def _parseline(self, line):
        sline = line.split(',')
        # Check if is the header line
        if sline[0] in self._excludedcolumns and not self._end_header:
            # It's the header row
            self._columns = sline
            self._end_header = True
            return 0

        elif not sline[0] in self._excludedcolumns and self._end_header:
            # It's the data line
            self.parse_data_line(sline)
        else:
            self.err("Unexpected header format", numline=self._numline)
            return -1

    def parse_data_line(self, sline):
        """
        Parse the data line. If an AS was selected it can distinguish between data rows and information rows.
        :param sline: a split data line to parse
        :return: the number of rows to jump and parse the next data line or return the code error -1
        """
        # if there are less values founded than headers, it's an error
        if len(sline) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return 0
        if self.analysiskey:
            # If an AS is selected it should saves all the columns from the same row under the selected AS.
            rawdict = {}
            for idx, result in enumerate(sline):
                # All data is interpreted as different fields from the same AS
                rawdict[self._columns[idx]] = result
            rid = rawdict.get('Sample ID No')
            if not rid:
                self.err("No Sample ID defined",
                         numline=self._numline)
                return -1
            rawdict['DefaultResult'] = self.defaultresult \
                                     if self.defaultresult in self._columns \
                                     else self.err("Default Result Key " + self.defaultresult + " not found")
            rawdict['DateTime'] = self.csvDate2BikaDate(rawdict['Analysis Date'], rawdict['Analysis Time'])
            self._addRawResult(rid, {self.analysiskey: rawdict}, False)

        else:
            # If non AS is selected it should saves all data under the same analysed sample (Sample ID No), and ignore
            # the less important rows from the line.
            headerdict = {}
            datadict = {}
            for idx, result in enumerate(sline):
                if self._columns[idx] not in self._excludedcolumns:
                    datadict[self._columns[idx]] = {'Result': result, 'DefaultData': 'Result'}
                else:
                    headerdict[self._columns[idx]] = result
            rid = headerdict['Sample ID No']
            datadict['DateTime'] = self.csvDate2BikaDate(headerdict['Analysis Date'], headerdict['Analysis Time'])
            self._addRawResult(rid, datadict, False)
            self._header = headerdict
            return 0

    def csvDate2BikaDate(self, Date, Time):
        #11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        dtobj = datetime.strptime(Date + ' ' + Time, "%Y/%d/%m %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")


class SysmexXSImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
