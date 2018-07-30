# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" Beckman Coulter Access 2
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import TaqMan96DNA212BSCSVParser, TaqMan96DNA212BSImporter
import json
import traceback

title = "TaqMan96 DNA212BS"


def Import(context, request):
    """ TaqMan96 DNA212BS analysis results
    """
    infile = request.form['taqman96_dna212bs_file']
    fileformat = request.form['taqman96_dna212bs_format']
    artoapply = request.form['taqman96_dna212bs_artoapply']
    override = request.form['taqman96_dna212bs_override']
    sample = request.form.get('taqman96_dna212bs_sample',
                              'requestid')
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = TaqMan96DNA212BS2CSVParser(infile)
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

        importer = TaqMan96DNA212BS2Importer(parser=parser,
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


class TaqMan96DNA212BS2CSVParser(TaqMan96DNA212BSCSVParser):
    def getAttachmentFileType(self):
        return "TaqMan96 DNA212BS "


class TaqMan96DNA212BS2Importer(TaqMan96DNA212BSImporter):
    def getKeywordsToBeExcluded(self):
        return []
