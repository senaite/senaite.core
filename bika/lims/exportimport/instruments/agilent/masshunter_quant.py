""" Agilent's 'Masshunter Quant'
"""
from DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import tmpID
from cStringIO import StringIO
from datetime import datetime
from operator import itemgetter
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import csv
import json
import plone
import zope
import zope.event

title = "Agilent - Masshunter Quant"


def Import(context, request):
    """ Read Agilent's Masshunter Quant analysis results
    """
    infile = request.form['amhq_file']
    fileformat = request.form['amhq_format']
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if fileformat == 'csv':
        parser = MasshunterQuantCSVParser(infile)
    else:
        errors.append(_("Unrecognized file format '%s'") % fileformat)

    if parser:
        # Load the importer
        importer = MasshunterQuantImporter(parser, context)
        importer.process()
        errors = importer.errors
        logs = importer.logs

    results = {'errors': errors, 'log': logs}

    return json.dumps(results)


class LogErrorReportable:

    def __init__(self):
        self._errors = []
        self._logs = []

    def err(self, msg, numline=None, line=None):
        self.msg(self._errors, msg, numline, line)
        self.msg(self._logs, _("[ERROR] ") + msg, numline, line)

    def warn(self, msg, numline=None, line=None):
        self.msg(self._logs, _("[WARN] ") + msg, numline, line)

    def log(self, msg, numline=None, line=None):
        self.msg(self._logs, msg, numline, line)

    def msg(self, array, msg, numline=None, line=None):
        prefix = ''
        suffix = ''
        if numline:
            prefix = "[%s] " % numline
        if line:
            suffix = ": %s" % line
        array.append(prefix + msg + suffix)

    @property
    def errors(self):
        """ Return an array with the errors thrown during the file processing
        """
        return self._errors

    @property
    def logs(self):
        """ Return an array with logs generated during the file processing
        """
        return self._logs


class MasshunterQuantParser(LogErrorReportable):

    def __init__(self, infile):
        LogErrorReportable.__init__(self)
        self._infile = infile
        self._header = {}
        self._sequences = []
        self._quantitationresults = {}

    def getInputFile(self):
        return self._infile

    def parse(self):
        raise NotImplementedError

    def getHeader(self):
        return self._header

    def getSequences(self):
        return self._sequences

    def getQuantitationResults(self):
        return self._quantitationresults


