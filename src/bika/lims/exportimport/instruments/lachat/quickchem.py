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

""" LaChat QuickChem FIA
"""
import json
import logging
import re
import traceback

from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.exportimport.instruments.utils import \
    (get_instrument_import_override,
     get_instrument_import_ar_allowed_states)
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

logger = logging.getLogger(__name__)

title = "LaChat QuickChem FIA"


class LaChatQuickCheckFIAParser(InstrumentCSVResultsFileParser):
    """ Instrument Parser
    """

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._resultsheader = []
        self._numline = 0

    def _parseline(self, line):
        if self._end_header is False:
            return self.parse_headerline(line)
        else:
            return self.parse_resultsline(line)

    def parse_headerline(self, line):
        """ Parses header lines
        """
        if self._end_header is True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split(',')]
        if splitted[1] == 'Sample ID':
            self._resultsheader = splitted
            self._end_header = True
        return 0

    def parse_resultsline(self, line):
        """
        """

        splitted = [token.strip() for token in line.split(',')]
        if self._end_header:
            # in Sample ID column, we may find format: '[SampleID] samplepoint'
            # the part between brackets is the sample id:
            resid = splitted[1]
            if resid.startswith('['):
                # the part between brackets is the sample id:
                resid = resid[1:].split(']')[0]

        rawdict = {'DefaultResult': 'Peak Concentration'}
        rawdict.update(dict(zip(self._resultsheader, splitted)))
        val = re.sub(r"\W", "", rawdict['Analyte Name'])

        # Set DefaultResult to 0.0 if result is "0" or "--" or '' or 'ND'
        result = rawdict[rawdict['DefaultResult']]
        column_name = rawdict['DefaultResult']
        result = self.get_result(column_name, result, line)
        rawdict[rawdict['DefaultResult']] = result
        #
        self._addRawResult(resid, values={val: rawdict}, override=False)
        self.log(
            "End of file reached successfully: ${total_objects} objects, "
            "${total_analyses} analyses, ${total_results} results",
            mapping={"total_objects": self.getObjectsTotalCount(),
                     "total_analyses": self.getAnalysesTotalCount(),
                     "total_results": self.getResultsTotalCount()}
        )

    def get_result(self, column_name, result, line):
        result = str(result)
        if result.startswith('--') or result == '' or result == 'ND':
            return 0.0

        if api.is_floatable(result):
            result = api.to_float(result)
            return result > 0.0 and result or 0.0
        self.err("No valid number ${result} in column (${column_name})",
                 mapping={"result": result,
                          "column_name": column_name},
                 numline=self._numline, line=line)
        return


class Importer(AnalysisResultsImporter):
    """ Instrument Importer
    """

    def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,

                                         override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Import Form
    """
    form = request.form
    # form['file'] sometimes returns a list
    infile = form['instrument_results_file'][0] if \
        isinstance(form['instrument_results_file'], list) \
        else form['instrument_results_file']
    # fileformat = form['instrument_results_file_format']
    override = form['results_override']
    artoapply = form['artoapply']

    instrument = form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))

    parser = LaChatQuickCheckFIAParser(infile)
    status = get_instrument_import_ar_allowed_states(artoapply)
    over = get_instrument_import_override(override)

    importer = Importer(parser=parser,
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


class Export(BrowserView):
    """ Writes worksheet analyses to a CSV file for LaChat QuickChem FIA.
        Sends the CSV file to the response for download by the browser.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, analyses):
        uc = getToolByName(self.context, 'uid_catalog')
        instrument = self.context.getInstrument()
        norm = getUtility(IIDNormalizer).normalize
        filename = '{}-{}.csv'.format(self.context.getId(),
                                      norm(instrument.getDataInterface()))

        # write rows, one per Sample, including including refs and duplicates.
        # Start Column A at 1 or 9? (the examples given used 9, no clues.)
        # If routine analysis, Column B is the AR ID + sample type.
        # If Reference analysis, Column B is the Ref Sample.
        # If Duplicate analysis, column B is the Worksheet.
        # Column C is the well number
        # Column D empty
        # Column E should always be 1 (2 indicates a duplicate from the same cup)
        layout = self.context.getLayout()
        rows = []
        # tmprows = []
        col_a = 1
        result = ''
        # We don't want to include every single slot!  Just one entry
        # per AR, Duplicate, or Control.
        used_ids = []
        for x, row in enumerate(layout):
            a_uid = row['analysis_uid']
            c_uid = row['container_uid']
            analysis = uc(UID=a_uid)[0].getObject() if a_uid else None
            container = uc(UID=c_uid)[0].getObject() if c_uid else None
            if row['type'] == 'a':
                if 'a{}'.format(container.id) in used_ids:
                    continue
                used_ids.append('a{}'.format(container.id))
                # col_a (sample id) has a weird format, but it matches
                # the examples we are given, so it is true:
                samplepoint = container.getSamplePoint()
                sp_title = samplepoint.Title() if samplepoint else ''
                col_b = '[{}] {}'.format(container.id, sp_title)
                col_c = str(row['position'])
                col_d = ''
                col_e = '1'
            elif row['type'] in 'bcd':
                refgid = analysis.getReferenceAnalysesGroupID()
                if 'bcd{}'.format(refgid) in used_ids:
                    continue
                used_ids.append('bcd{}'.format(refgid))
                col_b = refgid
                col_c = str(row['position'])
                col_d = ''
                col_e = '1'
            rows.append(','.join([str(col_a), col_b, col_c, col_d, col_e]))
            col_a += 1
        result += '\r\n'.join(rows)

        # stream to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)
