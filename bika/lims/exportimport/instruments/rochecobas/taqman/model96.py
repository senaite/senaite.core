# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Roche Cobas Taqman 96
"""
import csv
from DateTime import DateTime

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Roche Cobas - Taqman - 96"


class RocheCobasTaqmanRSFParser(InstrumentResultsFileParser):
    """ Parser for Roche Corbase Taqman 96
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'CSV')

    def parse(self):
        reader = csv.DictReader(self.getInputFile(), delimiter=',')

        for n, row in enumerate(reader):
            resid = row.get("Sample ID", None)
            orderno = row.get("Order Number", None)

            # no resid and no orderno
            if not any([resid, orderno]):
                self.err("Result identification not found.", numline=n)
                continue

            testname = row.get("Test", None)
            if testname is None:
                self.err("Result test name not found.", numline=n)
                continue

            dt = row.get("Accepted Date/Time", None)
            if dt is not None:
                dt = DateTime(dt)

            remarks = ""
            result = row.get("Result")
            if result == "Target Not Detected":
                remarks = "".join([result, " on Order Number,", resid])

            rawdict = row
            rawdict['DefaultResult'] = 'Result'
            rawdict['Remarks'] = remarks
            rawdict['DateTime'] = dt

            self._addRawResult(resid, {testname: rawdict}, False)


class RocheCobasTaqmanImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Beckman Coulter Access 2 analysis results
    """
    infile = request.form['rochecobas_taqman_model96_file']
    fileformat = request.form['rochecobas_taqman_model96_format']
    artoapply = request.form['rochecobas_taqman_model96_artoapply']
    override = request.form['rochecobas_taqman_model96_override']
    sample = request.form.get('rochecobas_taqman_model96_sample',
                              'requestid')
    instrument = request.form.get('rochecobas_taqman_model96_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'rsf':
        parser = RocheCobasTaqmanRSFParser(infile)
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

        importer = RocheCobasTaqmanImporter(parser=parser,
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
