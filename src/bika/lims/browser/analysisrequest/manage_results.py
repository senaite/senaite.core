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

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    """Manage Results View
    """
    template = ViewPageTemplateFile(
        "templates/analysisrequest_manage_results.pt")

    def __call__(self):
        self.checkInstrumentsValidity()
        return self.template()

    def checkInstrumentsValidity(self):
        """Checks the validity of the instruments used in the Analyses

        If an analysis with an invalid instrument (out-of-date or with
        calibration tests failed) is found, a warn message will be displayed.
        """
        invalid = []

        ans = [a.getObject() for a in self.context.getAnalyses()]
        for an in ans:
            valid = an.isInstrumentValid()
            if not valid:
                inv = '%s (%s)' % (safe_unicode(an.Title()),
                                   safe_unicode(an.getInstrument().Title()))
                if inv not in invalid:
                    invalid.append(inv)
        if len(invalid) > 0:
            message = _("Some analyses use out-of-date or uncalibrated "
                        "instruments. Results edition not allowed")
            message = "%s: %s" % (message, (', '.join(invalid)))
            self.context.plone_utils.addPortalMessage(message, 'warning')
