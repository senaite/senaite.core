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
# Copyright 2018-2026 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api


def create_worksheet(analyst, instrument=None, template=None, analyses=None):
    """Helper method for creating a new worksheet
    :param analyst: Analyst for this worksheet
    :type analyst: str
    :param instrument: Instrument for this worksheet. Not required.
    :type instrument: uid/object or None
    :param template: Template for this worksheet. Not required.
    :type template: uid/object or None
    :param analyses: Analyses for this worksheet. Not required.
    :type analyses: list or None
    :return: New Worksheet object
    :rtype: Worksheet
    """
    if not analyst:
        return None
    portal = api.get_portal()
    container = portal.get("worksheets")
    layout = api.get_senaite_setup().getWorksheetLayout()
    ws = api.create(container, "Worksheet",
                    analyst=analyst,
                    instrument=instrument,
                    results_layout=layout)

    unassigned_analyses = []
    analyses = api.to_list(analyses)
    analyses = list(filter(None, analyses))
    for analysis in analyses:
        an = api.get_object(analysis)
        ws_uid = an.getWorksheetUID()
        # collect all unassigned analyses
        if not all([ws_uid, api.is_uid(ws_uid)]):
            unassigned_analyses.append(an)
        ws.addAnalysis(an)
    if template is not None:
        ws.applyWorksheetTemplate(template, analyses=unassigned_analyses)

    ws.reindexObject()
    return ws
