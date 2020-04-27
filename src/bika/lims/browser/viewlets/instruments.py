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

from bika.lims import api
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class InstrumentQCFailuresViewlet(ViewletBase):
    """ Print a viewlet showing failed instruments
    """
    index = ViewPageTemplateFile("templates/instrument_qc_failures_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(InstrumentQCFailuresViewlet, self).__init__(
            context, request, view, manager=manager)
        self.nr_failed = 0
        self.failed = {
            "out-of-date": [],
            "qc-fail": [],
            "next-test": [],
            "validation": [],
            "calibration": [],
        }

    def get_failed_instruments(self):
        """Find invalid instruments

        - instruments who have failed QC tests
        - instruments whose certificate is out of date
        - instruments which are disposed until next calibration test

        Return a dictionary with all info about expired/invalid instruments
        """
        bsc = api.get_tool("bika_setup_catalog")
        insts = bsc(portal_type="Instrument", is_active=True)
        for i in insts:
            i = i.getObject()
            instr = {
                'uid': i.UID(),
                'title': i.Title(),
            }
            if i.isValidationInProgress():
                instr['link'] = '<a href="%s/validations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['validation'].append(instr)
            elif i.isCalibrationInProgress():
                instr['link'] = '<a href="%s/calibrations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['calibration'].append(instr)
            elif i.isOutOfDate():
                instr['link'] = '<a href="%s/certifications">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['out-of-date'].append(instr)
            elif not i.isQCValid():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['qc-fail'].append(instr)
            elif i.getDisposeUntilNextCalibrationTest():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['next-test'].append(instr)

    def available(self):
        """Control availability of the viewlet
        """
        context_state = api.get_view("plone_context_state")
        url = context_state.current_page_url()
        portal_url = api.get_url(api.get_portal())
        # render on the portal root
        if url.endswith(portal_url):
            return True
        # render on the front-page
        if url.endswith("/front-page"):
            return True
        # render for manage_results
        if url.endswith("/manage_results"):
            return True
        return False

    def render(self):
        """Render the viewlet
        """
        if not self.available():
            return ""

        mtool = api.get_tool("portal_membership")
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = "LabManager" in roles or "Manager" in roles

        self.get_failed_instruments()

        if allowed and self.nr_failed:
            return self.index()
        else:
            return ""
