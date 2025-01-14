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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import plone
import plone.protect

from bika.lims import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class SetAnalyst(BrowserView):
    """The Analysis dropdown sets worksheet.Analyst immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(value):
            return
        self.context.setAnalyst(value)


class SetInstrument(BrowserView):
    """The Instrument dropdown sets worksheet.Instrument immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            raise Exception("Invalid instrument")

        instrument = api.get_object_by_uid(value, None)
        if not instrument:
            raise Exception("Unable to lookup instrument")

        # set the instrument to the worksheet and analyses
        self.context.setInstrument(instrument, override_analyses=True)
