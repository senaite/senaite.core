""" FOSS 'Winescan FT120'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.foss.winescan import WinescanImporter,\
    WinescanCSVParser
import json

title = "FOSS - Winescan FT120"


def Import(context, request):
    """ Read FOSS's Winescan FT120 analysis results
    """
    infile = request.form['wsf_file']
    fileformat = request.form['wsf_format']
    artoapply = request.form['wsf_artoapply']
    override = request.form['wsf_override']
    sample = request.form.get('wsf_sample', 'requestid')
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = WinescanFT120CSVParser(infile)
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

        importer = WinescanImporter(parser=parser,
                                    context=context,
                                    idsearchcriteria=sam,
                                    allowed_ar_states=status,
                                    allowed_analysis_states=None,
                                    override=over)
        importer.process()
        errors = importer.errors
        logs = importer.logs

    results = {'errors': errors, 'log': logs}

    return json.dumps(results)


class WinescanFT120CSVParser(WinescanCSVParser):

    def getAttachmentFileType(self):
        return "FOSS Winescan FT120 CSV"
