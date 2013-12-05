""" FOSS 'Winescan Auto'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser, AnalysisResultsImporter
import json

title = "FOSS - Winescan Auto"


def Import(context, request):
    """ Read FOSS's Winescan Auto analysis results
    """
    infile = request.form['wsa_file']
    fileformat = request.form['wsa_format']
    artoapply = request.form['wsa_artoapply']
    override = request.form['wsa_override']
    sample = request.form.get('wsa_sample', 'requestid')
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'name'):
        errors.append(_("No file selected"))
    elif fileformat == 'csv':
        parser = WinescanAutoCSVParser(infile)
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

        importer = WinescanAutoImporter(parser=parser,
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


class WinescanAutoCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self.currentheader = None

    def getAttachmentFileType(self):
        return "FOSS Winescan Auto CSV"

    def _parseline(self, line):
        # Sample Id,,,Ash,Ca,Ethanol,ReducingSugar,VolatileAcid,TotalAcid
        if line.startswith('Sample Id'):
            self.currentheader = [token.strip() for token in line.split(',')]
            return 0

        if self.currentheader:
            # AR-01177-01,,,0.9905,22.31,14.11,2.95,0.25,5.11,3.54,3.26,-0.36
            splitted = [token.strip() for token in line.split(',')]
            resid = splitted[0]
            if not resid:
                self.err(_("No Sample ID found, line %s") % self._numline)
                self.currentHeader = None
                return 0

            duplicated = []
            values = {}
            for idx, result in enumerate(splitted):
                if idx == 0:
                    continue

                if len(self.currentheader) <= idx:
                    self.err(_("Orphan value in column %s, line %s") \
                             % (str(idx + 1), self._numline))
                    continue

                keyword = self.currentheader[idx]
                if not result and not keyword:
                    continue

                if result and not keyword:
                    self.err(_("Orphan value in column %s, line %s") \
                             % (str(idx + 1), self._numline))
                    continue

                if not result:
                    self.warn(_("Empty result for %s, column %s, line %s") % \
                              (keyword, str(idx + 1), self._numline))

                if keyword in values.keys():
                    self.err(_("Duplicated result for '%s', line %s") \
                             % (keyword, self._numline))
                    duplicated.append(keyword)
                    continue

                values[keyword] = {'DefaultResult': keyword, keyword: result}

            # Remove duplicated results
            outvals = {key: value for key, value in values.items() \
                       if key not in duplicated}

            # add result
            self._addRawResult(resid, outvals, True)
            self.currentHeader = None
            return 0

        self.err(_("No header found for line %s"), self._numline)
        return 0


class WinescanAutoImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None):
        AnalysisResultsImporter.__init__(self, parser, context, idsearchcriteria,
                                         override, allowed_ar_states,
                                         allowed_analysis_states)



































