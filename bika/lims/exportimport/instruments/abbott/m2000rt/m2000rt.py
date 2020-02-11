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

""" Abbott m2000 Real Time
"""

from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Abbott - m2000 Real Time"


def Import(context, request):
    """
    Abbot m2000 Real Time results import. This function handles
    requests when the user uploads a file and submits. It gets
    request parameters and creates a Parser object based on the
    parameters' values. After that, and based on that parser object,
    it creates an Importer object called importer that will process
    the selected file and try to import the results.
    """
    # Read the values the user has specified for the parameters
    # that appear in the import view of the current instrument
    # and that are defined in the instrument interface template
    infile = request.form['filename']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'tsv':
        parser = Abbottm2000rtTSVParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Select parameters for the importer from the values
        # just read from the import view
        status = ['sample_received', 'attachment_due', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'attachment_due', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        # Crate importer with the defined parser and the
        # rest of defined parameters. Then try to import the
        # results from the file
        importer = Abbottm2000rtImporter(parser=parser,
                                         context=context,
                                         allowed_ar_states=status,
                                         allowed_analysis_states=None,
                                         override=over,
                                         instrument_uid=instrument)
        tbex = ''
        try:
            # run the parser and save results
            importer.process()
        except:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


class Abbottm2000rtTSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, infile,
                                                encoding='utf-8-sig')
        self._separator = '\t'  # values are separated by tabs
        self._is_header = False
        self._current_section = ''  # current section of the file
        self._columns = None  # Column names of Analyte Result table
        self._ar_keyword = None  # Keyword of Analysis Service

    def _parseline(self, line):
        """
        Results log file line Parser. The parse method in
        InstrumentCSVResultsFileParser calls this method for each line
        in the results file that is to be parsed.
        :param line: a to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        split_line = line.split(self._separator)
        if self._is_header:
            self._is_header = False
            self._current_section = split_line[0]
            return 1  # Skip the line of equal signs after a header

        # If the line has only one column and it is made entirely of equal signs
        # then it is the beginning or the end a section definition. Since equal sign
        # lines corresponding to the end of section definitions are skipped this must
        # be the beginning of a section definition.
        elif len(split_line) == 1 and all(x == '=' for x in split_line[0]):
            self._is_header = True
            # if exiting result information section then reset column names and AR keyword
            if 'result information' in self._current_section.lower():
                self._reset()
        # From the assay calibration section the assay name is retrieved
        elif 'assay calibration' in self._current_section.lower():
            # if line inside assay calibration section starts with assay name,
            # then its value is the analysis service keyword
            if 'assay name' in split_line[0].lower():
                self._ar_keyword = self._format_keyword(split_line[1])
        # If current section is results information then process the results
        elif 'result information' in self._current_section.lower():
            if self._columns is None:
                self._columns = split_line
            else:
                result_id, values = self._handle_result_line(split_line)
                if result_id and values:
                    self._addRawResult(result_id, values)

        return 0

    def _handle_result_line(self, split_line):
        """
        Parses the data line and adds the results to the dictionary.
        :param split_line: a split data line to parse
        :returns: the current result id and the dictionary of values obtained from the results
        """
        values = {}
        result_id = ''
        if self._ar_keyword:
            # Create a new entry in the values dictionary and store the results
            values[self._ar_keyword] = {}
            for idx, val in enumerate(split_line):
                if self._columns[idx].lower() == 'sampleid':
                    result_id = val
                else:
                    # columns with date in its name store only the date and
                    # columns with time in its name store date and time.
                    if val and ('date' in self._columns[idx].lower()
                                or 'time' in self._columns[idx].lower()):
                        val = self._date_to_bika_date(val, 'date' in self._columns[idx].lower())
                    values[self._ar_keyword][self._columns[idx]] = val
                values[self._ar_keyword]['DefaultResult'] = 'FinalResult'

        return result_id, values

    def _format_keyword(self, keyword):
        """
        Removing special character from a keyword. Analysis Services must have
        this kind of keywords. E.g. if assay name from GeneXpert Instrument is
        HIV0.6ml, an AS must be created on Bika with the keyword 'HIV06ml'
        """
        import re
        result = ''
        if keyword:
            result = re.sub(r"\W", "", keyword)
        return result

    def _reset(self):
        """
        Reset column name's values and AR keyword
        :return: None
        """
        self._columns = None  # Column names of Analyte Result table
        self._ar_keyword = None  # Keyword of Analysis Service

    def _date_to_bika_date(self, date_time, only_date):
        """
        Convert a string containing a date from results file to bika format
        :param date_time: str with Date to convert
        :param only_date: boolean value that specifies if there is only a date
        to parse (true) or date plus time (false)
        :return: datetime in bika format
        """
        # if only date the input date format is: 2017/01/26
        # else: 2017/01/26 12:47:09 PM
        if only_date:
            return datetime.strptime(date_time, '%Y/%m/%d').strftime('%Y%m%d')
        else:
            return datetime.strptime(date_time, "%Y/%m/%d %I:%M:%S %p").strftime("%Y%m%d %H:%M:%S")


class Abbottm2000rtImporter(AnalysisResultsImporter):
    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
