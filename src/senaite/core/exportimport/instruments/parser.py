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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import codecs

from senaite.core.exportimport.instruments.logger import Logger
from zope.deprecation import deprecate


class InstrumentResultsFileParser(Logger):
    """Base parser
    """

    def __init__(self, infile, mimetype):
        Logger.__init__(self)
        self._infile = infile
        self._header = {}
        self._rawresults = {}
        self._mimetype = mimetype
        self._numline = 0

    def getInputFile(self):
        """ Returns the results input file
        """
        return self._infile

    def parse(self):
        """Parses the input file and populates the rawresults dict.

        See getRawResults() method for more info about rawresults format

        Returns True if the file has been parsed successfully.

        Is highly recommended to use _addRawResult method when adding raw
        results.

        IMPORTANT: To be implemented by child classes
        """
        raise NotImplementedError

    @deprecate("Please use getRawResults directly")
    def resume(self):
        """Resumes the parse process

        Called by the Results Importer after parse() call
        """
        if len(self.getRawResults()) == 0:
            self.warn("No results found")
            return False
        return True

    def getAttachmentFileType(self):
        """ Returns the file type name that will be used when creating the
            AttachmentType used by the importer for saving the results file as
            an attachment in each Analysis matched.
            By default returns self.getFileMimeType()
        """
        return self.getFileMimeType()

    def getFileMimeType(self):
        """ Returns the results file type
        """
        return self._mimetype

    def getHeader(self):
        """ Returns a dictionary with custom key, values
        """
        return self._header

    def _addRawResult(self, resid, values={}, override=False):
        """ Adds a set of raw results for an object with id=resid
            resid is usually an Analysis Request ID or Worksheet's Reference
            Analysis ID. The values are a dictionary in which the keys are
            analysis service keywords and the values, another dictionary with
            the key,value results.
            The column 'DefaultResult' must be provided, because is used to map
            to the column from which the default result must be retrieved.

            Example:
            resid  = 'DU13162-001-R1'
            values = {
                'D2': {'DefaultResult': 'Final Conc',
                       'Remarks':       '',
                       'Resp':          '5816',
                       'ISTD Resp':     '274638',
                       'Resp Ratio':    '0.0212',
                       'Final Conc':    '0.9145',
                       'Exp Conc':      '1.9531',
                       'Accuracy':      '98.19' },

                'D3': {'DefaultResult': 'Final Conc',
                       'Remarks':       '',
                       'Resp':          '5816',
                       'ISTD Resp':     '274638',
                       'Resp Ratio':    '0.0212',
                       'Final Conc':    '0.9145',
                       'Exp Conc':      '1.9531',
                       'Accuracy':      '98.19' }
                }
        """
        if override or resid not in self._rawresults.keys():
            self._rawresults[resid] = [values]
        else:
            self._rawresults[resid].append(values)

    def _emptyRawResults(self):
        """Remove all grabbed raw results
        """
        self._rawresults = {}

    def getObjectsTotalCount(self):
        """The total number of objects (ARs, ReferenceSamples, etc.) parsed
        """
        return len(self.getRawResults())

    def getResultsTotalCount(self):
        """The total number of analysis results parsed
        """
        count = 0
        for val in self.getRawResults().values():
            count += len(val)
        return count

    def getAnalysesTotalCount(self):
        """ The total number of different analyses parsed
        """
        return len(self.getAnalysisKeywords())

    def getAnalysisKeywords(self):
        """Return found analysis service keywords
        """
        analyses = []
        for rows in self.getRawResults().values():
            for row in rows:
                analyses = list(set(analyses + row.keys()))
        return analyses

    def getRawResults(self):
        """Returns a dictionary containing the parsed results data

        Each dict key is the results row ID (usually AR ID or Worksheet's
        Reference Sample ID). Each item is another dictionary, in which the key
        is a the AS Keyword.

        Inside the AS dict, the column 'DefaultResult' must be provided, that
        maps to the column from which the default result must be retrieved.

        If 'Remarks' column is found, it value will be set in Analysis Remarks
        field when using the deault Importer.

        Example:

            raw_results['DU13162-001-R1'] = [{

                'D2': {'DefaultResult': 'Final Conc',
                        'Remarks':       '',
                        'Resp':          '5816',
                        'ISTD Resp':     '274638',
                        'Resp Ratio':    '0.0212',
                        'Final Conc':    '0.9145',
                        'Exp Conc':      '1.9531',
                        'Accuracy':      '98.19' },

                'D3': {'DefaultResult': 'Final Conc',
                        'Remarks':       '',
                        'Resp':          '5816',
                        'ISTD Resp':     '274638',
                        'Resp Ratio':    '0.0212',
                        'Final Conc':    '0.9145',
                        'Exp Conc':      '1.9531',
                        'Accuracy':      '98.19' }]

            in which:
            - 'DU13162-001-R1' is the Analysis Request ID,
            - 'D2' column is an analysis service keyword,
            - 'DefaultResult' column maps to the column with default result
            - 'Remarks' column with Remarks results for that Analysis
            - The rest of the dict columns are results (or additional info)
              that can be set to the analysis if needed (the default importer
              will look for them if the analysis has Interim fields).

            In the case of reference samples:
            Control/Blank:
            raw_results['QC13-0001-0002'] = {...}

            Duplicate of sample DU13162-009 (from AR DU13162-009-R1)
            raw_results['QC-DU13162-009-002'] = {...}

        """
        return self._rawresults


