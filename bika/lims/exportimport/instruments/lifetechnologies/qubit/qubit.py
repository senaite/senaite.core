""" Life Technologies Qubit
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import QuBitCSVParser, QuBitImporter
import json
import traceback

title = "Life Technolgies - Qubit"


def Import(context, request):
    """ Read qubit analysis results
    """
    infile = request.form['filename']
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    sample = request.form.get('sample', 'requestid')
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the suitable parser
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    elif fileformat == 'csv':
        analysis = request.form.get('analysis', None)
        if analysis:
            parser = QuBitCSVParser(infile, analysis)
        else:
            errors.append(t(_("No analysis selected")))
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

        importer = QuBitImporter(parser=parser,
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
