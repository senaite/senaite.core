# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import csv
from DateTime.DateTime import DateTime
from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from bika.lims.exportimport import instruments
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter
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
                all_files = [f for f in listdir(folder)
                             if isfile(join(folder, f))]
                imported_list = self.getAlreadyImportedFiles(folder)
                if not imported_list:
                    self.add_to_logs(i, interface,
                                     'imported.csv File not found...', '')
                    continue
                for file_name in all_files:
                    if file_name in imported_list:
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
                        self.add_to_logs(i, interface,
                                         'Parser not found...', file_name)
                        continue
                    # We will run import with some default parameters
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
                    if tbex:
                        errors.append(tbex)
                    final_log = ''
                    success_log = self.getInfoFromLog(logs, 'Import finished')
                    if success_log:
                        final_log = success_log
                    else:
                        final_log = errors
                    self.insert_file_name(folder, file_name)
                    self.add_to_logs(i, interface, final_log, file_name)

        return 'Auto-Import finished...'

    def getAlreadyImportedFiles(self, folder):
        try:
            with open(folder+'/imported.csv', 'r') as f:
                imported = f.readlines()
                imported = [i.strip() for i in imported]
                return imported
        except:
            with open(folder+'/imported.csv', 'w') as f:
                f.write('imported.csv\n')
                f.close()
            return ['']
        return None

    def insert_file_name(self, folder, name):
        try:
            with open(folder+'/imported.csv', 'a') as fd:
                fd.write(name+'\n')
                fd.close()
        except:
            pass

    def getInfoFromLog(self, logs, keyword):
        try:
            for log in logs:
                if keyword in log:
                    return log
            return None
        except:
            return None

    def add_to_logs(self, instrument, interface, log, filename):
        _id = self.portal.invokeFactory("AutoImportLog", id=tmpID(),
                                        Instrument=instrument,
                                        Interface=interface,
                                        Results=log,
                                        ImportedFile=filename)
        item = self.portal[_id]
        item.markCreationFlag()


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
        if hasattr(orig_file, '__methods__'):
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
