# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

""" Alere Pima
"""
from datetime import datetime
from bika.lims.utils import to_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class AlerePimaSLKParser(InstrumentCSVResultsFileParser):
    #This class is made thinking in beads, but the other files
    # are quite similar.
    def __init__(self, slk):
        InstrumentCSVResultsFileParser.__init__(self, slk)
        self._columns = {} #The diferents data columns names
        self._linedata = {}#The line with the data
        self._rownum = None
        self._isFirst = True #Used to know if is the first linedata


    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}", mapping={"file_name":infile.filename})
        for line in infile.readlines():
            line = line.split(';')
            #The end of file
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
            #The header
            elif line[0] != 'C' and line[0] != 'E':
                self._header[line[0]] = line[1]
            #Obtain the columns name
            elif line[0] == 'C' and line[2] == 'Y1':
                self._columns[line[1]] = line[3].split('"')[1]
                #self._columns.append(line[3].split('"')[1])
            #Is a data line
            else:
                if line[2] != self._rownum:
                    self.builddict(self._isFirst)
                    self._linedata = {}
                    self._rownum = line[2]
                data = line[3].split('"')
                if len(data) >1:
                    self._linedata[line[1]] = data[1]
                else:
                    self._linedata[line[1]] = data[0][1:-1]


    def builddict(self,isFirst):
        #Buid the dict parsing self._columns and self._linedata
        #This method should be modified to read other files
        rawdict = {}
        if self._isFirst:
            self._isFirst = False
        else:
            for i in self._columns.keys():
                if i in self._linedata:
                    rawdict[self._columns[i]] = self._linedata[i]
                else:
                    rawdict[self._columns[i]] = None

            rawdict['Remarks'] = rawdict['ErrorMessage']
            rawdict['DefaultResult'] = self._columns['X6']
            #I don't know which is the analysis service keyword...
            self._addRawResult(rawdict['Sample'],{rawdict['Assay ID']:rawdict})

    def getAttachmentFileType(self):
        #This method must be override for other file types.
        return "Alare Pima Beads"

class AlerePimaImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
