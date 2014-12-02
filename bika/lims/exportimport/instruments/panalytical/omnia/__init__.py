#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Omnia Axios XRF
"""
from datetime import datetime
from bika.lims.utils import to_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

class AxiosXrfCSVMultiParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []
        self.columns_name = False #To know if the next line contains
                                  #analytic's columns name


    def _parseline(self, line):
        # Process the line differenly if it pertains at header or results block
        if self._end_header == False:
            sline = line.strip(',')
            return self.parse_headerline(sline)
        else:
            return self.parse_resultline(line)

    def splitLine(self, line):
        # If pertains at header it split the line by ':' and then remove ','
        # Else split by ',' and remove blank spaces
        if self._end_header == False:
            sline = line.split(':')
            return [token.strip(',') for token in sline]

        return [token.strip() for token in line.split(',')]

    def csvDate2BikaDate(self,DateTime):
    #11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        dtobj = datetime.strptime(DateTime,"%d/%m/%Y %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")

    def parse_headerline(self, line):
        #Process incoming header line
        """11/03/2014 14:46:46
        PANalytical
        Results quantitative - Omnian 2013,

        Selected archive:,Omnian 2013
        Number of results selected:,4
        """
        
        # Save each header field (that we know) and its own value in the dict        
        if line.startswith('Results quantitative'):
            line = to_unicode(line)
            if len(self._header) == 0:
                self.err("Unexpected header format", numline=self._numline)
                return -1

            line = line.replace(',', "")
            splitted = line.split(' - ')
            self._header['Quantitative'] = splitted[1]
            return 1

        if line.startswith('Selected archive'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Archive'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)
            return 0

        if line.startswith('Number of'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['NumResults'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)
            return 0

        if line.startswith('Seq.'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1
            #Grab column names
            self._columns = line.split(',')
            self._end_header = True
            return 1

        else:
            self._header['Date'] = line
            return 1



    def parse_resultline(self, line):
        # Process incoming results line
        if not line.strip():
            return 0
        if line.startswith(',,'):
            return 0

        rawdict = {}
        # Split by ","
        splitted = self.splitLine(line.strip(";"))

        errors = ''

        # Adjunt separated values from split by ','
        for idx, result in enumerate(splitted):
            if result.startswith('"'):
                # It means that is the value's firts part
                # Consequently we take second part and append both
                result = (splitted[idx].strip('"') + "," + splitted[idx+1].strip('"'))
                splitted[idx] = result
                splitted.remove(splitted[idx+1])
                
        result_type = ''
        result_sum = ''
        for idx, result in enumerate(splitted):
            if self._columns[idx] == 'Result type':
                result_type = result
            elif self._columns[idx].startswith('Sample name'):
                    rid = result
            elif self._columns[idx].startswith('Seq.'):
                pass
            elif self._columns[idx] == 'Sum':
                    result_sum = result
            else:
                rawdict[self._columns[idx]] = {'DefaultResult':result_type,
                                               # Replace to obtain UK values from default
                                               'Concentration':result.replace(',','.'),
                                               'Sum':result_sum}
        try:
            rawdict['DateTime'] = {'DateTime':self.csvDate2BikaDate(self._header['Date']),
                                   'DefaultValue':'DateTime'}
        except:
            pass
        if not rid:
            self.err("No Sample defined", numline=self._numline)
            return 0

        self._addRawResult(rid, rawdict, True)
        return 0


    def getAttachmentFileType(self):
        return "PANalytical - Omnia Axios XRF"

class AxiosXrfCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._columns = []
        self.columns_name = False #To know if the next line contains
                                  #analytic's columns name

    def _parseline(self, line):
        # Process the line differenly if it pertains at header or results block
        if self._end_header == False:
            sline = line.strip(',')
            return self.parse_headerline(sline)
        else:
            return self.parse_resultline(line)

    def csvDate2BikaDate(self,DateTime):
    #11/03/2014 14:46:46 --> %d/%m/%Y %H:%M %p
        dtobj = datetime.strptime(DateTime,"%d/%m/%Y %H:%M:%S")
        return dtobj.strftime("%Y%m%d %H:%M:%S")

    def splitLine(self, line):
        # If pertains at header it split the line by ':' and then remove ','
        # Else split by ',' and remove blank spaces
        if self._end_header == False:
            sline = line.split(':')
            return [token.strip(',') for token in sline]

        return [token.strip() for token in line.split(',')]

    def parse_headerline(self, line):
        #Process incoming header line
        """
        29/11/2013 10:15:44
        PANalytical
        "Quantification of sample ESFERA CINZA - 1g H3BO3 -  1:0,5 - NO PPC",

        R.M.S.:,"0,035"
        Result status:,
        Sum before normalization:,"119,5 %"
        Normalised to:,"100,0 %"
        Sample type:,Pressed powder
        Initial sample weight (g):,"2,000"
        Weight after pressing (g):,"3,000"
        Correction applied for medium:,No
        Correction applied for film:,No
        Used Compound list:,Oxides
        Results database:,omnian 2013
        Results database in:,c:\panalytical\superq\userdata
        """

        if line.startswith('"Quantification of sample') or line.startswith('Quantification of sample'):
            line = to_unicode(line)
            if len(self._header) == 0:
                self.warn('Unexpected header format', numline=self._numline)
                return -1
            # Remove non important string and double comas to obtein
            # the sample name free
            line = line.replace("Quantification of sample ", "")
            line = line.replace('"', "")
            splitted = line.split(' - ')

            if len(splitted) > 3:# Maybe we don't need this, i could be all the sample's identifier...
                self._header['Sample'] = splitted[0].strip(' ')
                self._header['Quantity'] = splitted[1]
                self._header['????'] = splitted[2]# At present we
                                                  # don't know what
                                                  # is that
                self._header['PPC'] = splitted[3]
            
            elif len(splitted) == 1:
                self._header['Sample'] = splitted[0].replace('Quantification of sample','').strip(' ')

            else:
                self.warn('Unexpected header format', numline=self._numline)
            return 1
        # Save each header field (that we know) and its own value in the dict
        if line.startswith('R.M.S.'):

            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['R.M.S.'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)
            return 0

        if line.startswith('Result status'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Result status'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Sum before normalization'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Sum'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Normalised to'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Normalized'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Sample type'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Sample type'] = splitted[1].strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Initial sample weight (g)'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Initial sample weight'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Weight after pressing (g)'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Weight after pressing'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Correction applied for medium'):
            if len(self._header) == 0:
                self.warn('Unexpected header format', numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Correction medium'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Correction applied for film'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Correction film'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

        if line.startswith('Used Compound list'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Used compound'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0
        if line.startswith('Results database:'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Result database'] = splitted[1].replace('"', '').strip()
            else:
                self.warn('Unexpected header format', numline=self._numline)

            return 0

       
        if self.columns_name:
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1

            #Grab column names
            self._end_header = True
            self._columns = self.splitLine(line)
            return 1

        if line.startswith('Results database in'):
            if len(self._header) == 0:
                self.err("No header found", numline=self._numline)
                return -1
            
            splitted = self.splitLine(line)
            if len(splitted) > 1:
                self._header['Database path'] = splitted[1]+splitted[2]
                self.columns_name = True
            else:
                self.warn('Unexpected header format', numline=self._numline)
                
            return 1
            
        else:
            self._header['Date'] = line
            return 1

    def parse_resultline(self, line):
        # Process incoming results line
        if not line.strip():
            return 0

        rawdict = {}
        # Split by ","
        splitted = self.splitLine(line.strip(";"))
        # Look to know if the first value is an enumerate field
        try:
            int(splitted[0])
            rawdict["num"] = splitted[0]
            splitted = splitted[1:]
        except ValueError:
            pass

        # Enumerate the list to obtain: [(0,data0),(1,data1),...]
        e_splitted = list(enumerate(splitted))
        errors = ''

        com = False
        for idx, result in e_splitted:
            if result.startswith('"'):
                # It means that is the first value part
                # Consequently we take second part and append both
                result = (e_splitted[idx][1].strip('"') + "," + e_splitted[idx+1][1].strip('"'))
                e_splitted[idx] = (idx,result)
                e_splitted.remove(e_splitted[idx+1])
                com = True
                rawdict[self._columns[idx]] = result
                conc = self._columns[idx] # Main value's name
                                
               
            elif com:# We have rm the 2nd part value, consequently we
                    # need to decrement idx
                if len(self._columns) <= idx-1:
                    self.err("Orphan value in column ${index}",
                             mapping={"index":str(idx + 1)},
                             numline=self._numline)
                    break
                # We add and sync the result with its value's name
                rawdict[self._columns[idx-1]] = result

            else:
                if len(self._columns) <= idx:
                    self.err("Orphan value in column ${index}",
                             mapping={"index":str(idx + 1)},
                             numline=self._numline)
                    break
                rawdict[self._columns[idx]] = result

        aname = rawdict[self._columns[0]]# The fisrt column is analytic name  
        if not aname:
            self.err("No Analysis Name defined", numline=self._numline)
            return 0
        elif aname == "<H>":
            # <H> maybe is data error header? We need more examples...
            errors = rawdict.get('Compound')
            notes = rawdict.get('Calibration')
            rawdict['Notes'] = notes

        rid = self._header['Sample']
        if not rid:
            self.err("No Sample defined", numline=self._numline)
            return 0

        notes = rawdict.get('Notes', '')
        notes = "Notes: %s" % notes if notes else ''
        rawdict['DefaultResult'] = conc
        # Replace to obtain UK values from default
        rawdict[conc] = rawdict[conc].replace(',','.')
        rawdict['Remarks'] = ' '.join([errors, notes])
        rawres = self.getRawResults().get(rid, [])
        raw = rawres[0] if len(rawres) > 0 else {}
        raw[aname] = rawdict
        if not 'DateTime' in raw:
            try:
                raw['DateTime'] = {'DateTime':self.csvDate2BikaDate(self._header['Date']),
                                   'DefaultValue':'DateTime'}
            except:
                pass
            
        self._addRawResult(rid, raw, True)
        return 0


    def getAttachmentFileType(self):
        return "PANalytical - Omnia Axios XRF"


class AxiosXrfImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
