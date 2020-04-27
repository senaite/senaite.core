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
        importer = SysmexXTImporter(parser=parser,
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
