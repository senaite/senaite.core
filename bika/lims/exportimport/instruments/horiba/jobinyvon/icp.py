""" Horiba Jobin-Yvon ICP
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from parser import HoribaJobinYvonCSVParser
from importer import HoribaJobinYvonImporter
import json
import traceback

title = "Horiba Jobin-Yvon - ICP"


class Importer:
    def __call__(self, context, request):
        """ Horiba Jobin-Yvon ICPanalysis results
        """
        self.request = request

        self.errors = []
        self.logs = []
        self.warns = []

        infile = self.request.form['data_file']
        if not hasattr(infile, 'filename'):
            self.errors.append(_("No file selected"))
            return self.ret()
        parser = HoribaJobinYvonICPCSVParser(infile)

        # Load the most suitable parser according to file extension/options/etc...
        format = self.request.form['format']
        parser = None
        if not hasattr(infile, 'filename'):
            self.errors.append(_("No file selected"))
        elif format == 'csv':
            parser = HoribaJobinYvonCSVParser(infile)
        else:
            self.errors.append(t(_("Unrecognized file format ${format}",
                                   mapping={"format": format})))

        if parser:

            ar_states = self.get_allowed_ar_states()
            over = self.get_overrides()
            crit = self.get_id_search_criteria()
            instrument = request.form.get('instrument', None)

            importer = HoribaJobinYvonICPImporter(parser=parser,
                                                  context=context,
                                                  idsearchcriteria=crit,
                                                  allowed_ar_states=ar_states,
                                                  allowed_analysis_states=None,
                                                  override=over,
                                                  instrument_uid=instrument)

            exception_string = ''
            try:
                importer.process()
            except:
                exception_string = traceback.format_exc()
            self.errors = importer.errors
            self.logs = importer.logs
            self.warns = importer.warns
            if exception_string:
                self.errors.append(exception_string)

        return self.ret()

    def ret(self):
        errors = []
        for e in self.errors:
            if e not in errors:
                errors.append(e)
        warns = []
        for e in self.warns:
            if e not in warns:
                warns.append(e)
        results = {'errors': errors,
                   'log': self.logs,
                   'warns': warns}
        return json.dumps(results)

    def get_allowed_ar_states(self):
        artoapply = self.request.form['artoapply']
        # Load the importer
        ar_states = ['sample_received', 'attachment_due', 'to_be_verified']
        if artoapply == 'received':
            ar_states = ['sample_received']
        elif artoapply == 'received_tobeverified':
            ar_states = ['sample_received', 'attachment_due', 'to_be_verified']
        return ar_states

    def get_overrides(self):
        override = self.request.form['override']
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]
        else:
            over = [False, False]
        return over

    def get_id_search_criteria(self):
        sample = self.request.form.get('sample', 'requestid')
        if sample == 'requestid':
            sam = ['getRequestID']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']
        else:
            sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
        return sam


Import = Importer()


class HoribaJobinYvonICPCSVParser(HoribaJobinYvonCSVParser):
    def getAttachmentFileType(self):
        return "Horiba JobinYvon ICP"


class HoribaJobinYvonICPImporter(HoribaJobinYvonImporter):
    def getKeywordsToBeExcluded(self):
        return []
