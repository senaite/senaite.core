#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Alere Pima
"""
from datetime import datetime
from bika.lims.utils import to_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class AlerePimaSLKParser(InstrumentCSVResultsFileParser):

    def __init__(self, slk):
        InstrumentCSVResultsFileParser.__init__(self, slk)
        self._columns = [] #The diferents data columns names
        self._linedata = [] #The line with the data
        self._rownum = None
        self._isFirst = True #Used to know if is the first linedata
        #self._header = {} #The header line

    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}", mapping={"file_name":infile.filename})
        for line in infile.readlines():
            line = line.split(';')
            if line[0] == 'E\n':
                self.log(
                "End of file reached successfully: ${total_objects} objects, "
                "${total_analyses} analyses, ${total_results} results",
                mapping={"total_objects": self.getObjectsTotalCount(),
                "total_analyses": self.getAnalysesTotalCount(),
                "total_results":self.getResultsTotalCount()}
                )
                self.builddict(self._isFirst)
                return True
            elif line[0] != 'C' and line[0] != 'E':
                self._header[line[0]] = line[1]
            elif line[0] == 'C' and line[2] == 'Y1':
                self._columns.append(line[3].split('"')[1])
            else:
                if line[2] != self._rownum:
                    self.builddict(self._isFirst)
                    self._linedata = []
                    self._rownum = line[2]
                data = line[3].split('"')
                if len(data) >1:
                    self._linedata.append(data[1])
                else:
                    self._linedata.append(data[0][1:-1])


    def builddict(self,isFirst):
        #Buid the dict from self._columns and self._linedata
        dict = {}
        rawdict = {}
        if self._isFirst:
            self._isFirst = False
        else:
            CleanColumnsArray = self._columns[1:]
            if len(self._linedata) != len(self._columns):
                CleanColumnsArray.remove('ErrorMessage')
                dict['ErrorMessage'] = ''
            for e in enumerate(CleanColumnsArray,start=1):
                dict[e[1]] = self._linedata[e[0]]
            dict['DefaultResult'] = self._linedata[5]
            dict['Remarks'] = dict['ErrorMessage']
            rawdict[self._linedata[2]] = dict
            self._addRawResult(self._linedata[0],rawdict)


    def getAttachmentFileType(self):
        return "Alare Pima Beads"

class AlerePimaImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
