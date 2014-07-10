""" FOSS 'Winescan Auto'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import WinescanImporter, WinescanCSVParser
import json
import traceback

title = "FOSS - Winescan Auto"


def Import(context, request):
    """ Read FOSS's Winescan Auto analysis results
    """
    infile = request.form['wsa_file']
    fileformat = request.form['wsa_format']
    artoapply = request.form['wsa_artoapply']
    override = request.form['wsa_override']
    sample = request.form.get('wsa_sample', 'requestid')
    instrument = request.form.get('wsa_instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    elif fileformat == 'csv':
        parser = WinescanAutoCSVParser(infile)
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

        importer = WinescanAutoImporter(parser=parser,
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


class WinescanAutoCSVParser(WinescanCSVParser):

    def getAttachmentFileType(self):
        return "FOSS Winescan Auto CSV"


class WinescanAutoImporter(WinescanImporter):

    def getKeywordsToBeExcluded(self):
        return ['Info', 'ResultType', 'BottleType', 'Remark']
