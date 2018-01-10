# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.utils import getToolByName
from bika.lims.controlpanel.bika_samplingrounds import SamplingRoundsView


class ClientSamplingRoundsView(SamplingRoundsView):
    """This is displayed in the "Sampling Rounds" tab on each client
    """

    def __init__(self, context, request):
        super(ClientSamplingRoundsView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'SamplingRound',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.title = self.context.translate(_("Client Sampling Rounds"))
        self.context_actions = {
            _('Add'): {'url': '++add++SamplingRound',  # To work with dexterity
                       'icon': '++resource++bika.lims.images/add.png'}}

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return super(ClientSamplingRoundsView, self).__call__()
