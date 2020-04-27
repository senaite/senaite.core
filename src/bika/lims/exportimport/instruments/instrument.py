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

""" Generic controller for instrument results import view
"""
import json
import traceback
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import AnalysisResultsImporter

def getFileFormat(request):
    return request.form['instrument_results_file_format']

def getResultsInputFile(request):
    return request.form['instrument_results_file']


def GenericImport(context, request, parser, importer=None):
    infile = getResultsInputFile(request)
    fileformat = getFileFormat(request)
    artoapply = request.form['artoapply']
    override = request.form['results_override']

    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []
    # Load the most suitable parser according to file extension/options/etc...
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))

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

        imp = importer
        if not imp:
            imp = AnalysisResultsImporter(parser=parser,
                                          context=context,
                                          allowed_ar_states=status,
                                          allowed_analysis_states=None,
                                          override=over,
                                          instrument_uid=instrument)

        tbex = ''
        try:
            imp.process()
        except:
            tbex = traceback.format_exc()
        errors = imp.errors
        logs = imp.logs
        warns = imp.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


def format_keyword(keyword):
    """
    Removing special character from a keyword. Analysis Services must have
    this kind of keywords. E.g. if assay name from the Instrument is
    'HIV-1 2.0', an AS must be created on Bika with the keyword 'HIV120'
    """
    import re
    result = ''
    if keyword:
        result = re.sub(r"\W", "", keyword)
        result = re.sub("_", "", result)
    return result
