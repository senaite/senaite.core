# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analyses import AnalysesView
from bika.lims.permissions import *
import os
import glob
import plone
import App


class SampleAnalysesView(AnalysesView):
    """ This renders the Field and Lab analyses tables for Samples
    """
    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request)
        self.show_workflow_action_buttons = False
        for k,v in kwargs.items():
            self.contentFilter[k] = v
        self.contentFilter['getSampleUID'] = context.UID()
        self.columns['Request'] = {
            'title': _("Request"),
            'attr': 'getParentTitle',
            'replace_url': 'getParentURL',
            'sortable': False}
        # Add Request columns
        pos = self.review_states[0]['columns'].index('Service') + 1
        self.review_states[0]['columns'].insert(pos, 'Request')
        pos += 1
