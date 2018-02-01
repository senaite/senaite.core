# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Sysmex XT-4000i
"""
import json
import traceback

from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.sysmex.xt.i1800 import TX1800iParser
from bika.lims.exportimport.instruments.sysmex.xt import SysmexXTImporter
from bika.lims.utils import t

title = "Sysmex XT - 4000i"


def Import(context, request):
    """
    This function handles requests when user uploads a file and submits. Gets
    requests parameters, and creates a Parser object. Then based on that
    parser object, creates an Importer object and calls its importer.
    """
    infile = request.form['tx4000i_file']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    sample = request.form.get('sample', 'requestid')
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []
    status_mapping = {
        'received': ['sample_received'],
        'received_tobeverified': ['sample_received', 'attachment_due', 'to_be_verified']
    }
    override_mapping = {
        'nooverride': [False, False],
        'override': [True, False],
        'overrideempty': [True, True]
    }
    sample_mapping = {
        'requestid': ['getId'],
        'sampleid': ['getSampleID'],
        'clientsid': ['getClientSampleID'],
        'sample_clientsid': ['getSampleID', 'getClientSampleID']
    }
    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'txt':
        # So far, both Instruments from Sysmex TX Series use the same format for result files.
        # In both case 'ASTM' protocol is used with the same order of columns. So,
        # we are going to use TXT Parser from 'TX1800i' Interface.
        parser = TX1800iParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
        status = status_mapping.get(artoapply, ['sample_received', 'attachment_due', 'to_be_verified'])
        over = override_mapping.get(override, [False, False])
        sam = sample_mapping.get(sample, ['getId', 'getSampleID', 'getClientSampleID'])
        importer = SysmexXTImporter(parser=parser,
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
