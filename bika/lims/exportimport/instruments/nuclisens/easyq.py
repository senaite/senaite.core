# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Nuclisens EasyQ
"""
import csv
import types
from cStringIO import StringIO
from openpyxl import load_workbook

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Nuclisens EasyQ"


class EasyQParser(InstrumentResultsFileParser):
    """ Parser
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'XLSX')

    def xlsx_to_csv(self, infile, worksheet=0, delimiter=","):
        """ Convert xlsx to easier format first, since we want to use the
        convenience of the CSV library
        """
        wb = load_workbook(self.getInputFile())
        sheet = wb.worksheets[worksheet]
        buffer = StringIO()

        # extract all rows
        for n, row in enumerate(sheet.rows):
            line = []
            for cell in row:
                value = cell.value
                if type(value) in types.StringTypes:
                    value = value.encode("utf8")
                if value is None:
                    value = ""
                line.append(str(value))
            print >>buffer, delimiter.join(line)
        buffer.seek(0)
        return buffer

    def parse(self):
        """ parse the data
        """

        # convert the xlsx file to csv first
        delimiter = "|"
        csv_file = self.xlsx_to_csv(self.getInputFile(), delimiter=delimiter)
        reader = csv.DictReader(csv_file, delimiter=delimiter)

        for n, row in enumerate(reader):
            resid = row.get("SampleID", None)
            serial = row.get("SerialNumber", None)

            # no resid and no serial
            if not any([resid, serial]):
                self.err("Result identification not found.", numline=n)
                continue

            # get the test name
            testname = row.get("Description", None)
            if testname is None:
                self.err("Testname (Description) not found.", numline=n)
                continue

            rawdict = row
            rawdict['DefaultResult'] = 'Value'
            key = resid or serial
            self._addRawResult(key, {testname: rawdict}, False)


class EasyQImporter(AnalysisResultsImporter):
    """ Importer
    """

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):

        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         idsearchcriteria,
                                         override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Import Form
    """
    infile = request.form['nuclisens_easyq_file']
    fileformat = request.form['nuclisens_easyq_format']
    artoapply = request.form['nuclisens_easyq_artoapply']
    override = request.form['nuclisens_easyq_override']
    sample = request.form.get('nuclisens_easyq_sample', 'requestid')
    instrument = request.form.get('nuclisens_easyq_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'xlsx':
        parser = EasyQParser(infile)
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

        sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getRequestID']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = EasyQImporter(parser=parser,
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
