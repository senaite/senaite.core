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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import traceback
from collections import OrderedDict
from collections import defaultdict

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.exportimport.instruments.importer import \
    AnalysisResultsImporter
from senaite.core.exportimport.instruments.parser import \
    InstrumentCSVResultsFileParser
from senaite.core.exportimport.instruments.utils import \
    get_instrument_import_ar_allowed_states
from senaite.core.exportimport.instruments.utils import \
    get_instrument_import_override

title = "2-Dimensional-CSV"


def Import(context, request):
    """Read Dimensional-CSV analysis results
    """
    form = request.form
    infile = form["instrument_results_file"]
    if isinstance(infile, list):
        infile = infile[0]
    artoapply = form["artoapply"]
    results_override = form["results_override"]
    instrument_uid = form.get("instrument", None)

    errors = []
    logs = []

    if not hasattr(infile, "filename"):
        errors.append(_("No file selected"))
    parser = TwoDimensionCSVParser(infile)
    allowed_sample_states = get_instrument_import_ar_allowed_states(artoapply)
    override = get_instrument_import_override(results_override)
    importer = AnalysisResultsImporter(
        parser=parser, context=context,
        override=override, allowed_sample_states=allowed_sample_states,
        allowed_analysis_states=None, instrument_uid=instrument_uid)

    tbex = ""

    try:
        importer.process()
    except Exception:
        tbex = traceback.format_exc()

    errors = importer.errors
    logs = importer.logs
    warns = importer.warns

    if tbex:
        errors.append(tbex)

    results = {"errors": errors, "log": logs, "warns": warns}
    return json.dumps(results)


class TwoDimensionCSVParser(InstrumentCSVResultsFileParser):
    """Generic 2-Dimensional CSV parser
    """
    def __init__(self, csv):
        super(TwoDimensionCSVParser, self).__init__(csv)
        self._keywords = []

    def _parseline(self, line):
        """Parse a line from the input CSV

        :param line: CSV text line
        :returns: number of lines to be jumped or -1 if an error occured
        """
        if self._numline == 1:
            return self.parse_headerline(line)
        return self.parse_resultsline(line)

    def splitline(self, line):
        """Split the line into a list of tokens

        Additionally, this method removes all obsolete "end" markers

        :param line: CSV text line
        :returns: List of tokens
        """
        splitted = super(TwoDimensionCSVParser, self).splitline(line)
        # handle empty lines
        if not filter(None, splitted):
            return []
        # BBB: wipe off any "end" markers from the end
        elif splitted and splitted[-1] == "end":
            return splitted[0:-1]
        # BBB: Treat lines starting with "end" as empty
        elif splitted and splitted[0] == "end":
            return []
        return splitted

    def parse_headerline(self, line):
        """Parses header lines
        """
        splitted = self.splitline(line)

        if not splitted:
            return -1

        # always treat the first line as the header line
        if self._numline == 1:
            # keywords begin by convention after the ID column
            self._keywords = splitted[1:]
        return 0

    def parse_resultsline(self, line):
        """Parse a single result line from the CSV

        Example:
        'S-001,,"0,95","<0,80","<0,40","<0,40", ...'

        NOTE: We might get analysis and interim results mixed!

        Furthermore, interim results might appear *before* an analysis result.

        Therefore, this parser must unfortunately do more than simple parsing.
        It must find and wakup the sample of the line, check the contained
        analyses and group interims to their analysis keyword.

        The final structure shoud be a dictionary that maps the analysis
        keyword to a results dictionary that contains both, analysis and
        interim results:

        {
            'Ca': {
                'DefaultResult': 'resultValue',
                'resultValue':   '0.95',
                'interim1':      '<0.8',
                'interim2':      '<0.4',
                ...
            },
        }

        The importer will then set the analysis result, interim results and any
        additional key that matches a field, e.g. "Remarks" to the analysis
        object.

        However, setting any other value besides the analysis or interim
        results might be ambiguous, e.g. setting a Remarks in the CSV applies
        to all analyses.
        """
        splitted = self.splitline(line)

        # skip empty result lines
        if not splitted:
            return 0

        # sample identifier should be always on first position
        sid = splitted[0]

        # combine the splitted line with the header columns
        # but excluding the sample ID in the first column
        pairs = zip(self._keywords, splitted[1:])

        sample = self.query_sample(sid)
        if not sample:
            # might be a reference sample or any other custom type
            # -> just take the raw result w/o further sample specific handling
            for kw, result in pairs:
                res = {"DefaultResult": "resultValue", "resultValue": result}
                self._addRawResult(sid, values={kw: res}, override=False)
            return 0

        # NOTE: the code is sample specific and only exists to group interim
        # fields into the result dicts of their corresponding analyses.
        # It might make sense to shift that logic into the importer, but this
        # requires some additional refactoring of the logic.

        # fetch all analyses of the sample
        analyses = sample.getAnalyses()
        # get interim mapping for the analyses
        interim_mapping = self.get_interim_mapping(analyses)
        # extract the analysis keywords
        analysis_keywords = map(lambda x: x.getKeyword, analyses)
        # create a mapping from analysis keyword -> results dict
        results = OrderedDict([(x, {}) for x in analysis_keywords])

        for num, pair in enumerate(pairs):
            keyword, result = pair

            if keyword in analysis_keywords:
                # we found an analysis keyword result
                results[keyword]["DefaultResult"] = "resultValue"
                results[keyword]["resultValue"] = result
            elif keyword in interim_mapping.keys():
                # keyword is an analysis interim
                # -> add it to the results dict of it belonging analysis
                for k in interim_mapping[keyword]:
                    results[k][keyword] = result
            else:
                # Keyword belongs neither to an analysis nor to an interim
                # -> we add it below all known analysis keywords as raw value
                for k, v in results.items():
                    results[k][keyword] = result

        for kw, result in results.items():
            # skip empty result sets
            if not result:
                continue
            self._addRawResult(sid, values={kw: result}, override=False)

    def query_sample(self, identifier):
        """Query a sample by identifier

        :param identifier: Sample Identifier
        :returns: Sample object or None
        """
        catalog = api.get_tool(SAMPLE_CATALOG)
        id_query = {"getId": identifier}
        csid_query = {"getClientSampleID": identifier}
        results = catalog(id_query) or catalog(csid_query)
        if len(results) != 1:
            return None
        return api.get_object(results[0])

    def get_interim_keywords_for(self, analysis):
        """Return all interim keywords for the given analysis
        """
        interims = analysis.getInterimFields()
        return list(map(lambda x: x.get("keyword"), interims))

    def get_interim_mapping(self, analyses):
        """Create a mapping of interim -> analysis keywords
        """
        mapping = defaultdict(list)
        for analysis in analyses:
            analysis = api.get_object(analysis)
            keyword = analysis.getKeyword()
            for interim in self.get_interim_keywords_for(analysis):
                mapping[interim].append(keyword)
        return mapping
