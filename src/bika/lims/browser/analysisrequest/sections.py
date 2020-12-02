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
from bika.lims import senaiteMessageFactory as _
from plone.app.layout.viewlets import ViewletBase


class LabAnalysesViewlet(ViewletBase):
    """Laboratory analyses section viewlet for Sample view
    """

    # Order index for this section
    order = 10

    title = _("Analyses")
    icon_name = "analysisservice"
    capture = "lab"

    @property
    def sample(self):
        return self.view.context

    def is_visible(self):
        """Returns true if this sample contains at least one analysis for the
        point of capture (capture)
        """
        analyses = self.sample.getAnalyses(getPointOfCapture=self.capture)
        return len(analyses) > 0

    def get_listing_view(self):
        request = api.get_request()
        view_name = "table_{}_analyses".format(self.capture)
        view = api.get_view(view_name, context=self.sample, request=request)
        return view

    def index(self):
        return self.render()

    def render(self):
        view = self.get_listing_view()
        view.update()
        view.before_render()
        return view.ajax_contents_table()


class FieldAnalysesViewlet(LabAnalysesViewlet):
    """Field analyses section viewlet for Sample view
    """
    order = 5
    title = _("Field Analyses")
    capture = "field"


class QCAnalysesViewlet(LabAnalysesViewlet):
    """QC analyses section viewlet for Sample view
    """
    order = 50
    title = _("QC Analyses")
    capture = "qc"

    def is_visible(self):
        """Returns true if this sample contains at least one qc analysis
        """
        analyses = self.sample.getQCAnalyses()
        return len(analyses) > 0
