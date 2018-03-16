# -*- coding: utf-8 -*-
""" Metler Toledo DL55
"""
import json
import re
import traceback

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.utils import \
    (get_instrument_import_search_criteria,
     get_instrument_import_override,
     get_instrument_import_ar_allowed_states)
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from openpyxl import load_workbook

title = "Metler Toledo DL55"


class MetlerToledoDL55Parser(InstrumentResultsFileParser):
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'XLSX')

    def parse(self):
        """ parse the data
        """

        wb = load_workbook(self.getInputFile())
        sheet = wb.worksheets[0]

        sample_id = None
        cnt = 0
        for row in sheet.rows:

            # sampleid is only present in first row of each sample.
            # any rows above the first sample id are ignored.
            if row[1].value:
                sample_id = row[1].value
            if not sample_id:
                continue

            # If no keyword is present, this row is skipped.
            if len(row) < 7 or not isinstance(row[6].value, basestring):
                continue
            # keyword is stripped of non-word characters
            keyword = re.sub(r"\W", "", row[6].value)

            # result is floatable or error
            result = row[4].value
            try:
                float(result)
            except ValueError:
                self.log(
                    "Error in sample '" + sample_id + "': " + "Result for '" +
                    keyword + "' is not a number " + "(" + result + ").")
                continue

            # Compose dict for importer.  No interim values, just a result.
            rawdict = {
                'DefaultResult': 'Result',
                'Result': result,
            }
            result = rawdict[rawdict['DefaultResult']]
            column_name = rawdict['DefaultResult']
            cnt += 1
            result = self.get_result(column_name, result, cnt)
            rawdict[rawdict['DefaultResult']] = result
            self._addRawResult(sample_id,
                               values={keyword: rawdict},
                               override=False)
        return True

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
    """ Importer
    """

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         idsearchcriteria,
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
    sample = form.get('sample', 'requestid')
    instrument = form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))

    parser = MetlerToledoDL55Parser(infile)
    status = get_instrument_import_ar_allowed_states(artoapply)
    over = get_instrument_import_override(override)
    sam = get_instrument_import_search_criteria(sample)

    importer = Importer(parser=parser,
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
