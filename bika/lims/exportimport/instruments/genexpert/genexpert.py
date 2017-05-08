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


class GenExpertParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, csv)

    def _parseline(self, line):
        return 0


class GenExpertImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
