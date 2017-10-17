# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Sysmex XT1800i
"""
import json
import traceback

from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import InstrumentCSVResultsFileParser
from bika.lims.exportimport.instruments.sysmex.xt import SysmexImporter
from bika.lims.utils import t

title = "Sysmex XT1800i"


def Import(context, request):
    """
    This function handles requests when user uploads a file and submits. Gets
    requests parameters, and creates a Parser object. Then based on that
    parser object, creates an Importer object and calls its importer.
    """
    infile = request.form['tx1800i_file']
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
    if fileformat == 'txt':
        parser = TX1800iParser(infile)
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

        importer = SysmexImporter(parser=parser,
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

SEPARATOR = '|'


class TX1800iParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, infile, 'TXT')
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
        return 0

    def _handle_header(self, sline):
        """
        """
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

        return 0

    def _submit_result(self):
        """
        Adding current values as a Raw Result and Resetting everything.
        """
        if self._cur_res_id and self._cur_values:
            # Setting DefaultResult just because it is obligatory.
            self._cur_values[self._keyword]['DefaultResult'] = 'DefResult'
            self._cur_values[self._keyword]['DefResult'] = ''
            # If we add results as a raw result, AnalysisResultsImporter will
            # automatically import them to the system. The only important thing
            # here is to respect the dictionary format.
            self._addRawResult(self._cur_res_id, self._cur_values)
            self._reset()

    def _format_keyword(self, keyword):
        """
        Removing special character from a keyword.
        """
        import re
        result = ''
        if keyword:
            result = re.sub(r"\W", "", keyword)
        return result

    def _reset(self):
        self._cur_section = ''
        self._cur_sub_section = ''
        self._cur_res_id = ''
        self._cur_values = {}
        self._is_header_line = False
        self._columns = []
        self._keyword = ''


