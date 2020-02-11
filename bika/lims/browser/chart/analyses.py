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

import json
from bika.lims import api

class EvolutionChart(object):

    def __init__(self):
        self.analyses_dict = dict()

    def add_analysis(self, analysis):
        """Adds an analysis to be consumed by the Analyses Chart machinery (js)

        :param analysis_object: analysis to be rendered in the chart
        """
        analysis_object = api.get_object(analysis)
        result = analysis_object.getResult()
        results_range = analysis_object.getResultsRange()
        range_result = results_range.get('result', None)
        range_min = results_range.get('min', None)
        range_max = results_range.get('max', None)
        # All them must be floatable
        for value in [result, range_result, range_min, range_max]:
            if not api.is_floatable(value):
                return
        cap_date = analysis_object.getResultCaptureDate()
        cap_date = api.is_date(cap_date) and \
                   cap_date.strftime('%Y-%m-%d %I:%M %p') or ''
        if not cap_date:
            return

        # Create json
        ref_sample_id = analysis_object.getSample().getId()
        as_keyword = analysis_object.getKeyword()
        as_name = analysis_object.Title()
        as_ref = '{} ({})'.format(as_name, as_keyword)
        as_rows = self.analyses_dict.get(as_ref, {})
        an_rows = as_rows.get(ref_sample_id, [])
        an_rows.append({
            'date': cap_date,
            'target': api.to_float(range_result),
            'upper': api.to_float(range_max),
            'lower': api.to_float(range_min),
            'result': api.to_float(result),
            'unit': analysis_object.getUnit(),
            'id': api.get_uid(analysis_object)
        })
        as_rows[ref_sample_id] = an_rows
        self.analyses_dict[as_ref] = as_rows

    def get_json(self):
        """Returns a JSON dict conformant with the data structure expected by
        the analyses evolution charting machinery

        :returns: dict in JSON format
        :rtype: str
        """
        return json.dumps(self.analyses_dict)
