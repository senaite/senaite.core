
""" Alere Pima "CD4"
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import AlerePimaImporter, AlerePimaSLKParser
import json
import traceback

title = "Alere Pima CD4"


def Import(context, request):
    """ Alere Pima CD4 analysis results
    """
    infile = request.form['alere_pima_cd4_file']
    fileformat = request.form['alere_pima_cd4_format']
    artoapply = request.form['alere_pima_cd4_artoapply']
    override = request.form['alere_pima_cd4_override']
    sample = request.form.get('alere_pima_cd4_sample',
                              'requestid')
    instrument = request.form.get('alere_pima_cd4_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'slk':
        parser = AlerePimacd4SLKParser(infile)
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

        importer = AlerePimaImporter(parser=parser,
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

class AlerePimacd4SLKParser(AlerePimaSLKParser):

    def getAttachmentFileType(self):
        return "Alare Pima CD4"