class MasshunterQuantCSVParser(MasshunterQuantParser):

    HEADERKEY_BATCHINFO = 'Batch Info'
    HEADERKEY_BATCHDATAPATH = 'Batch Data Path'
    HEADERKEY_ANALYSISTIME = 'Analysis Time'
    HEADERKEY_ANALYSTNAME = 'Analyst Name'
    HEADERKEY_REPORTTIME = 'Report Time'
    HEADERKEY_REPORTERNAME = 'Reporter Name'
    HEADERKEY_LASTCALIBRATION = 'Last Calib Update'
    HEADERKEY_BATCHSTATE = 'Batch State'
    SEQUENCETABLE_KEY = 'Sequence Table'
    SEQUENCETABLE_HEADER_DATAFILE = 'Data File'
    SEQUENCETABLE_PRERUN = 'prerunrespchk.d'
    SEQUENCETABLE_MIDRUN = 'mid_respchk.d'
    SEQUENCETABLE_POSTRUN = 'post_respchk.d'
    SEQUENCETABLE_NUMERICHEADERS = ('Inj Vol',)
    QUANTITATIONRESULTS_KEY = 'Quantification Results'
    QUANTITATIONRESULTS_TARGETCOMPOUND = 'Target Compound'
    QUANTITATIONRESULTS_HEADER_DATAFILE = 'Data File'
    QUANTITATIONRESULTS_PRERUN = 'prerunrespchk.d'
    QUANTITATIONRESULTS_MIDRUN = 'mid_respchk.d'
    QUANTITATIONRESULTS_POSTRUN = 'post_respchk.d'
    QUANTITATIONRESULTS_NUMERICHEADERS = ('Resp', 'ISTD Resp', 'Resp Ratio',
                                          'Final Conc', 'Exp Conc', 'Accuracy')
    QUANTITATIONRESULTS_COMPOUNDCOLUMN = 'Compound'
    COMMAS = ',,,,,,,,,,,,,,,,,'

    def __init__(self, csv):
        MasshunterQuantParser.__init__(self, csv)
        self._end_header = False
        self._end_sequencetable = False
        self._sequencesheader = []
        self._quantitationresultsheader = []
        self._numline = 0

    def parse(self):
        """ Processes the input CSV file
        """
        infile = self.getInputFile()
        self.log(_("Parsing file ") + " %s (%s)" % (infile.filename, infile.name))
        jump = 0
        for line in infile.readlines():
            self._numline += 1
            if jump == -1:
                # Something went wrong. Finish
                self.err(_("File processing finished due to critical errors"))
                return False
            if jump > 0:
                # Jump some lines
                jump -= 1
                continue

            if not line or not line.strip():
                continue

            line = line.strip()
            if self._end_header == False:
                jump = self.parse_headerline(line)

            elif self._end_sequencetable == False:
                jump = self.parse_sequencetableline(line)

            else:
                jump = self.parse_quantitationesultsline(line)

        self.log(_("End of file reached"))
        if (len(self._quantitationresults) == 0):
            self.err(_("No quantitation results found"))
            return False

        return True

    def parse_headerline(self, line):
        """ Parses header lines

            Header example:
            Batch Info,2013-03-20T07:11:09.9053262-07:00,2013-03-20T07:12:55.5280967-07:00,2013-03-20T07:11:07.1047817-07:00,,,,,,,,,,,,,,
            Batch Data Path,D:\MassHunter\Data\130129\QuantResults\130129LS.batch.bin,,,,,,,,,,,,,,,,
            Analysis Time,3/20/2013 7:11 AM,Analyst Name,Administrator,,,,,,,,,,,,,,
            Report Time,3/20/2013 7:12 AM,Reporter Name,Administrator,,,,,,,,,,,,,,
            Last Calib Update,3/20/2013 7:11 AM,Batch State,Processed,,,,,,,,,,,,,,
            ,,,,,,,,,,,,,,,,,
        """
        if self._end_header == True:
            # Header already processed
            return 0

        if line.startswith(self.SEQUENCETABLE_KEY):
            self._end_header = True
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1
            return 0

        splitted = [token.strip() for token in line.split(',')]

        # Batch Info,2013-03-20T07:11:09.9053262-07:00,2013-03-20T07:12:55.5280967-07:00,2013-03-20T07:11:07.1047817-07:00,,,,,,,,,,,,,,
        if splitted[0] == self.HEADERKEY_BATCHINFO:
            if self.HEADERKEY_BATCHINFO in self._header:
                self.warn(_("Header Batch Info already found. Discarding"),
                         self._numline, line)
                return 0

            self._header[self.HEADERKEY_BATCHINFO] = []
            for i in range(len(splitted) - 1):
                if splitted[i + 1]:
                    self._header[self.HEADERKEY_BATCHINFO].append(splitted[i + 1])

        # Batch Data Path,D:\MassHunter\Data\130129\QuantResults\130129LS.batch.bin,,,,,,,,,,,,,,,,
        elif splitted[0] == self.HEADERKEY_BATCHDATAPATH:
            if self.HEADERKEY_BATCHDATAPATH in self._header:
                self.warn(_("Header Batch Data Path already found. Discarding"),
                         self._numline, line)
                return 0;

            if splitted[1]:
                self._header[self.HEADERKEY_BATCHDATAPATH] = splitted[1]
            else:
                self.warn(_("Batch Data Path not found or empty"), self._numline, line)

        # Analysis Time,3/20/2013 7:11 AM,Analyst Name,Administrator,,,,,,,,,,,,,,
        elif splitted[0] == self.HEADERKEY_ANALYSISTIME:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%m/%d/%Y %I:%M %p")
                    self._header[self.HEADERKEY_ANALYSISTIME] = d
                except ValueError:
                    self.err(_("Invalid Analysis Time format"), self._numline, line)
            else:
                self.warn(_("Analysis Time not found or empty"), self._numline, line)

            if splitted[2] and splitted[2] == self.HEADERKEY_ANALYSTNAME:
                if splitted[3]:
                    self._header[self.HEADERKEY_ANALYSTNAME] = splitted[3]
                else:
                    self.warn(_("Analyst Name not found or empty"), self._numline, line)
            else:
                self.err(_("Analyst Name not found"), self._numline, line)

        # Report Time,3/20/2013 7:12 AM,Reporter Name,Administrator,,,,,,,,,,,,,,
        elif splitted[0] == self.HEADERKEY_REPORTTIME:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%m/%d/%Y %I:%M %p")
                    self._header[self.HEADERKEY_REPORTTIME] = d
                except ValueError:
                    self.err(_("Invalid Report Time format"), self._numline, line)
            else:
                self.warn(_("Report time not found or empty"), self._numline, line)

            if splitted[2] and splitted[2] == self.HEADERKEY_REPORTERNAME:
                if splitted[3]:
                    self._header[self.HEADERKEY_REPORTERNAME] = splitted[3]
                else:
                    self.warn(_("Reporter Name not found or empty"), self._numline, line)
            else:
                self.err(_("Reporter Name not found"), self._numline, line)

        # Last Calib Update,3/20/2013 7:11 AM,Batch State,Processed,,,,,,,,,,,,,,
        elif splitted[0] == self.HEADERKEY_LASTCALIBRATION:
            if splitted[1]:
                try:
                    d = datetime.strptime(splitted[1], "%m/%d/%Y %I:%M %p")
                    self._header[self.HEADERKEY_LASTCALIBRATION] = d
                except ValueError:
                    self.err(_("Invalid Last Calibration time format"), self._numline, line)
            else:
                self.warn(_("Last Calibration time not found or empty"), self._numline, line)

            if splitted[2] and splitted[2] == self.HEADERKEY_BATCHSTATE:
                if splitted[3]:
                    self._header[self.HEADERKEY_BATCHSTATE] = splitted[3]
                else:
                    self.warn(_("Batch state not found or empty"), self._numline, line)
            else:
                self.err(_("Batch state not found"), self._numline, line)

        return 0

    def parse_sequencetableline(self, line):
        """ Parses sequence table lines

            Sequence Table example:
            Sequence Table,,,,,,,,,,,,,,,,,
            Data File,Sample Name,Position,Inj Vol,Level,Sample Type,Acq Method File,,,,,,,,,,,
            prerunrespchk.d,prerunrespchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            DSS_Nist_L1.d,DSS_Nist_L1,P1-A2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            DSS_Nist_L2.d,DSS_Nist_L2,P1-B2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            DSS_Nist_L3.d,DSS_Nist_L3,P1-C2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            UTAK_DS_L1.d,UTAK_DS_L1,P1-D2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            UTAK_DS_L2.d,UTAK_DS_L2,P1-E2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            mid_respchk.d,mid_respchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            UTAK_DS_low.d,UTAK_DS_Low,P1-F2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            FDBS_31.d,FDBS_31,P1-G2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            FDBS_32.d,FDBS_32,P1-H2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            LS_60-r001.d,LS_60,P1-G12,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            LS_60-r002.d,LS_60,P1-G12,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            LS_61-r001.d,LS_61,P1-H12,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            LS_61-r002.d,LS_61,P1-H12,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            post_respchk.d,post_respchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            ,,,,,,,,,,,,,,,,,
        """

        # Sequence Table,,,,,,,,,,,,,,,,,
        # prerunrespchk.d,prerunrespchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
        # mid_respchk.d,mid_respchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
        # ,,,,,,,,,,,,,,,,,
        if line.startswith(self.SEQUENCETABLE_KEY) \
            or line.startswith(self.SEQUENCETABLE_PRERUN) \
            or line.startswith(self.SEQUENCETABLE_MIDRUN) \
            or self._end_sequencetable == True:

            # Nothing to do, continue
            return 0

        # Data File,Sample Name,Position,Inj Vol,Level,Sample Type,Acq Method File,,,,,,,,,,,
        if line.startswith(self.SEQUENCETABLE_HEADER_DATAFILE):
            self._sequencesheader = [token.strip() for token in line.split(',') if token.strip()]
            return 0

        # post_respchk.d,post_respchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
        # Quantitation Results,,,,,,,,,,,,,,,,,
        if line.startswith(self.SEQUENCETABLE_POSTRUN) \
            or line.startswith(self.QUANTITATIONRESULTS_KEY) \
            or line.startswith(self.COMMAS):
            self._end_sequencetable = True
            if len(self._sequences) == 0:
                self.err(_("No Sequence Table found"), self._numline)
                return -1

            # Jumps 2 lines:
            # Data File,Sample Name,Position,Inj Vol,Level,Sample Type,Acq Method File,,,,,,,,,,,
            # prerunrespchk.d,prerunrespchk,Vial 3,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
            return 2

        # DSS_Nist_L1.d,DSS_Nist_L1,P1-A2,-1.00,,Sample,120824_VitD_MAPTAD_1D_MRM_practice.m,,,,,,,,,,,
        splitted = [token.strip() for token in line.split(',')]
        sequence = {}
        for colname in self._sequencesheader:
            sequence[colname] = ''

        for i in range(len(splitted)):
            token = splitted[i]
            if i < len(self._sequencesheader):
                colname = self._sequencesheader[i]
                if token and colname in self.SEQUENCETABLE_NUMERICHEADERS:
                    try:
                        sequence[colname] = float(token)
                    except ValueError:
                        self.warn(_("No valid number %s in column %s (%s)") %
                                    (token, str(i+1), colname), self._numline, line)
                        sequence[colname] = token
                else:
                    sequence[colname] = token
            elif token:
                self.err(_("Orphan value in column %s (%s)") % (str(i+1), token),
                           self._numline, line)
        self._sequences.append(sequence)

    def parse_quantitationesultsline(self, line):
        """ Parses quantitation result lines

            Quantitation results example:
            Quantitation Results,,,,,,,,,,,,,,,,,
            Target Compound,25-OH D3+PTAD+MA,,,,,,,,,,,,,,,,
            Data File,Compound,ISTD,Resp,ISTD Resp,Resp Ratio, Final Conc,Exp Conc,Accuracy,,,,,,,,,
            prerunrespchk.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,5816,274638,0.0212,0.9145,,,,,,,,,,,
            DSS_Nist_L1.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,6103,139562,0.0437,1.6912,,,,,,,,,,,
            DSS_Nist_L2.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,11339,135726,0.0835,3.0510,,,,,,,,,,,
            DSS_Nist_L3.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,15871,141710,0.1120,4.0144,,,,,,,,,,,
            mid_respchk.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,4699,242798,0.0194,0.8514,,,,,,,,,,,
            DSS_Nist_L3-r002.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,15659,129490,0.1209,4.3157,,,,,,,,,,,
            UTAK_DS_L1-r001.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,29846,132264,0.2257,7.7965,,,,,,,,,,,
            UTAK_DS_L1-r002.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,28696,141614,0.2026,7.0387,,,,,,,,,,,
            post_respchk.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,5022,231748,0.0217,0.9315,,,,,,,,,,,
            ,,,,,,,,,,,,,,,,,
            Target Compound,25-OH D2+PTAD+MA,,,,,,,,,,,,,,,,
            Data File,Compound,ISTD,Resp,ISTD Resp,Resp Ratio, Final Conc,Exp Conc,Accuracy,,,,,,,,,
            prerunrespchk.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,6222,274638,0.0227,0.8835,,,,,,,,,,,
            DSS_Nist_L1.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,1252,139562,0.0090,0.7909,,,,,,,,,,,
            DSS_Nist_L2.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,3937,135726,0.0290,0.9265,,,,,,,,,,,
            DSS_Nist_L3.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,826,141710,0.0058,0.7697,,,,,,,,,,,
            mid_respchk.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,7864,242798,0.0324,0.9493,,,,,,,,,,,
            DSS_Nist_L3-r002.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,853,129490,0.0066,0.7748,,,,,,,,,,,
            UTAK_DS_L1-r001.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,127496,132264,0.9639,7.1558,,,,,,,,,,,
            UTAK_DS_L1-r002.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,135738,141614,0.9585,7.1201,,,,,,,,,,,
            post_respchk.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,6567,231748,0.0283,0.9219,,,,,,,,,,,
            ,,,,,,,,,,,,,,,,,
        """

        # Quantitation Results,,,,,,,,,,,,,,,,,
        # prerunrespchk.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,5816,274638,0.0212,0.9145,,,,,,,,,,,
        # mid_respchk.d,25-OH D3+PTAD+MA,25-OH D3d3+PTAD+MA,4699,242798,0.0194,0.8514,,,,,,,,,,,
        # post_respchk.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,6567,231748,0.0283,0.9219,,,,,,,,,,,
        # ,,,,,,,,,,,,,,,,,
        if line.startswith(self.QUANTITATIONRESULTS_KEY) \
            or line.startswith(self.QUANTITATIONRESULTS_PRERUN) \
            or line.startswith(self.QUANTITATIONRESULTS_MIDRUN) \
            or line.startswith(self.QUANTITATIONRESULTS_POSTRUN) \
            or line.startswith(self.COMMAS):

            # Nothing to do, continue
            return 0

        # Data File,Compound,ISTD,Resp,ISTD Resp,Resp Ratio, Final Conc,Exp Conc,Accuracy,,,,,,,,,
        if line.startswith(self.QUANTITATIONRESULTS_HEADER_DATAFILE):
            self._quantitationresultsheader = [token.strip() for token in line.split(',') if token.strip()]
            return 0

        # Target Compound,25-OH D3+PTAD+MA,,,,,,,,,,,,,,,,
        if line.startswith(self.QUANTITATIONRESULTS_TARGETCOMPOUND):
            # New set of Quantitation Results
            splitted = [token.strip() for token in line.split(',')]
            if splitted[1]:
                self._quantitationresults[splitted[1]] = []
            else:
                self.warn(_("No Target Compound found"), self._numline, line)
            return 0

        # DSS_Nist_L1.d,25-OH D2+PTAD+MA,25-OH D3d3+PTAD+MA,1252,139562,0.0090,0.7909,,,,,,,,,,,
        splitted = [token.strip() for token in line.split(',')]
        quantitation = {}
        for colname in self._quantitationresultsheader:
            quantitation[colname] = ''

        for i in range(len(splitted)):
            token = splitted[i]
            if i < len(self._quantitationresultsheader):
                colname = self._quantitationresultsheader[i]
                if token and colname in self.QUANTITATIONRESULTS_NUMERICHEADERS:
                    try:
                        quantitation[colname] = float(token)
                    except ValueError:
                        self.warn(_("No valid number %s in column %s (%s)") %
                                    (token, str(i+1), colname), self._numline, line)
                        quantitation[colname] = token
                else:
                    quantitation[colname] = token
            elif token:
                self.err(_("Orphan value in column % (%s)") % (str(i+1), token),
                           self._numline, line)

        if self.QUANTITATIONRESULTS_COMPOUNDCOLUMN in quantitation:
            compound = quantitation[self.QUANTITATIONRESULTS_COMPOUNDCOLUMN]
            if compound not in self._quantitationresults.keys():
                self._quantitationresults[compound] = []
            self._quantitationresults[compound].append(quantitation)
        else:
            self.err(_("Value for column '%s' not found") \
                     % self.QUANTITATIONRESULTS_COMPOUNDCOLUMN,
                     self._numline, line)


