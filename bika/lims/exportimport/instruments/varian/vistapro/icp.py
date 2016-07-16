# -*- coding: utf-8 -*-
""" Varian Vista-PRO ICP
"""
import csv
import logging

from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
import json
import traceback

logger = logging.getLogger(__name__)

title = "Varian Vista-PRO ICP"


class VistaPROICPParser(InstrumentResultsFileParser):
    """ Vista-PRO Parser
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'CSV')

    def parse(self):
        """ CSV Parser
        """

        reader = csv.DictReader(self.getInputFile(), delimiter=',')

        for n, row in enumerate(reader):

            resid = row.get("Solution Label", "").strip()

            # Service Keyword
            element = row.get("Element", "").split()[0]

            rawdict = row
            rawdict['DefaultResult'] = 'Soln Conc'

            self._addRawResult(resid, values={element: rawdict}, override=False)


class VistaPROICPImporter(AnalysisResultsImporter):
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
    infile = request.form['varian_vistapro_icp_file']
    fileformat = request.form['varian_vistapro_icp_format']
    artoapply = request.form['varian_vistapro_icp_artoapply']
    override = request.form['varian_vistapro_icp_override']
    sample = request.form.get('varian_vistapro_icp_sample', 'requestid')
    instrument = request.form.get('varian_vistapro_icp_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = VistaPROICPParser(infile)
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

        sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getRequestID']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = VistaPROICPImporter(parser=parser,
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
