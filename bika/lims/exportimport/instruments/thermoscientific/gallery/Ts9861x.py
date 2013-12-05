""" Thermo Scientific 'Gallery 9861x'
"""
from bika.lims import bikaMessageFactory as _
from . import ThermoGalleryImporter, ThermoGalleryTSVParser
import json

title = "Thermo Scientific - Gallery 9861x"


def Import(context, request):
    """ Thermo Scientific - Gallery 9861x analysis results
    """
    infile = request.form['thermoscientific_gallery_9861x_file']
    fileformat = request.form['thermoscientific_gallery_9861x_format']
    artoapply = request.form['thermoscientific_gallery_9861x_artoapply']
    override = request.form['thermoscientific_gallery_9861x_override']
    sample = request.form.get('thermoscientific_gallery_9861x_sample',
                              'requestid')
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'tsv_40':
        parser = ThermoGallery9861xTSVParser(infile)
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

        importer = ThermoGallery9861xImporter(parser=parser,
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


class ThermoGallery9861xTSVParser(ThermoGalleryTSVParser):

    def getAttachmentFileType(self):
        return "Thermo Scientific Gallery 9861x TSV/XLS"


class ThermoGallery9861xImporter(ThermoGalleryImporter):

    def getKeywordsToBeExcluded(self):
        return []
