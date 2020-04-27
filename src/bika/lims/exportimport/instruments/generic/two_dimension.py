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

""" 2-Dimensional-CSV
"""
from bika.lims import bikaMessageFactory as _
from bika.lims import api
import json
import re
from bika.lims.exportimport.instruments.utils import \
    (get_instrument_import_override,
     get_instrument_import_ar_allowed_states)
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
import traceback
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING

title = "2-Dimensional-CSV"


def Import(context, request):
    """ Read Dimensional-CSV analysis results
    """
    form = request.form
    # TODO form['file'] sometimes returns a list
    infile = form['instrument_results_file'][0] if \
        isinstance(form['instrument_results_file'], list) else \
        form['instrument_results_file']
    artoapply = form['artoapply']
    override = form['results_override']

    instrument = form.get('instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    parser = TwoDimensionCSVParser(infile)
    status = get_instrument_import_ar_allowed_states(artoapply)
    over = get_instrument_import_override(override)
    importer = TwoDimensionImporter(parser=parser,
                                    context=context,
                                    allowed_ar_states=status,
                                    allowed_analysis_states=None,
                                    override=over,
                                    instrument_uid=instrument,
                                    form=form)
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


def is_keyword(kw):
    bsc = api.get_tool('bika_setup_catalog')
    return len(bsc(getKeyword=kw))


def find_analyses(ar_or_sample):
    """ This function is used to find keywords that are not on the analysis
        but keywords that are on the interim fields.

        This function and is is_keyword function should probably be in
        resultsimport.py or somewhere central where it can be used by other
        instrument interfaces.
    """
    bc = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    ar = bc(portal_type='AnalysisRequest', id=ar_or_sample)
    if len(ar) == 0:
        ar = bc(portal_type='AnalysisRequest', getClientSampleID=ar_or_sample)
    if len(ar) == 1:
        obj = ar[0].getObject()
        analyses = obj.getAnalyses(full_objects=True)
        return analyses
    return []


def get_interims_keywords(analysis):
    interims = api.safe_getattr(analysis, 'getInterimFields')
    return map(lambda item: item['keyword'], interims)


def find_analysis_interims(ar_or_sample):
    """ This function is used to find keywords that are not on the analysis
        but keywords that are on the interim fields.

        This function and is is_keyword function should probably be in
        resultsimport.py or somewhere central where it can be used by other
        instrument interfaces.
    """
    interim_fields = list()
    for analysis in find_analyses(ar_or_sample):
        keywords = get_interims_keywords(analysis)
        interim_fields.extend(keywords)
    return list(set(interim_fields))


def find_kw(ar_or_sample, kw):
    """ This function is used to find keywords that are not on the analysis
        but keywords that are on the interim fields.

        This function and is is_keyword function should probably be in
        resultsimport.py or somewhere central where it can be used by other
        instrument interfaces.
    """
    for analysis in find_analyses(ar_or_sample):
        if kw in get_interims_keywords(analysis):
            return analysis.getKeyword()
    return None


class TwoDimensionCSVParser(InstrumentCSVResultsFileParser):

    QUANTITATIONRESULTS_NUMERICHEADERS = ('Title8', 'Title9', 'Title31',
                                          'Title32', 'Title41', 'Title42',
                                          'Title43',)

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._keywords = []
        self._quantitationresultsheader = []
        self._numline = 0

    def _parseline(self, line):
        if self._end_header:
            return self.parse_resultsline(line)
        return self.parse_headerline(line)

    def parse_headerline(self, line):
        """ Parses header lines

            Keywords example:
            Keyword1, Keyword2, Keyword3, ..., end
        """
        if self._end_header is True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split(',')]
        if splitted[-1] == 'end':
            self._keywords = splitted[1:-1]  # exclude the word end
            self._end_header = True
        return 0

    def parse_resultsline(self, line):
        """ Parses result lines
        """
        splitted = [token.strip() for token in line.split(',')]

        if splitted[0] == 'end':
            return 0

        blank_line = [i for i in splitted if i != '']
        if len(blank_line) == 0:
            return 0

        quantitation = {}
        list_of_interim_results = []
        # list_of_interim_results is a list that will have interim fields on
        # the current line so that we don't have to call self._addRawResult
        # for the same interim fields, ultimately we want a dict that looks
        # like quantitation = {'AR': 'AP-0001-R01', 'interim1': 83.12, 'interim2': 22.3}
        # self._addRawResult(quantitation['AR'],
        #                    values={kw: quantitation},
        #                    override=False)
        # We use will one of the interims to find the analysis in this case new_kw which becomes kw
        # kw is the analysis keyword which sometimes we have to find using the interim field
        # because we have the result of the interim field and not of the analysis

        found = False  # This is just a flag used to check values in list_of_interim_results
        clean_splitted = splitted[1:-1]  # First value on the line is AR
        for i in range(len(clean_splitted)):
            token = clean_splitted[i]
            if i < len(self._keywords):
                quantitation['AR'] = splitted[0]
                # quantitation['AN'] = self._keywords[i]
                quantitation['DefaultResult'] = 'resultValue'
                quantitation['resultValue'] = token
            elif token:
                self.err("Orphan value in column ${index} (${token})",
                         mapping={"index": str(i + 1),
                                  "token": token},
                         numline=self._numline, line=line)

            result = quantitation[quantitation['DefaultResult']]
            column_name = quantitation['DefaultResult']
            result = self.get_result(column_name, result, line)
            quantitation[quantitation['DefaultResult']] = result

            kw = re.sub(r"\W", "", self._keywords[i])
            if not is_keyword(kw):
                new_kw = find_kw(quantitation['AR'], kw)
                if new_kw:
                    quantitation[kw] = quantitation['resultValue']
                    del quantitation['resultValue']
                    for interim_res in list_of_interim_results:
                        if kw in interim_res:
                            # Interim field already in quantitation dict
                            found = True
                            break
                    if found:
                        continue
                    interims = find_analysis_interims(quantitation['AR'])
                    # pairing headers(keywords) and their values(results) per line
                    keyword_value_dict = dict(zip(self._keywords, clean_splitted))
                    for interim in interims:
                        if interim in keyword_value_dict:
                            quantitation[interim] = keyword_value_dict[interim]
                            list_of_interim_results.append(quantitation)
                    kw = new_kw
                    kw = re.sub(r"\W", "", kw)

            self._addRawResult(quantitation['AR'],
                               values={kw: quantitation},
                               override=False)
            quantitation = {}
            found = False

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



class TwoDimensionImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid='', form=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
