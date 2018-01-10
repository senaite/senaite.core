# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" LaChat QuickChem FIA
"""
import csv
import json
import logging
import re
import traceback

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims.utils import t
from cStringIO import StringIO
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

logger = logging.getLogger(__name__)

title = "LaChat QuickChem FIA"


class Parser(InstrumentResultsFileParser):
    """ Instrument Parser
    """

    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'CSV')

    def parse(self):
        """ CSV Parser
        """

        reader = csv.DictReader(self.getInputFile(), delimiter='\t')

        for row in reader:
            # in Sample ID column, we may find format: '[SampleID] samplepoint'
            sampleid = row['Sample ID']
            if sampleid.startswith('['):
                # the part between brackets is the sample id:
                row['Sample ID'] = sampleid[1:].split(']')[0]

            # Strip all special chars from the service name (Analyte Name col)
            row['Analyte Name'] = re.sub(r"\W", "", row['Analyte Name'])

            row['DefaultResult'] = 'Peak Concentration'
            self._addRawResult(row['Sample ID'],
                               values={row['Analyte Name']: row},
                               override=False)

        self.log(
            "End of file reached successfully: ${total_objects} objects, "
            "${total_analyses} analyses, ${total_results} results",
            mapping={"total_objects": self.getObjectsTotalCount(),
                     "total_analyses": self.getAnalysesTotalCount(),
                     "total_results": self.getResultsTotalCount()}
        )

        return True


class Importer(AnalysisResultsImporter):
    """ Instrument Importer
    """

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         idsearchcriteria,
                                         override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)


def Import(context, request):
    """ Import Form
    """
    infile = request.form['lachat_quickchem_fia_file']
    fileformat = request.form['lachat_quickchem_fia_format']
    artoapply = request.form['lachat_quickchem_fia_artoapply']
    override = request.form['lachat_quickchem_fia_override']
    sample = request.form.get('lachat_quickchem_fia_sample', 'requestid')
    instrument = request.form.get('lachat_quickchem_fia_instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        parser = Parser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

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

        importer = Importer(parser=parser,
                            context=context,
                            idsearchcriteria=sam,
                            allowed_ar_states=status,
                            allowed_analysis_states=None,
                            override=over,
                            instrument_uid=instrument)
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


class Export(BrowserView):
    """ Writes worksheet analyses to a CSV file for LaChat QuickChem FIA.
        Sends the CSV file to the response for download by the browser.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, analyses):
        uc = getToolByName(self.context, 'uid_catalog')
        instrument = self.context.getInstrument()
        norm = getUtility(IIDNormalizer).normalize
        filename = '{}-{}.csv'.format(self.context.getId(),
                                       norm(instrument.getDataInterface()))

        # write rows, one per Sample, including including refs and duplicates.
        #Start Column A at 1 or 9? (the examples given used 9, no clues.)
        #If routine analysis, Column B is the AR ID + sample type.
        #If Reference analysis, Column B is the Ref Sample.
        #If Duplicate analysis, column B is the Worksheet.
        #Column C is the well number
        #Column D empty
        #Column E should always be 1 (2 indicates a duplicate from the same cup)
        layout = self.context.getLayout()
        rows = []
        tmprows = []
        col_a = 1
        result = ''
        # We don't want to include every single slot!  Just one entry
        # per AR, Duplicate, or Control.
        used_ids = []
        for x, row in enumerate(layout):
            a_uid = row['analysis_uid']
            c_uid = row['container_uid']
            analysis = uc(UID=a_uid)[0].getObject() if a_uid else None
            container = uc(UID=c_uid)[0].getObject() if c_uid else None
            if row['type'] == 'a':
                if 'a{}'.format(container.id) in used_ids:
                    continue
                used_ids.append('a{}'.format(container.id))
                # col_a (sample id) has a weird format, but it matches
                # the examples we are given, so it is true:
                sample = container.getSample()
                samplepoint = sample.getSamplePoint()
                sp_title = samplepoint.Title() if samplepoint else ''
                col_b = '[{}] {}'.format(container.id, sp_title)
                col_c = str(row['position'])
                col_d = ''
                col_e = '1'
            elif row['type'] in 'bcd':
                refgid = analysis.getReferenceAnalysesGroupID()
                if 'bcd{}'.format(refgid) in used_ids:
                    continue
                used_ids.append('bcd{}'.format(refgid))
                col_b = refgid
                col_c = str(row['position'])
                col_d = ''
                col_e = '1'
            rows.append(','.join([str(col_a), col_b, col_c, col_d, col_e]))
            col_a += 1
        result += '\r\n'.join(rows)

        # stream to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)