class MasshunterQuantImporter(LogErrorReportable):

    def __init__(self, masshunterquantparser, context):
        self._parser = masshunterquantparser
        self.context = context

    def getParser(self):
        return self._parser

    def process(self):
        parsed = self._parser.parse()
        self._errors = self._parser.errors
        self._logs = self._parser.logs
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.bac = getToolByName(self.context, 'bika_analysis_catalog')
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bc = getToolByName(self.context, 'bika_catalog')
        resultfield = 'Final Conc'
        attached = []

        if parsed:

            # Process the parsed data
            header = self._parser.getHeader()
            sequences = self._parser.getSequences()
            quantitationresults = self._parser.getQuantitationResults()

            # 1. Foreach Sample in sequences, obtain the Sample Name
            # 2. Foreach Sequence, retrieve the Data File
            # 3. Foreach Data File, retrieve the result line from Quant results
            for acode, results in quantitationresults.iteritems():

                #HACK
                if acode == '25-OH D3+PTAD+MA':
                    acode = 'D3'
                elif acode == '25-OH D2+PTAD+MA':
                    acode = 'D2'

                service = self.bsc(getKeyword=acode)
                if not service:
                    self.err(_('Service keyword %s not found') % acode)
                    continue

                for resline in results:
                    datafile = resline.get('Data File', '')
                    if not datafile:
                        self.err(_("No Data File found for quantitation result %s") % str(resline))
                        continue

                    # get the sequences for each quantitative result
                    seqs = [sequence for sequence in sequences \
                            if sequence.get('Data File', '') == \
                            resline.get('Data File', '')]

                    if len(seqs) == 0:
                        self.err(_("No sample found for quantitative result %s") % datafile)
                        continue
                    elif len(seqs) > 1:
                        self.err(_("More than one sequence found for quantitative result %s") % datafile)
                        continue

                    # Find the sample for that sequence
                    sampleid = seqs[0].get("Sample Name", "")
                    if not sampleid:
                        self.err(_("No Sample Name found for sequence %s") % str(seqs[0]))
                        continue

                    ar = self._findAnalysisRequest(sampleid)
                    if not ar:
                        continue

                    # Look for the desired analysis in the AR
                    analyses = ar.getAnalyses()
                    analyses = [analysis.getObject() for analysis in ar.getAnalyses() \
                                if analysis.getObject().getKeyword() == acode]
                    if len(analyses) == 0:
                        self.err(_("Analysis %s not found in Analysis "
                                     "Request %s. Discarding result for sample"
                                     "%s") % (acode, ar.id, sampleid))
                        continue

                    analysis = None
                    for an in analyses:
                        if (an.getResult()):
                            self.warn(_("Analysis %s from Analysis Request %s "
                                       "already have results. Discarding "
                                       "result for sample %s") %
                                     (acode, ar.id, sampleid))
                            continue

                        analysis = an

                    if not analysis:
                        self.err(_("There's no Analysis %s without result "
                                     "in Analysis Request %s. Discarding "
                                     "result for sample %s") %
                                     (acode, ar.id, sampleid))
                        continue

                    # If analysis has interim fields, check with agilent's 
                    # columns
                    interimsout = []
                    interims = analysis.getInterimFields()
                    for interim in interims:
                        keyword = interims['keyword']
                        if resline.get(keyword, ''):
                            interimsout.append({'keyword': interims['keyword'],
                                                'value':resline.get(keyword)})
                        else:
                            interimsout.append(interim)
                    if interimsout:
                        analysis.setInterimFields(interimsout)

                    elif resline.get(resultfield, ''):
                        # set the result
                        analysis.setResult(resline.get(resultfield))

                    else:
                        self.warn(_("Empty '%s' result for sample %s.") %
                                  (resultfield, sampleid))
                        continue

                    # Attach the file to the AR
                    if ar.UID() not in attached:

                        # Create the AttachmentType for CSV if not exists
                        attachmentType = self.bsc(portal_type="AttachmentType", title="CSV")
                        if len(attachmentType) == 0:
                            folder = self.context.bika_setup.bika_attachmenttypes
                            _id = folder.invokeFactory('AttachmentType', id=tmpID())
                            obj = folder[_id]
                            obj.edit(title="CSV",
                                     description="Comma Separated Values file")
                            obj.unmarkCreationFlag()
                            renameAfterCreation(obj)
                            attuid = obj.UID()
                        else:
                            attuid = attachmentType[0].UID

                        attachmentid = ar.generateUniqueId('Attachment')
                        ar.aq_parent.invokeFactory(id=attachmentid, type_name="Attachment")
                        attachment = ar.aq_parent._getOb(attachmentid)
                        attachment.edit(
                            AttachmentFile=self._parser.getInputFile().read(),
                            AttachmentType=attuid,
                            AttachmentKeys="Agilent - Masshunter Quant")
                        attachment.reindexObject()

                        others = ar.getAttachment()
                        attachments = []
                        for other in others:
                            attachments.append(other.UID())
                        attachments.append(attachment.UID())
                        ar.setAttachment(attachments)
                        attached.append(ar.UID())

            return True

        else:
            self.err(_("Unable to import data. Parser finished with errors"))
            return False

    def _findAnalysisRequest(self, sampleid):
        """ Searches for an analysis request.
            Looks for analysis requests which have a sample with a SampleID,
            UID or ClientSampleID that matches with the argument sampleid.
            Only retrieves the AR if its status is 'sample_received',
            'attachment_due' or 'to_be_verified'
            If no AR found, returns None
            If more than one AR found, returns None
        """

        # Get the AR from the sample
        # review_state: sample_registered, to_be_sampled, sampled,
        # to_be_preserved, sample_due, sample_received,
        # attachment_due, to_be_verified, verified, published, invalid
        allowed_states = ['sample_received', 'attachment_due',
                          'to_be_verified']
        ars = self.bc(portal_type='AnalysisRequest',
                      getSampleID=sampleid,
                      review_state=allowed_states)
        if len(ars) == 0:
            ars = self.bc(portal_type='AnalysisRequest',
                          getSampleUID=sampleid,
                          review_state=allowed_states)

            if len(ars) == 0:
                ars = self.bc(portal_type='AnalysisRequest',
                              getClientSampleID=sampleid,
                              review_state=allowed_states)

                if len(ars) == 0:
                    self.err(_("No Analysis Request with '%s' states "
                               "found for sample %s") %
                             (str(allowed_states), sampleid))
                    return None

        if len(ars) > 1:
            self.err(_("More than one Analysis Request found for sample %s")
                     % sampleid)
            return None

        return ars[0].getObject()