class InstrumentCSVResultsFileParser(InstrumentResultsFileParser):
    """Parser for CSV files
    """

    def __init__(self, infile, encoding=None):
        InstrumentResultsFileParser.__init__(self, infile, 'CSV')
        # Some Instruments can generate files with different encodings, so we
        # may need this parameter
        self._encoding = encoding

    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}",
                 mapping={"file_name": infile.filename})
        jump = 0
        # We test in import functions if the file was uploaded
        try:
            if self._encoding:
                f = codecs.open(infile.name, 'r', encoding=self._encoding)
            else:
                f = open(infile.name, 'rU')
        except AttributeError:
            f = infile
        except IOError:
            f = infile.file
        for line in f.readlines():
            self._numline += 1
            if jump == -1:
                # Something went wrong. Finish
                self.err("File processing finished due to critical errors")
                return False
            if jump > 0:
                # Jump some lines
                jump -= 1
                continue

            if not line or not line.strip():
                continue

            line = line.strip()
            jump = 0
            if line:
                jump = self._parseline(line)

        self.log(
            "End of file reached successfully: ${total_objects} objects, "
            "${total_analyses} analyses, ${total_results} results",
            mapping={"total_objects": self.getObjectsTotalCount(),
                     "total_analyses": self.getAnalysesTotalCount(),
                     "total_results": self.getResultsTotalCount()}
        )
        return True

    def splitLine(self, line):
        sline = line.split(',')
        return [token.strip() for token in sline]

    def _parseline(self, line):
        """ Parses a line from the input CSV file and populates rawresults
            (look at getRawResults comment)
            returns -1 if critical error found and parser must end
            returns the number of lines to be jumped in next read. If 0, the
            parser reads the next line as usual
        """
        raise NotImplementedError


class InstrumentTXTResultsFileParser(InstrumentResultsFileParser):
    """Parser for TXT files
    """

    def __init__(self, infile, separator, encoding=None,):
        InstrumentResultsFileParser.__init__(self, infile, 'TXT')
        # Some Instruments can generate files with different encodings, so we
        # may need this parameter
        self._separator = separator
        self._encoding = encoding

    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}", mapping={"file_name": infile.filename})
        jump = 0
        lines = self.read_file(infile)
        for line in lines:
            self._numline += 1
            if jump == -1:
                # Something went wrong. Finish
                self.err("File processing finished due to critical errors")
                return False
            if jump > 0:
                # Jump some lines
                jump -= 1
                continue

            if not line:
                continue

            jump = 0
            if line:
                jump = self._parseline(line)

        self.log(
            "End of file reached successfully: ${total_objects} objects, "
            "${total_analyses} analyses, ${total_results} results",
            mapping={"total_objects": self.getObjectsTotalCount(),
                     "total_analyses": self.getAnalysesTotalCount(),
                     "total_results": self.getResultsTotalCount()}
        )
        return True

    def read_file(self, infile):
        """Given an input file read its contents, strip whitespace from the
         beginning and end of each line and return a list of the preprocessed
         lines read.

        :param infile: file that contains the data to be read
        :return: list of the read lines with stripped whitespace
        """
        try:
            encoding = self._encoding if self._encoding else None
            mode = 'r' if self._encoding else 'rU'
            with codecs.open(infile.name, mode, encoding=encoding) as f:
                lines = f.readlines()
        except AttributeError:
            lines = infile.readlines()
        lines = [line.strip() for line in lines]
        return lines

    def splitLine(self, line):
        sline = line.split(self._separator)
        return [token.strip() for token in sline]

    def _parseline(self, line):
        """ Parses a line from the input CSV file and populates rawresults
            (look at getRawResults comment)
            returns -1 if critical error found and parser must end
            returns the number of lines to be jumped in next read. If 0, the
            parser reads the next line as usual
        """
        raise NotImplementedError
