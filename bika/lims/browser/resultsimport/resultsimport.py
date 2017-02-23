# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import csv
import os
from DateTime.DateTime import DateTime
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.utils import tmpID
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.exportimport import instruments
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter
import json
import traceback
from os import listdir
from os.path import isfile, join


class ResultsImportView(BrowserView):

    """
    This view will be called from any periodically running script to run
    auto-import process. Instruments which has interfaces, and also interfaces
    which auto-import folders assigned, will participate in this process.
    To import for specified Instrument or/and Interface, these parameters can
    be set in URL as well.
    """
    def __init__(self, context, request):
        super(ResultsImportView, self).__init__(context, request)

    def __call__(self):
        request = self.request

        bsc = getToolByName(self, 'bika_setup_catalog')
        # Getting instrumnets to run auto-import
        query = {'portal_type': 'Instrument',
                 'inactive_state': 'active'}
        if request.get('i_uid', ''):
            query['UID'] = request.get('i_uid')
        brains = bsc(query)
        interfaces = []
        for brain in brains:
            i = brain.getObject()
            # If Import Interface ID is specified in request, then auto-import
            # will run only that interface. Otherwise all available interfaces
            # of this instruments
            if request.get('interface', ''):
                interfaces.add(request.get('interface'))
            else:
                interfaces = [pairs.get('InterfaceName', '') for pairs
                              in i.getResultFilesFolder()]
            folder = ''
            for interface in interfaces:
                # Each interface must have its folder where result files are
                # saved. If not, then we will skip
                for pairs in i.getResultFilesFolder():
                    if pairs['InterfaceName'] == interface:
                        folder = pairs.get('Folder', '')
                if not folder:
                    continue
                # TODO Filter not to insert same files again. We are
                # getting all files from the folder.
                all_files = [f for f in listdir(folder)
                             if isfile(join(folder, f))]
                imported_list = self.getAlreadyImportedFiles(folder)
                if not imported_list:
                    print 'Can not open imported list...'
                    continue
                for file_name in all_files:
                    if file_name in imported_list:
                        print 'File imported...'
                        continue
                    temp_file = open(folder+'/'+file_name)
                    # Parsers work with UploadFile object from
                    # zope.HTTPRequest which has filename attribute.
                    # To add this attribute we convert the file.
                    # CHECK should we add headers too?
                    result_file = ConvertToUploadFile(temp_file)
                    exim = instruments.getExim(interface)
                    parser_name = instruments.getParserName(interface)
                    parser_function = getattr(exim, parser_name) \
                        if hasattr(exim, parser_name) else ''
                    if not parser_function:
                        continue
                    # We will run imoprt with some default parameters
                    # Expected to be modified in the future.
                    parser = parser_function(result_file)
                    importer = GeneralImporter(
                                parser=parser,
                                context=self.portal,
                                idsearchcriteria=['getRequestID',
                                                  'getSampleID',
                                                  'getClientSampleID'],
                                allowed_ar_states=['sample_received'],
                                allowed_analysis_states=None,
                                override=[False, False],
                                instrument_uid=i.UID())
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
                    results = {'errors': errors,
                               'log': logs, 'warns': warns}
                    return results
        return 'Nothing happened...'

    def getAlreadyImportedFiles(self, folder):
        try:
            with open(folder+'/imported.csv') as f:
                imported = f.readlines()
                return imported
        except:
            return None

class GeneralImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


class ConvertToUploadFile:
    """
    File objects don't have 'filename' and 'headers' attributes.
    Since Import step of different Interfaces checks if 'filename' is set
    to be sure that submitted form contains uploaded file, we also have to add
    this attribute to our File object.
    """
    def __init__(self, orig_file):
        if hasattr(file, '__methods__'):
            methods = orig_file.__methods__
        else:
            methods = ['close', 'fileno', 'flush', 'isatty',
                       'read', 'readline', 'readlines', 'seek',
                       'tell', 'truncate', 'write', 'writelines',
                       '__iter__', 'next', 'name']
        d = self.__dict__
        for m in methods:
            if hasattr(orig_file, m):
                d[m] = getattr(orig_file, m)
        self.filename = orig_file.name
