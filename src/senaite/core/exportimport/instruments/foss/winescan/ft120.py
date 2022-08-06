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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

""" FOSS 'Winescan FT120'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import WinescanImporter, WinescanCSVParser
import json
import six
import traceback

title = "FOSS - Winescan FT120"


def Import(context, request):
    """ Read FOSS's Winescan FT120 analysis results
    """
    infile = request.form['wsf_file']
    fileformat = request.form['wsf_format']
    artoapply = request.form['wsf_artoapply']
    override = request.form['wsf_override']
    instrument = request.form.get('instrument', None)
    errors = []
    warns = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = WinescanFT120CSVParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
        status = ['sample_received', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        importer = WinescanFT120Importer(parser=parser,
                                         context=context,
                                         allowed_ar_states=status,
                                         allowed_analysis_states=None,
                                         override=over,
                                         instrument_uid=instrument)

        tbex = ''
        try:
            importer.process()
        except Exception:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


class WinescanFT120CSVParser(WinescanCSVParser):

    def __init__(self, csv):
        WinescanCSVParser.__init__(self, csv)
        self._omitrows = ['Pilot definition',
                         'Pilot test',
                         'Zero setting',
                         'Zero correction']
        self._omit = False
        self._parsedresults = {}
        self._calibration = 0

    def getAttachmentFileType(self):
        return "FOSS Winescan FT120 CSV"

    def _parseline(self, line):
        if line.startswith('Calibration'):
            self._calibration += 1
            return 0

        return WinescanCSVParser._parseline(self, line)

    def _addRawResult(self, resid, values={}, override=False):
        """ Structure of values dict (dict entry for each analysis/field):

            {'ALC': {'ALC': '13.55',
                     'DefaultResult': 'ALC',
                     'Remarks': ''},
             'CO2': {'CO2': '0.66',
                     'DefaultResult': 'CO2',
                     'Remarks': ''},
             'Date': {'Date': '21/11/2013',
                      'DefaultResult': 'Date',
                      'Remarks': ''},
             'Malo': {'DefaultResult': 'Malo',
                      'Malo': '0.26',
                      'Remarks': ''},
             'Meth': {'DefaultResult': 'Meth',
                      'Meth': '0.58',
             'Rep #': {'DefaultResult': 'Rep #',
                      'Remarks': '',
                      'Rep #': '1'}
            }
        """

        if 'Date' in values and 'Time' in values:
            try:
                dtstr = '%s %s' % (values.get('Date')['Date'], values.get('Time')['Time'])
                # 2/11/2005 13:33 PM
                from datetime import datetime
                dtobj = datetime.strptime(dtstr, '%d/%m/%Y %H:%M %p')
                dateTime = dtobj.strftime("%Y%m%d %H:%M")
            except Exception:
                pass
            del values['Date']
            del values['Time']

        # Adding the date, time and calibration inside each analysis service result.
        # I'm adding the calibration number here because it is the way we can avoid
        # WINE-76 easly
        for keyword in values.keys():
            values[keyword]['DateTime'] = dateTime
            values[keyword]['Calibration'] = self._calibration

        # First, we must find if already exists a row with results for
        # the same date, in order to take into account replicas, Mean
        # and Standard Deviation
        rows = self.getRawResults().get(resid, [])
        row, rows = self._extractrowbycalibration(rows, self._calibration)
        is_std = values.get('Rep #',{}).get('Rep #','') == 'Sd'
        is_mean = values.get('Rep #',{}).get('Rep #','') == 'Mean'
        if is_std:
            # Add the results of Standard Deviation. For each acode, add
            # the Standard Result
            del values['Rep #']
            for key, value in six.iteritems(values):
                row['Sd-%s' % key] = value
        elif is_mean:
            # Remove the # item and override with new values
            row = values
            del row['Rep #']
        else:
            # Override with new values
            row = values
        rows.append(row)
        isfirst = True
        for row in rows:
            WinescanCSVParser._addRawResult(self, resid, row, isfirst)
            isfirst = False

    def _extractrowbycalibration(self, rows=[], calidx=0):
        outrows = []
        target = {}
        for row in rows:
            # We are getting the rows' calibration. It was saved inside each row
            dtrow = row[row.keys()[0]].get('Calibration',0)
            if dtrow == calidx:
                target = row
            else:
                outrows.append(row)
        return target, outrows


class WinescanFT120Importer(WinescanImporter):

    def getKeywordsToBeExcluded(self):
        return ['Product']
