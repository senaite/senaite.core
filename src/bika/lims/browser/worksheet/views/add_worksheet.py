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

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID


class AddWorksheetView(BrowserView):
    """ Handler for the "Add Worksheet" button in Worksheet Folder.
        If a template was selected, the worksheet is pre-populated here.
    """

    def __call__(self):

        # Validation
        form = self.request.form
        analyst = self.request.get('analyst', '')
        template = self.request.get('template', '')
        instrument = self.request.get('instrument', '')

        if not analyst:
            message = _("Analyst must be specified.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, "portal_workflow")
        pm = getToolByName(self.context, "portal_membership")

        ws = _createObjectByType("Worksheet", self.context, tmpID())
        ws.processForm()

        # Set analyst and instrument
        ws.setAnalyst(analyst)
        if instrument:
            ws.setInstrument(instrument)

        # Set the default layout for results display
        ws.setResultsLayout(self.context.bika_setup.getWorksheetLayout())

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not template:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(template)
        ws.applyWorksheetTemplate(wst)

        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            msg = _("No analyses were added")
            self.context.plone_utils.addPortalMessage(msg)
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
