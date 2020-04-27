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

""" Varian Vista-PRO ICP
"""
import logging
import re

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.exportimport.instruments.utils import \
    (get_instrument_import_override,
     get_instrument_import_ar_allowed_states)
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
from bika.lims import bikaMessageFactory as _
import json
import traceback

logger = logging.getLogger(__name__)

title = "Varian Vista-PRO ICP"


class VistaPROICPParser(InstrumentCSVResultsFileParser):
    """ Vista-PRO Parser
    """
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._resultsheader = []
        self._numline = 0

    def _parseline(self, line):
        if self._end_header:
            return self.parse_resultsline(line)
        return self.parse_headerline(line)

    def parse_headerline(self, line):
        """ Parses header lines
        """
        if self._end_header is True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split(',')]
        if splitted[0] == 'Solution Label':
            self._resultsheader = splitted
            self._end_header = True
        return 0

    def parse_resultsline(self, line):
        """ CSV Parser
        """

        splitted = [token.strip() for token in line.split(',')]
        if self._end_header:
            resid = splitted[0]
        rawdict = {'DefaultResult': 'Soln Conc'}
        rawdict.update(dict(zip(self._resultsheader, splitted)))
        date_string = "{Date} {Time}".format(**rawdict)
        date_time = DateTime(date_string)
        rawdict['DateTime'] = date_time
        element = rawdict.get("Element", "").replace(" ", "").replace(".", "")

        # Set DefaultResult to 0.0 if result is "0" or "--" or '' or 'ND'
        result = rawdict[rawdict['DefaultResult']]
        column_name = rawdict['DefaultResult']
        result = self.get_result(column_name, result, line)
        rawdict[rawdict['DefaultResult']] = result
        #

        val = re.sub(r"\W", "", element)
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



class VistaPROICPImporter(AnalysisResultsImporter):
    """ Importer
    """

    def __init__(self, parser, context, override,
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

    parser = VistaPROICPParser(infile)
    status = get_instrument_import_ar_allowed_states(artoapply)
    over = get_instrument_import_override(override)

    importer = VistaPROICPImporter(parser=parser,
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
    """ Writes worksheet analyses to a CSV file for Varian Vista Pro ICP.
        Sends the CSV file to the response for download by the browser.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, analyses):
        uc = getToolByName(self.context, 'uid_catalog')
        instrument = self.context.getInstrument()
        norm = getUtility(IIDNormalizer).normalize
        # We use ".sin" extension, but really it's just a little CSV inside.
        filename = '{}-{}.sin'.format(self.context.getId(),
                                      norm(instrument.getDataInterface()))

        # write rows, one per Sample, including including refs and duplicates.
        # COL A:  "sample-id*sampletype-title"  (yes that's a '*').
        # COL B:  "                    ",
        # COL C:  "                    ",
        # COL D:  "                    ",
        # COL E:  1.000000000,
        # COL F:  1.000000,
        # COL G:  1.0000000
        # If routine analysis, COL B is the AR ID + sample type.
        # If Reference analysis, COL B is the Ref Sample.
        # If Duplicate analysis, COL B is the Worksheet.
        lyt = self.context.getLayout()
        lyt.sort(cmp=lambda x, y: cmp(int(x['position']), int(y['position'])))
        rows = []

        # These are always the same on each row
        b = '"                    "'
        c = '"                    "'
        d = '"                    "'
        e = '1.000000000'
        f = '1.000000'
        g = '1.0000000'

        result = ''
        # We don't want to include every single slot!  Just one entry
        # per AR, Duplicate, or Control.
        used_ids = []
        for x, row in enumerate(lyt):
            a_uid = row['analysis_uid']
            c_uid = row['container_uid']
            analysis = uc(UID=a_uid)[0].getObject() if a_uid else None
            container = uc(UID=c_uid)[0].getObject() if c_uid else None
            if row['type'] == 'a':
                if 'a{}'.format(container.id) in used_ids:
                    continue
                used_ids.append('a{}'.format(container.id))
                samplepoint = container.getSamplePoint()
                sp_title = samplepoint.Title() if samplepoint else ''
                a = '"{}*{}"'.format(container.id, sp_title)
            elif row['type'] in 'bcd':
                refgid = analysis.getReferenceAnalysesGroupID()
                if 'bcd{}'.format(refgid) in used_ids:
                    continue
                used_ids.append('bcd{}'.format(refgid))
                a = refgid
            rows.append(','.join([a, b, c, d, e, f, g]))
        result += '\r\n'.join(rows)

        # stream to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)
