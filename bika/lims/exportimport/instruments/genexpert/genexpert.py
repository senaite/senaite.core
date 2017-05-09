# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" GenExpert
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

title = "GenExpert"


def Import(context, request):
    """ Import Form
    """
    infile = request.form['genexpert_file']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    sample = request.form.get('sample', 'requestid')
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = GenExpertParser(infile)
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

        sam = ['getId', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getId']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = GenExpertImporter(parser=parser,
                                     context=context,
                                     idsearchcriteria=sam,
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


class GenExpertParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, infile)
        self._cur_section = ''  # Current section of CSV
        self._cur_sub_section = ''  # Current subsection of CSV
        self._cur_res_id = ''  # Sample or Patient ID of the current record
        self._cur_values = {}  # Values of the last record
        self._is_header_line = False  # To get headers of Analyte Result table
        self._columns = []  # Column names of Analyte Result table

    def _parseline(self, line):
        """
        Result CSV Line Parser.
        :param line: a to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        sline = line.split(SEPARATOR)
        # If a line has only one column, then it is a Section or Subsection
        # header.
        if len(sline) == 1:
            return self._handle_header(sline)
        # If it is not an header it contains some data. but we need data only
        # from the RESULT TABLE section.
        elif not self._cur_section == SECTION_RESULT_TABLE:
            return 0
        # If line start with Sample ID, then it is res_id of current record.
        elif sline[0].lower() == 'Sample ID'.lower():
            self._cur_res_id = sline[1].strip()
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
            self._cur_section == sline[0]
            if sline[0] == SECTION_RESULT_TABLE:
                # We are going to go through new results table. Add the last
                # record as a raw result and reset everything.
                self._addRawResult(self._cur_res_id, self._cur_values)
                self._reset()
            return 0
        else:
            self._cur_sub_section == sline[0]
            if sline[0] == SUBSECTION_ANALYTE_RESULT:
                # This is Analyte Result Line, next line will be headers of
                # results table
                self._is_header_line = True
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

        # Adding line to result values
        self._cur_values[name] = {
                'DefaultResult': 'Analyte Result',
                'Remarks': '',
                'Analyte Result': result,
                }

        # Maybe not necessary but adding this result to the previous results
        # in the self._cur_values dictionary.
        for key in self._cur_values:
            if key == name:
                continue
            self._cur_values[key][name] = result

        return 0

    def _convert_result(self, value):
        if not value:
            return 0
        elif value.lower() == 'neg':
            return 2
        elif value.lower() == 'pass':
            return 3
        else:
            return 1

    def _reset(self):
        self._cur_sub_section = ''
        self._cur_res_id = ''
        self._cur_values = {}
        self._is_header_line = False
        self._columns = []


class GenExpertImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
