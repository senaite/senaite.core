# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Abbott m2000 Real Time
"""

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

title = "Abbott - m2000 Real Time"


def Import(context, request):
    """
    Abbot m2000 Real Time results import. This function handles
    requests when the user uploads a file and submits. It gets
    request parameters and creates a Parser object based on the
    parameters' values. After that, and based on that parser object,
    it creates an Importer object called importer that will process
    the selected file and try to import the results.
    """
    # Read the values the user has specified for the parameters
    # that appear in the import view of the current instrument
    # and that are defined in the instrument interface template
    infile = request.form['filename']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    sample = request.form.get('sample',
                              'requestid')
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'tsv':
        parser = Abbottm2000rtTSVParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Select parameters for the importer from the values
        # just read from the import view
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

        sam = ['getId', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getId']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        # Crate importer with the defined parser as well as the
        # rest of defined parameters and try to import the
        # results from the specified file
        importer = Abbottm2000rtImporter(parser=parser,
                                         context=context,
                                         idsearchcriteria=sam,
                                         allowed_ar_states=status,
                                         allowed_analysis_states=None,
                                         override=over,
                                         instrument_uid=instrument)
        tbex = ''
        try:
            # run the parser and save results
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


class Abbottm2000rtTSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, infile):
        InstrumentCSVResultsFileParser.__init__(self, infile)
        self._separator = '\t'

    def _parseline(self, line):
        """
        Results log file line Parser. The parse method implemented in
        InstrumentCSVResultsFileParser calls this method for each line
        in the results file that is to be parsed.
        :param line: a to parse
        :returns: the number of rows to jump and parse the next data line or
        return the code error -1
        """
        split_line = line.split(self._separator)
        print split_line
        return 0


class Abbottm2000rtImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
