""" Axios 'XRF'
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class AxiosXrfCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []

    def _parseline(self, line):
        #sline = line.replace('"', '').strip()
        if self._end_header == False:
            #sline = line.replace('"', '').strip()
            sline = line.strip(',')
            #sline = sline.strip(',')
            return self.parse_headerline(sline)
        else:
            return self.parse_resultline(sline)

    def splitLine(self, line):
        if self._end_header == False:#Només per la bateria de headers, no pel uantification
            sline = split(':')
            return [token.strip(',') for token in sline]
        
        return [token.strip() for token in line.split('\t')]

    def parse_headerline(self, line):
        """ Parses header lines
29/11/2013 10:15:44
PANalytical
Quantification of sample ESFERA CINZA - 1g H3BO3 -  1:0,5 - NO PPC
            
        """
        
        if line.startswith('"Quantification of sample'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1
            
            self.line = self.line.strip('"')
            splitted = self.line.split('-')

            if len(splitted) > 3:
                splitted[0] = splitted[0].strip()
                sample_name_l = splitted[0].split(' ')[3:]
                sample_name = str()
                for token in sample_name_l:
                    sample_name += " " + token
                self._header['Sample'] = sample_name
                self._header['Quantity'] = splitted[1]
                self._header['????'] = splitted[3]
                self._header['PPC'] = splitted[4]
                
            else:
                self.warn(_('Unexpected header format'))

            return 1 #Llegia la segona linia amb 1?

        if line.startswith('R.M.S.'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Result status'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Sum before normalization'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Normalised to'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Sample type'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Initial sample weight (g)'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Weight after pressing (g)'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Correction applied for medium'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Correction applied for film'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Used Compound list'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0
        if line.startswith('Results database'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Time'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0
        
        if line.startswith('Results database in'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Database path'] = splitted[1]+plitted[2]
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 1

        if line.startswith('Analyte'):
            # Analyte,Calibration,Compound,Concentration,Unit,Calculation,Status
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            #Grab column names
            self._end_header = True
            self._columns = self.splitLine(line)
            return 1

        else:
            #Agafar la data

    def parse_resultline(self, line):
        # Sample/ctrl ID    Pat/Ctr/cAl    Test name    Test type
        if not line.strip():
            return 0

        rawdict = {}
        splitted = self.splitLine(line)
        for idx, result in enumerate(splitted):
            if len(self._columns) <= idx:
                self.err(_("Orphan value in column %s, line %s") \
                         % (str(idx + 1), self._numline))
                break
            rawdict[self._columns[idx]] = result

        acode = rawdict.get('Test name', '')
        if not acode:
            self.err(_("No Analysis Code defined, line %s") % (self.num_line))
            return 0

        rid = rawdict.get('Sample/ctrl ID')
        if not rid:
            self.err(_("No Sample ID defined, line %s") % (self.num_line))
            return 0

        errors = rawdict.get('Errors', '')
        errors = "Errors: %s" % errors if errors else ''
        notes = rawdict.get('Notes', '')
        notes = "Notes: %s" % notes if notes else ''
        rawdict[acode]=rawdict['Result']
        rawdict['DefaultResult'] = acode
        rawdict['Remarks'] = ' '.join([errors, notes])
        rawres = self.getRawResults().get(rid, [])
        raw = rawres[0] if len(rawres) > 0 else {}
        raw[acode] = rawdict
        self._addRawResult(rid, raw, True)
        return 0


    def getAttachmentFileType(self):
        return "PANalytical - Axios_XRF XRF CSV"


class AxiosXrfImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
