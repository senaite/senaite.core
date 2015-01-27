""" Thermo Scientific 'Arena 20XT' (The file name for importing staff)
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import ThermoArenaImporter, ThermoArenaRPRCSVParser
import json
import traceback

title = "Thermo Scientific - Arena 20XT"

def Import(context, request):
    """ Thermo Scientific - Arena 20XT analysis results
    """
    infile = request.form['thermoscientific_arena_20XT_file']
    fileformat = request.form['thermoscientific_arena_20XT_format']
    artoapply = request.form['thermoscientific_arena_20XT_artoapply']
    override = request.form['thermoscientific_arena_20XT_override']
    sample = request.form.get('thermoscientific_arena_20XT_sample',
                              'requestid')
    instrument = request.form.get('thermoscientific_arena_20XT_instrument', None)
    errors = []
    logs = []
    warns = []

    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'rpr.csv':
        parser = ThermoArena20XTRPRCSVParser(infile)
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

        importer = ThermoArena20XTImporter(parser=parser,
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

class ThermoArena20XTImporter(ThermoArenaImporter):

    def getKeywordsToBeExcluded(self):
        return []

class ThermoArena20XTRPRCSVParser(ThermoArenaRPRCSVParser):
    def getAttachmentFileType(self):
        return "Thermo Scientific Arena 20XT RPR.CSV"