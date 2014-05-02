#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
            return self.parse_resultline(line)

    def splitLine(self, line):
        if self._end_header == False:#Només per la bateria de headers, no pel uantification
            sline = line.split(':')
            return [token.strip(',') for token in sline]

        return [token.strip() for token in line.split(',')]

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
            
            line = line.replace("Quantification of sample ", "")
            line = line.replace('"', "")
            splitted = line.split(' - ')
           
            if len(splitted) > 3:
                sample_name = splitted[0]
                                
                self._header['Sample'] = sample_name.strip(' ')
                self._header['Quantity'] = splitted[1]
                self._header['????'] = splitted[2]
                self._header['PPC'] = splitted[3]

            else:
                self.warn(_('Unexpected header format'))

            return 1

        if line.startswith('R.M.S.'):

            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['R.M.S.'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Result status'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Result status'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Sum before normalization'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Sum'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Normalised to'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Normalized'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Sample type'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Sample type'] = splitted[1].strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Initial sample weight (g)'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Initial sample weight'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Weight after pressing (g)'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Weight after pressing'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Correction applied for medium'):
            if len(self._header) == 0:
                self.err(_("Unexpected header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Correction medium'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Correction applied for film'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Correction film'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Used Compound list'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Used compound'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0
        if line.startswith('Results database:'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Result database'] = splitted[1].replace('"', '').strip()
            else:
                self.warn(_('Unexpected header format'), self._numline)

            return 0

        if line.startswith('Results database in'):
            if len(self._header) == 0:
                self.err(_("No header found"), self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Database path'] = splitted[1]+splitted[2]
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
            self._header['Date'] = line
            return 1

    def parse_resultline(self, line):
        # Analyte,Calibration,Compound,Concentration,Unit,Calculation,Status
        if not line.strip():
            return 0
        
        rawdict = {}
        splitted = self.splitLine(line.strip(";"))
        e_splitted = list(enumerate(splitted))
        errors = ''
                
        for idx, result in e_splitted:
            if result.startswith('"'): #Ajuntem els resultats
                result = (e_splitted[idx][1].strip('"') + "," + e_splitted[idx+1][1].strip('"'))
                a = e_splitted[idx][0]
                e_splitted[idx] = (a,result)
                e_splitted.remove(e_splitted[idx+1])

            if len(self._columns) <= idx:
                self.err(_("Orphan value in column %s, line %s") \
                             % (str(idx + 1), self._numline))
                break
            rawdict[self._columns[idx]] = result
        
        aname = rawdict.get('Analyte', '')
        if not aname:
            self.err(_("No Analysis Name defined, line %s") % (self.num_line))
            return 0
        elif aname == "<H>":
            errors = rawdict.get('Compound')
            notes = rawdict.get('Calibration')

        rid = self._header['Sample']
        if not rid:
            self.err(_("No Sample defined, line %s") % (self.num_line))
            return 0

        notes = rawdict.get('Notes', '')
        notes = "Notes: %s" % notes if notes else ''
        rawdict['DefaultResult'] = 'Concentration'
        rawdict['Concentration'] = rawdict['Concentration'].replace(',','.')
        rawdict['Remarks'] = ' '.join([errors, notes])
        rawres = self.getRawResults().get(rid, [])
        raw = rawres[0] if len(rawres) > 0 else {}
        raw[aname] = rawdict
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
