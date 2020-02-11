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

import plone
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysis, IJSONReadExtender
from bika.lims.jsonapi import get_include_fields
from bika.lims.utils import dicts_to_dict
from bika.lims.utils.analysis import get_method_instrument_constraints
from zExceptions import Forbidden
from zope.component import adapts
from zope.interface import implements


class JSONReadExtender(object):

    """- Adds the specification from Analysis Request to Analysis in JSON response
    """

    implements(IJSONReadExtender)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def analysis_specification(self):
        ar = self.context.aq_parent
        rr = dicts_to_dict(ar.getResultsRange(), 'keyword')

        return rr[self.context.getKeyword()]

    def __call__(self, request, data):
        self.request = request
        self.include_fields = get_include_fields(request)
        if not self.include_fields or "specification" in self.include_fields:
            data['specification'] = self.analysis_specification()
        return data


class ajaxGetMethodInstrumentConstraints(BrowserView):

    def __call__(self):
        """
            Returns a json dictionary with the constraints and rules for
            methods, instruments and results to be applied to each of the
            analyses specified in the request (an array of uids).
            See docs/imm_results_entry_behaviour.png for further details
        """
        constraints = {}
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(constraints)

        rowuids = self.request.get('uids', '[]')
        rowuids = json.loads(rowuids)
        constraints = get_method_instrument_constraints(self, rowuids)
        return json.dumps(constraints)
