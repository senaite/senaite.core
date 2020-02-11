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

""" GeneXpert
"""
import csv
import json
import traceback
import types
from cStringIO import StringIO
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

from bika.lims import bikaMessageFactory as _

from bika.lims.utils import t

title = "GeneXpert"


def Import(context, request):
    """
    This function handles requests when user uploads a file and submits. Gets
    requests parameters, and creates a Parser object. Then based on that
    parser object, creates an Importer object and calls its importer.
    """
    infile = request.form['genexpert_file']
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
    if fileformat == 'csv':
        parser = GeneXpertParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
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

        importer = GeneXpertImporter(parser=parser,
                                     context=context,
                                     allowed_ar_states=status,
                                     allowed_analysis_states=None,
                                     override=over,
                                     instrument_uid=instrument)
        tbex = ''
        try:
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


SEPARATOR = ','
SECTION_RESULT_TABLE = 'RESULT TABLE'
SUBSECTION_ANALYTE_RESULT = 'Analyte Result'
# Results values should match the ones from Analysis Services from Bika.
RESULT_VALUE_INDETERMINE = 1
RESULT_VALUE_NEGATIVE = 2
RESULT_VALUE_POSITIVE = 3


class GeneXpertParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, infile,
                                                encoding='utf-16-le')
        self._cur_section = ''  # Current section of CSV
        self._cur_sub_section = ''  # Current subsection of CSV
        self._cur_res_id = ''  # Sample or Patient ID of the current record
        self._cur_values = {}  # Values of the last record
        self._is_header_line = False  # To get headers of Analyte Result table
        self._columns = []  # Column names of Analyte Result table
        self._keyword = ''  # Keyword of Analysis Service

    def _parseline(self, line):
        """
        Result CSV Line Parser.
        :param line: a to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        sline = line.split(SEPARATOR)

        if is_header(sline):
            return self._handle_header(sline)
        # If it is not an header it contains some data. but we need data only
        # from the RESULT TABLE section.
        elif not self._cur_section == SECTION_RESULT_TABLE:
            return 0
        # If line starts with 'Sample ID', then it is res_id of current record.
        elif sline[0].lower() == 'Sample ID'.lower():
            self._cur_res_id = sline[1].strip()
            return 0
        # If line starts with 'Assay' column,it is keyword of Analysis Service.
        elif sline[0].lower() == 'Assay'.lower():
            self._keyword = self._format_keyword(sline[1])
            return 0
        # Results are in Analyte Result subsection. We can skip other lines.
        elif not self._cur_sub_section == SUBSECTION_ANALYTE_RESULT:
            return 0
        # If this is header line of Analyte Result table, set the columns
        elif self._is_header_line:
            self._is_header_line = False
            self._columns = sline
        # Must be result line of Analyte Result Table.
        else:
            return self._handle_result_line(sline)

    def _handle_header(self, sline):
        """
        A function for lines with only ONE COLUMN.
        If line has only one column, then it is either a Section or
        Subsection name.
        """
        # All characters UPPER CASE means it is a Section.
        if sline[0].isupper():
            self._cur_section = sline[0]
            self._cur_sub_section = ''
            return 0
        else:
            self._cur_sub_section = sline[0]
            if sline[0] == SUBSECTION_ANALYTE_RESULT:
                # This is Analyte Result Line, next line will be headers of
                # results table
                self._is_header_line = True
                return 0
            elif sline[0] in ('Detail', 'Errors', 'Messages'):
                # It is end of Analyte Result sub-section. Add the last
                # record as a raw result and reset everything.
                self._submit_result()
                return 0

    def _handle_result_line(self, sline):
        """
        Parses the data line and adds to the dictionary.
        :param sline: a split data line to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        # If there are less values founded than headers, it's an error
        if len(sline) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return -1
        result = ''
        name = ''
        for idx, val in enumerate(sline):
            if self._columns[idx] == 'Analyte Name':
                name = val
            elif self._columns[idx] == 'Analyte Result':
                result = self._convert_result(val)

        if not self._cur_values.get(self._keyword, None):
            self._cur_values[self._keyword] = {}

        self._cur_values[self._keyword][name] = result

        # Each line goes to result values as well in case AS'es for each
        # Analyte is created in Bika. For those kind of AS'es, keywords must be
        # the same as Analyte Name field from CSV.
        self._cur_values[name] = {
                'DefaultResult': 'Analyte Result',
                'Remarks': '',
                'Analyte Result': result,
                }

        # Adding this result to the previous results
        # in the self._cur_values dictionary, as an interim field.
        for key in self._cur_values:
            if key == name:
                continue
            self._cur_values[key][name] = result

        return 0

    def _submit_result(self):
        """
        Adding current values as a Raw Result and Resetting everything.
        Notice that we are not calculating final result of assay. We just set
        NP and GP values and in Bika, AS will have a Calculation to generate
        final result based on NP and GP values.
        """
        if self._cur_res_id and self._cur_values:
            # Setting DefaultResult just because it is obligatory. However,
            # it won't be used because AS must have a Calculation based on
            # GP and NP results.
            self._cur_values[self._keyword]['DefaultResult'] = 'DefResult'
            self._cur_values[self._keyword]['DefResult'] = ''
            # If we add results as a raw result, AnalysisResultsImporter will
            # automatically import them to the system. The only important thing
            # here is to respect the dictionary format.
            self._addRawResult(self._cur_res_id, self._cur_values)
            self._reset()

    def _format_keyword(self, keyword):
        """
        Removing special character from a keyword. Analysis Services must have
        this kind of keywords. E.g. if assay name from GeneXpert Instrument is
        'Ebola RUO', an AS must be created on Bika with the keyword 'EbolaRUO'
        """
        import re
        result = ''
        if keyword:
            result = re.sub(r"\W", "", keyword)
            # Remove underscores ('_') too.
            result = re.sub(r"_", "", result)
        return result

    def _convert_result(self, value):
        if not value:
            return RESULT_VALUE_INDETERMINE
        elif value.upper() == 'NEG':
            return RESULT_VALUE_NEGATIVE
        elif value.upper() == 'POS':
            return RESULT_VALUE_POSITIVE
        else:
            return RESULT_VALUE_INDETERMINE

    def _reset(self):
        self._cur_section = ''
        self._cur_sub_section = ''
        self._cur_res_id = ''
        self._cur_values = {}
        self._is_header_line = False
        self._columns = []
        self._keyword = ''


class GeneXpertImporter(AnalysisResultsImporter):

    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def is_header(line):
    """
    If a line has only one column, then it is a Section or Subsection
    header.
    :param line: Line to check
    :return: boolean -If line is header
    """
    if len(line) == 1:
        return True
    for idx, val in enumerate(line):
        if idx > 0 and val:
            return False
    return True
