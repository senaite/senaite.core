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

from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
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
                       'permission': 'Add portal content',
                       'icon': '++resource++bika.lims.images/add.png'}}

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return super(ClientSamplingRoundsView, self).__call__()
