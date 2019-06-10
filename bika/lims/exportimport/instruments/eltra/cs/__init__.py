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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

""" Eltra CS - 2000
"""
from datetime import datetime
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser
from bika.lims import bikaMessageFactory as _


class EltraCSTSVParser(InstrumentCSVResultsFileParser):
    def __init__(self, tsv, analysis1, analysis2):
        InstrumentCSVResultsFileParser.__init__(self, tsv)
        self._analysis1 = analysis1
        self._analysis2 = analysis2

    def _parseline(self, line):
        """
        https://jira.bikalabs.com/browse/LIMS-1818?focusedCommentId=16915&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-16915
        Only first 4 columns are important:

        3/24/2015 7:55 AM BOG 651 (IND) - 16 0.10931925301288605 0.016803081793406938

        Date: 3/24/2015 7:55 AM
        Sample: BOG 651
        Carbon: 0.10931925301288605
        Sulphur: 0.016803081793406938
        """

        sline = line.split('\t')
        if len(sline) < 4:
            return -1
        try:
            raw_dict = {
                self._analysis1: {
                    'DefaultResult': 'Result',
                    'Result': sline[2],
                    'Date': self.csvDate2BikaDate(sline[0])
                },
                self._analysis2: {
                    'DefaultResult': 'Result',
                    'Result': sline[3],
                    'Date': self.csvDate2BikaDate(sline[0])
                }
            }
            self._addRawResult(sline[1], raw_dict)
            return 0
        except IndexError:
            return -1

    def csvDate2BikaDate(self, DateTime):
        # example: 11/03/2014 14:46:46 --> %d/%m/%Y %H:%M%S
        dtobj = datetime.strptime(DateTime, "%m/%d/%Y %I:%M %p")
        return dtobj.strftime("%Y%m%d %H:%M")


class EltraCSImporter(AnalysisResultsImporter):
    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
