""" Eltra CS - 2000
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import EltraCSTSVParser, EltraCSImporter
import json
import traceback

title = "Eltra CS - 2000"


def Import(context, request):
    """ Eltra CS - 2000
    """
    infile = request.form.get('data_file', None)
    fileformat = request.form['format']
    artoapply = request.form['artoapply']
    override = request.form['override']
    sample = request.form.get('sample',
                              'requestid')
    analysis1 = request.form.get('analysis1', None)
    analysis2 = request.form.get('analysis2', None)
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    elif not analysis1 or not analysis2 or analysis1 == '' or analysis2 == '':
        errors.append(_("No Analysis Services defined"))
    elif fileformat == 'tsv':
        parser = EltraCS2000CSVParser(infile, analysis1, analysis2)
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

        importer = EltraCS2000Importer(parser=parser,
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


class EltraCS2000CSVParser(EltraCSTSVParser):
    def getAttachmentFileType(self):
        return "Eltra CS 2000"


class EltraCS2000Importer(EltraCSImporter):
    def getKeywordsToBeExcluded(self):
        return []
