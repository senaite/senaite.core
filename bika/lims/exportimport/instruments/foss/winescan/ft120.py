""" FOSS 'Winescan FT120'
"""
from bika.lims import bikaMessageFactory as _
from . import WinescanImporter, WinescanCSVParser
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
    warns = []
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

        importer = WinescanFT120Importer(parser=parser,
                                         context=context,
                                         idsearchcriteria=sam,
                                         allowed_ar_states=status,
                                         allowed_analysis_states=None,
                                         override=over)
        importer.process()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


class WinescanFT120CSVParser(WinescanCSVParser):

    def __init__(self, csv):
        WinescanCSVParser.__init__(self, csv)
        self._omitrows = ['Calibration',
                         'Pilot definition',
                         'Pilot test',
                         'Zero setting',
                         'Zero correction']
        self._omit = False
        self._parsedresults = {}

    def getAttachmentFileType(self):
        return "FOSS Winescan FT120 CSV"

    def _parseline(self, line):
        if self.currentheader and line in self._omitrows:
            self.currentheader = None
            self._omit = True
        elif line.startswith('Sample Id') or not self._omit:
            self._omit = False
            return WinescanCSVParser._parseline(self, line)
        return 0

    def _addRawResult(self, resid, values={}, override=False):
        replicate = '1'

        ''' Structure of values dict (dict entry for each analysis/field):

            {'ALC': {'ALC': '13.55',
                     'DefaultResult': 'ALC',
                     'Remarks': ''},
             'CO2': {'CO2': '0.66',
                     'DefaultResult': 'CO2',
                     'Remarks': ''},
             'Date': {'Date': '21/11/2013',
                      'DefaultResult': 'Date',
                      'Remarks': ''},
             'Malo': {'DefaultResult': 'Malo',
                      'Malo': '0.26',
                      'Remarks': ''},
             'Meth': {'DefaultResult': 'Meth',
                      'Meth': '0.58',
             'Rep #': {'DefaultResult': 'Rep #',
                      'Remarks': '',
                      'Rep #': '1'}
            }
        '''

        if 'Rep #' in values.keys():
            replicate = values['Rep #']['Rep #']

        replicates = {}
        if resid in self._parsedresults.keys():
            replicates = self._parsedresults[resid]

        if replicate in replicates.keys():
            self.err(_("Replicate '%s' already exists for '%s', line %s") % \
                      (replicate, resid, self._numline))
            return
        else:
            del values['Rep #']
            replicates[replicate] = values
        self._parsedresults[resid] = replicates

    def resume(self):
        """ Looks for, Replicates, Mean and Sd values foreach Sample.
            If Mean and Sd values found for a sample, removes the replicates
            and creates a unique rawresult for that sample with Mean and Sd.
            If there's a sample with replicates but without Mean, logs an error
            and removes the sample from rawresults
        """
        self._emptyRawResults()
        for objid, replicates in self._parsedresults.iteritems():
            results = {}
            if 'Mean' in replicates.keys():
                results = replicates['Mean']
                for key, value in replicates.get('Sd', {}).iteritems():
                    results['Sd-%s' % key] = value

            elif len(replicates) > 1:
                self.err(_("More than one replica with no Mean for '%s'") % \
                           objid)
                continue

            elif len(replicates) < 1:
                self.err(_("No replicas found for '%s'") % objid)
                continue

            else:
                results = replicates.itervalues().next()

            WinescanCSVParser._addRawResult(self, objid, results, True)
        return WinescanCSVParser.resume(self)


class WinescanFT120Importer(WinescanImporter):

    def getKeywordsToBeExcluded(self):
        return ['Date', 'Time', 'Product']
