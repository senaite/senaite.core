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


class ResultsImportView(BrowserView):

    def __init__(self, context, request):
        super(ResultsImportView, self).__init__(context, request)

    def __call__(self):
        request = self.request

        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc(portal_type='Instrument',
                     inactive_state='active')
        i = brains[0].getObject()
        folder = i.getResultFilesFolder()[0]['Folder']
        interface = i.getResultFilesFolder()[0]['InterfaceName']
        result_file = open('test.csv', 'rb')
        exim = instruments.getExim(interface)
        parser_name = 'TestParser'
        parser_function = getattr(exim, parser_name)
        parser = parser_function(result_file)
        importer = AnalysisResultsImporter(
                    parser=parser,
                    context=self.portal,
                    idsearchcriteria=['getRequestID', 'getSampleID',
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

            results = {'errors': errors, 'log': logs, 'warns': warns}

        return json.dumps(results)
