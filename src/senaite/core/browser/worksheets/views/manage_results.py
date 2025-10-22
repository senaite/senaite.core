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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import getUsers
from plone.app.layout.globals.interfaces import IViewView
from plone.memoize import view
from senaite.core.config.worksheet import DEFAULT_WORKSHEET_LAYOUT
from senaite.core.p3compat import cmp
from senaite.core.permissions.worksheet import can_manage_worksheets
from senaite.core.vocabularies.worksheet import WorksheetLayoutsFactory
from zope.interface import implements


class ManageResultsView(BrowserView):
    """Worksheet Manage Results View
    """
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/results.pt")

    def __init__(self, context, request):
        super(ManageResultsView, self).__init__(context, request)
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++plone++senaite.core.static/assets/icons/worksheet.svg"
        )

    def __call__(self):
        self.rejection_message()

        # Save the results layout
        layout_list = self.layout_displaylist.keys()
        current_layout = self.context.getResultsLayout()
        r_layout = self.request.get("resultslayout", "")
        if r_layout in layout_list and r_layout != current_layout:
            self.context.setResultsLayout(r_layout)
            message = _(
                u"change_worksheet_result_layout_message",
                default=u"Changes saved.",
            )
            self.add_status_message(message, "info")

        # Classic/Transposed or additional View Switch
        view = self.context.getResultsLayout()
        if view not in self.layout_displaylist.keys():
            message = _(
                u"not_found_worksheet_layout_message",
                default=u"Layout view '${view}' not found. "
                        u"Set '${default}' as layout view.",
                mapping={
                    "view": view,
                    "default": DEFAULT_WORKSHEET_LAYOUT,
                },
            )
            self.add_status_message(message, "warning")
            view = DEFAULT_WORKSHEET_LAYOUT
            self.context.setResultsLayout(view)

        self.Analyses = api.get_view(
            view, context=self.context, request=self.request)

        self.analystname = self.context.getAnalystName()
        self.instrumenttitle = self.get_instrument_title()

        # Check if the instruments used are valid
        self.checkInstrumentsValidity()

        return self.template()

    def rejection_message(self):
        for msg in self.context.getRejectionMessages():
            self.add_status_message(msg)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    @property
    def layout_displaylist(self):
        return WorksheetLayoutsFactory

    def get_analysts(self):
        """Returns Analysts
        """
        roles = ["Manager", "LabManager", "Analyst"]
        return getUsers(self.context, roles)

    @view.memoize
    def get_instrument_title(self):
        """Return the current instrument title
        """
        instrument = self.context.getInstrument()
        if not instrument:
            return ""
        return api.get_title(instrument)

    @view.memoize
    def is_manage_allowed(self):
        """Check if manage is allowed
        """
        return can_manage_worksheets(self.context)

    @view.memoize
    def is_assignment_allowed(self):
        """Check if analyst assignment is allowed
        """
        if not self.is_manage_allowed():
            return False
        review_state = api.get_workflow_status_of(self.context)
        edit_states = ["open", "to_be_verified"]
        return review_state in edit_states

    def getInstruments(self):
        # TODO: Return only the allowed instruments for at least one contained
        # analysis
        bsc = getToolByName(self, 'senaite_catalog_setup')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Instrument',
                                  is_active=True)]
        o = self.context.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))

    def get_wide_interims(self):
        """Returns a dictionary with the analyses services from the current
        worksheet which have at least one interim with 'Wide' attribute set to
        true and that have not been yet submitted

        The structure of the returned dictionary is the following:
        <Analysis_keyword>: {
            'analysis': <Analysis_name>,
            'keyword': <Analysis_keyword>,
            'interims': {
                <Interim_keyword>: {
                    'value': <Interim_default_value>,
                    'keyword': <Interim_key>,
                    'title': <Interim_title>
                }
            }
        }
        """
        outdict = {}
        allowed_states = ['assigned', 'unassigned']
        for analysis in self.context.getAnalyses():
            # TODO Workflow - Analysis Use a query instead of this
            if api.get_workflow_status_of(analysis) not in allowed_states:
                continue

            if analysis.getKeyword() in outdict.keys():
                continue

            andict = {
                "analysis": analysis.Title(),
                "keyword": analysis.getKeyword(),
                "interims": {}
            }

            # Analysis Service interim defaults
            for field in analysis.getInterimFields():
                if field.get("wide", False):
                    andict["interims"][field["keyword"]] = field

            if andict["interims"]:
                outdict[analysis.getKeyword()] = andict
        return outdict

    def checkInstrumentsValidity(self):
        """Checks the validity of the instruments used in the Analyses If an
        analysis with an invalid instrument (out-of-date or with calibration
        tests failed) is found, a warn message will be displayed.
        """
        invalid = []
        ans = self.context.getAnalyses()
        for an in ans:
            instrument = an.getInstrument()
            if instrument and not instrument.isValid():
                inv = "%s (%s)" % (
                    safe_unicode(an.Title()), safe_unicode(instrument.Title()))
                if inv not in invalid:
                    invalid.append(inv)
        if len(invalid) > 0:
            message = _(
                u"check_instrument_validity_message",
                default=u"Some analyses use out-of-date or uncalibrated "
                        u"instruments. Results edition not allowed: ${inv}",
                mapping={"inv": ", ".join(invalid)}
            )
            self.add_status_message(message, "warning")
