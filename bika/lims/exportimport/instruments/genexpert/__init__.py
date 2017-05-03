# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" GenExpert
"""
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser

from hl7apy.parser import parse_message
from util.constants import STX, CR, LF, CRLF, ACK, NAK, ENQ, EOT
from util.extractresults import ExtractResults


class GenExpertParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = {}
        self._linedata = {}
        self._rownum = None
        self._isFirst = True

    def parse(self):
        infile = self.getInputFile()
        self.log("Parsing file ${file_name}",
                 mapping={"file_name": infile.filename})

        formatted_hl7 = self.get_message(infile)
        if formatted_hl7:
            # extract result from the HL7 message
            results = ExtractResults.loadresultarray(formatted_hl7)
            for x in results:
                print x, ':', results[x]

        return True

    def get_message(self, rfile):
        message = ''
        line = ''
        data_byte = rfile.read(1)

        while data_byte != EOT:

            if data_byte != ENQ and data_byte != ACK:
                line += data_byte

            if data_byte == ENQ:
                print 'return ack sent:', ACK

            if data_byte == LF:
                if self.is_proper_message(line):
                    if ExtractResults.make_checksum(line[1:-4]) == line[-4:-2]:
                        line = line[2:]
                        line = line[:-5]
                        message += line
                        line = ''
                    else:
                        line = ''

            data_byte = rfile.read(1)

        if not message and not parse_message(message):
            return parse_message(message)
        else:
            return False

    def is_proper_message(self, message):

        if not isinstance(message, bytes):
            raise TypeError('bytes expected, got %r' % message)
            return False
        if not (message.startswith(STX) and message.endswith(CRLF)):
            raise ValueError('Malformed ASTM message. Expected that it will started'
                             ' with %x and followed by %x%x characters. Got: %r'
                             ' ' % (ord(STX), ord(CR), ord(LF), message))
            return False

        return True


class GenExpertImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, idsearchcriteria, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         idsearchcriteria, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
