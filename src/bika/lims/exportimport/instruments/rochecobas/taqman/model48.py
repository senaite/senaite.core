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

""" Roche Cobas Taqman 48
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Roche Cobas - Taqman - 48"


class RocheCobasTaqmanParser(InstrumentCSVResultsFileParser):

    def __init__(self, rsf, fileformat=None):
        InstrumentCSVResultsFileParser.__init__(self, rsf)
        self._columns = []  # The different columns names
        self._values = {}  # The analysis services from the same resid
        self._resid = ''  # A stored resid
        self._rownum = None
        self._end_header = False
        self._fileformat = fileformat
        self._separator = ',' if self._fileformat == 'csv' else '\t'

    def _parseline(self, line):

        sline = line.replace('"', '').split(self._separator)

        if len(sline) > 0 and not self._end_header:
            self._columns = sline
            self._end_header = True
            return 0
        elif sline > 0 and self._end_header:
            self.parse_data_line(sline)
        else:
            self.err("Unexpected data format", numline=self._numline)
            return -1

    def parse_data_line(self, sline):
        """
        Parses the data line and builds the dictionary.
        :param sline: a split data line to parse
        :returns: the number of rows to jump and parse the next data line or return the code error -1
        """
        # if there are less values founded than headers, it's an error
        if len(sline) != len(self._columns):
            self.err("One data line has the wrong number of items")
            return -1
        rawdict = {}
        for idx, result in enumerate(sline):
            rawdict[self._columns[idx]] = result
        # Getting key values
        resid = rawdict['Sample ID']
        if resid == '' and rawdict['Order Number'] != '':
            # If Sample ID is void, we will use the OrderNumber as a reference.
            resid = rawdict['Order Number']
        elif resid == '' and rawdict['Order Number'] == '':
            # If there isn't Sample ID or Order Number
            self.err("Result identification not found.", numline=self._numline)
            return -1
        testname = rawdict['Test']
        if testname == '':
            # None test name found
            self.err("Result test name not found.", numline=self._numline)
            return -1
        del rawdict['Test']

        # Building the new dict
        rawdict['DefaultResult'] = 'Result'
        rawdict['Remarks'] = ''.join([rawdict['Result'], " on Order Number.", resid]) \
            if rawdict['Result'] == "Target Not Detected" else ''

        if self._fileformat == "csv":
            rawdict['DateTime'] = rawdict['Accepted Date/Time']
        else:
            rawdict['DateTime'] = self.csvDate2BikaDate(
                rawdict['Accepted Date/Time'])

        self._addRawResult(resid, {testname: rawdict}, False)
        return 0

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        Date, Time = DateTime.split(' ')
        dtobj = datetime.strptime(Date + ' ' + Time, "%Y/%m/%d %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")


class RocheCobasTaqmanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                          override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)

def Import(context, request):
    """ Beckman Coulter Access 2 analysis results
    """
    infile = request.form['rochecobas_taqman_model48_file']
    fileformat = request.form['rochecobas_taqman_model48_format']
    artoapply = request.form['rochecobas_taqman_model48_artoapply']
    override = request.form['rochecobas_taqman_model48_override']
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'rsf':
        parser = RocheCobasTaqmanParser(infile)
    if fileformat == 'csv':
        parser = RocheCobasTaqmanParser(infile, "csv")
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

        importer = RocheCobasTaqman48Importer(parser=parser,
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

class BeckmancoulterAccess2RSFParser(RocheCobasTaqmanParser):
    def getAttachmentFileType(self):
        return "Roche Cobas Taqman 48"

class RocheCobasTaqman48Importer(RocheCobasTaqmanImporter):
    def getKeywordsToBeExcluded(self):
        return []
