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

""" Cobas Integra 400 plus
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import CobasIntegra400plusImporter, CobasIntegra400plusCSVParser
import json
import traceback

title = "Cobas Integra 400 plus"


def Import(context, request):
    """ Cobas Integra analysis results
    """
    infile = request.form['cobas_integra_400_plus_file']
    fileformat = request.form['cobas_integra_400_plus_format']
    artoapply = request.form['cobas_integra_400_plus_artoapply']
    override = request.form['cobas_integra_400_plus_override']
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'cobas_integra_400_plus_file'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = CobasIntegra400plus2CSVParser(infile)
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

        importer = CobasIntegra400plus2Importer(parser=parser,
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


class CobasIntegra400plus2CSVParser(CobasIntegra400plusCSVParser):
    def getAttachmentFileType(self):
        return "Cobas Integra 400 plus"


class CobasIntegra400plus2Importer(CobasIntegra400plusImporter):
    def getKeywordsToBeExcluded(self):
        return []
