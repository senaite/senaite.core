# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" 2-Dimensional-CSV
"""
from DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import api
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
import re
import zope
import zope.event
from bika.lims.exportimport.instruments.resultsimport import InstrumentCSVResultsFileParser,\
    AnalysisResultsImporter
import traceback

title = "2-Dimensional-CSV"


def Import(context, request):
    """ Read Dimensional-CSV analysis results
    """
    form = request.form
    #TODO form['file'] sometimes returns a list
    infile = form['instrument_results_file'][0] if isinstance(form['instrument_results_file'],list) else form['instrument_results_file']
    artoapply = form['artoapply']
    override = form['results_override']
    sample = form.get('sample', 'requestid')
    instrument = form.get('instrument', None)
    errors = []
    logs = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    parser = TwoDimensionCSVParser(infile)

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

        sam = ['getId', 'getSampleID', 'getClientSampleID']
        if sample == 'requestid':
            sam = ['getId']
        if sample == 'sampleid':
            sam = ['getSampleID']
        elif sample == 'clientsid':
            sam = ['getClientSampleID']
        elif sample == 'sample_clientsid':
            sam = ['getSampleID', 'getClientSampleID']

        importer = TwoDimensionImporter(parser=parser,
                                           context=context,
                                           idsearchcriteria=sam,
                                           allowed_ar_states=status,
                                           allowed_analysis_states=None,
                                           override=over,
                                           instrument_uid=instrument,
                                           form=form)
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


def is_keyword(kw):
    bsc = api.get_tool('bika_setup_catalog')
    return len(bsc(getKeyword=kw))

def find_kw(ar, kw):
    keyword = None
    bc= api.get_tool('bika_catalog')
    ar = bc(portal_type='AnalysisRequest', id=ar)
    if len(ar) == 1:
        obj  = ar[0].getObject()
        analyses = obj.getAnalyses(full_objects=True)
        for analysis in analyses:
            interims = hasattr(analysis, 'getInterimFields') \
                        and analysis.getInterimFields() or []
            for interim in interims:
                if interim['keyword'] == kw:
                    keyword = analysis.getKeyword()
                    break
    return keyword


class TwoDimensionCSVParser(InstrumentCSVResultsFileParser):

    QUANTITATIONRESULTS_NUMERICHEADERS = ('Title8', 'Title9','Title31',
            'Title32','Title41', 'Title42','Title43', 
            )
    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._end_header = False
        self._keywords = []
        self._quantitationresultsheader = []
        self._numline = 0

    def _parseline(self, line):
        if self._end_header == False:
            return self.parse_headerline(line)
        else:
            return self.parse_resultsline(line)

    def parse_headerline(self, line):
        """ Parses header lines

            Keywords example:
            Keyword1, Keyword2, Keyword3, ..., end
        """
        if self._end_header == True:
            # Header already processed
            return 0

        splitted = [token.strip() for token in line.split(',')] 
        if splitted[-1] == 'end':
            self._keywords = splitted[1:-1] # exclude the word end
            self._end_header = True
        return 0

    def parse_resultsline(self, line):
        """ Parses result lines
        """
        splitted = [token.strip() for token in line.split(',')]

        if splitted[0] == 'end':
            return 0

        blank_line = [i for i in splitted if i !='']
        if len(blank_line) == 0:
            return 0

        quantitation = {}
        clean_splitted = splitted[1:-1]#First value on the line is AR
        for i in range(len(clean_splitted)):
            token = clean_splitted[i]
            if i < len(self._keywords):
                quantitation['AR'] = splitted[0]
                #quantitation['AN'] = self._keywords[i]
                quantitation['DefaultResult'] = 'resultValue'
                quantitation['resultValue'] = token
            elif token:
                self.err("Orphan value in column ${index} (${token})",
                         mapping={"index": str(i+1),
                                  "token": token},
                         numline=self._numline, line=line)

            result = quantitation[quantitation['DefaultResult']]
            column_name = quantitation['DefaultResult']
            result = self.zeroValueDefaultInstrumentResults(column_name, result, line)
            quantitation[quantitation['DefaultResult']] = result

            kw = re.sub(r"\W", "", self._keywords[i])
            if not is_keyword(kw):
                new_kw = find_kw(quantitation['AR'], kw)
                if new_kw:
                    quantitation[kw] = quantitation['resultValue']
                    del quantitation['resultValue']
                    kw = new_kw
                    kw = re.sub(r"\W", "", kw)

            self._addRawResult(quantitation['AR'],
                               values={kw:quantitation},
                               override=False)
            quantitation = {}

    def zeroValueDefaultInstrumentResults(self, column_name, result, line):
        result = str(result)
        if result.startswith('--') or result == '' or result == 'ND':
            return 0.0

        try:
            result = float(result)
            if result < 0.0:
                result  = 0.0
        except ValueError:
            self.err(
                "No valid number ${result} in column (${column_name})",
                mapping={"result": result,
                         "column_name": column_name},
                numline=self._numline, line=line)
            return
        return result

class TwoDimensionImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid='', form=None):
        AnalysisResultsImporter.__init__(self, parser, context, idsearchcriteria,
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
