# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
