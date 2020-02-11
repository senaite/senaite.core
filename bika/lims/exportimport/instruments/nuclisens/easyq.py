# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

""" Nuclisens EasyQ
"""
import csv
import json
import traceback
from cStringIO import StringIO
import xml.etree.ElementTree as ET

import types
from openpyxl import load_workbook

from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentResultsFileParser
from bika.lims.exportimport.instruments.instrument import format_keyword
from bika.lims.utils import t

title = "Nuclisens EasyQ"


class EasyQParser(InstrumentResultsFileParser):
    """ Parser
    """
    def __init__(self, rsf):
        InstrumentResultsFileParser.__init__(self, rsf, 'XLSX')

    def xlsx_to_csv(self, infile, worksheet=0, delimiter=","):
        """ Convert xlsx to easier format first, since we want to use the
        convenience of the CSV library
        """
        wb = load_workbook(self.getInputFile())
        sheet = wb.worksheets[worksheet]
        buffer = StringIO()

        # extract all rows
        for n, row in enumerate(sheet.rows):
            line = []
            for cell in row:
                value = cell.value
                if type(value) in types.StringTypes:
                    value = value.encode("utf8")
                if value is None:
                    value = ""
                line.append(str(value))
            print >>buffer, delimiter.join(line)
        buffer.seek(0)
        return buffer

    def parse(self):
        """ parse the data
        """

        # convert the xlsx file to csv first
        delimiter = "|"
        csv_file = self.xlsx_to_csv(self.getInputFile(), delimiter=delimiter)
        reader = csv.DictReader(csv_file, delimiter=delimiter)

        for n, row in enumerate(reader):
            resid = row.get("SampleID", None)
            serial = row.get("SerialNumber", None)
            # Convert empty values as "Invalid"
            value = row.get("Value", None) or "Invalid"

            # no resid and no serial
            if not any([resid, serial]):
                self.err("Result identification not found.", numline=n)
                continue

            rawdict = row
            rawdict["Value"] = value.rstrip(" cps/ml")
            rawdict['DefaultResult'] = 'Value'

            # HEALTH-567 correction factor for calculation
            # XXX HEALTH-567 Is this just for nmrl?
            if 'Plasma' in rawdict.get('Matrix', 'Other'):
                rawdict['CF'] = 1  # report value as-is
            else:
                rawdict['CF'] = 1.82  # report value * 1.82

            key = resid or serial
            testname = row.get("Product", "EasyQDirector")
            self._addRawResult(key, {testname: rawdict}, False)


class EasyQXMLParser(InstrumentResultsFileParser):
    """ XML input Parser
    """
    def __init__(self, xml):
        InstrumentResultsFileParser.__init__(self, xml, 'XML')
        self._assays = {}
        self._instruments = {}

    def parse(self):
        """ parse the data
        """
        tree = ET.parse(self.getInputFile())
        root = tree.getroot()
        # Building Assay dictionary to query names by id from test results line
        for as_ref in root.find("Assays").findall("AssayRef"):
            self._assays[as_ref.get("KEY_AssayRef")] = as_ref.get("ID")

        # Building Instruments dictionary to get Serial number by id
        for ins in root.find("Instruments").findall("Instrument"):
            self._instruments[ins.get("KEY_InstrumentData")] = \
                ins.get("SerialNumber")

        for t_req in root.iter("TestRequest"):
            t_res = t_req.find("TestResult")
            if len(t_res) == 0 or not t_res.get("Valid", "false") == "true":
                continue
            res_id = t_req.get("SampleID")
            test_name = self._assays.get(t_req.get("KEY_AssayRef"))
            test_name = format_keyword(test_name)
            result = t_res.get("Value")
            if not result:
                continue
            result = result.split(" cps/ml")[0]
            detected = t_res.get("Detected")

            # SOME ADDITIONAL DATA
            # Getting instrument serial number from 'Run' element which is
            # parent of 'TestRequest' elements
            ins_serial = t_req.getParent().get("KEY_InstrumentData")

            # Matrix is important for calculation.
            matrix = t_req.get("Matrix")
            # For now, using EasyQDirector as keyword, but this is not the
            # right way. test_name must be used.
            values = {
                'EasyQDirector': {
                    "DefaultResult": "Result",
                    "Result": result,
                    "Detected": detected,
                    "Matrix": matrix,
                    "Instrument": ins_serial
                }
            }
            self._addRawResult(res_id, values)


class EasyQImporter(AnalysisResultsImporter):
    """ Importer
    """

    def _process_analysis(self, objid, analysis, values):
        ret = AnalysisResultsImporter._process_analysis(self, objid, analysis,
                                                         values)
        # HEALTH-567
        if values.get('Value') and str(values['Value'])[0] in "<>":
            analysis.setDetectionLimitOperand('<')
        return ret


def __init__(self, parser, context,  override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):

        AnalysisResultsImporter.__init__(self,
                                         parser,
                                         context,
                                         override=override,
                                         allowed_ar_states=allowed_ar_states,
                                         allowed_analysis_states=allowed_analysis_states,
                                         instrument_uid=instrument_uid)


def Import(context, request):
    """ Import Form
    """
    infile = request.form['nuclisens_easyq_file']
    fileformat = request.form['nuclisens_easyq_format']
    artoapply = request.form['nuclisens_easyq_artoapply']
    override = request.form['nuclisens_easyq_override']
    instrument = request.form.get('instrument', None)
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'xlsx':
        parser = EasyQParser(infile)
    elif fileformat == 'xml':
        parser = EasyQXMLParser(infile)
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

        importer = EasyQImporter(parser=parser,
                                 context=context,
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
