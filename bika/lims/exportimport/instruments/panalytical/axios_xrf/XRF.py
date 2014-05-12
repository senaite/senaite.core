""" PANalytical - Axios_XRF XRF
"""
from bika.lims import bikaMessageFactory as _
from . import AxiosXrfImporter, AxiosXrfCSVParser
import json
import traceback

title = "PANalytical - Axios XRF"


def Import(context, request):
    """ PANalytical - Axios_XRF XRF analysis results
    """
    infile = request.form['panalytical_axios_xrf_file']
    fileformat = request.form['panalytical_axios_xrf_format']
    artoapply = request.form['panalytical_axios_xrf_artoapply']
    override = request.form['panalytical_axios_xrf_override']
    sample = request.form.get('panalytical_axios_xrf_sample',
                              'requestid')
    instrument = request.form.get('panalytical_axios_xrf_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = AxiosXrfCSVParser(infile)
    else:
        errors.append(_("Unrecognized file format '%s'") % fileformat)

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

        importer = AxiosXrfImporter(parser=parser,
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
