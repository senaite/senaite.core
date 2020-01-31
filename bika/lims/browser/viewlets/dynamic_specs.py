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

from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DynamicSpecsViewlet(ViewletBase):
    """ Displays an informative message when the specification has a dynamic
    specification assigned, so ranges might be overriden by the ranges provided
    in the xls file from the Dynamic Specification
    """
    template = ViewPageTemplateFile("templates/dynamic_specs_viewlet.pt")


class SampleDynamicSpecsViewlet(ViewletBase):
    """Displays an informative message in Sample view when the assigned
    specification has a dynamic specification assigned, so ranges set manually
    might be overriden by the ranges provided in the xls file from the Dynamic
    Specification
    """
    template = ViewPageTemplateFile(
        "templates/sample_dynamic_specs_viewlet.pt")

    def get_dynamic_specification(self):
        """Returns the dynamic specification assigned to the Sample via
        Specification, but only if the current view is manage analyses
        """
        if not self.request.getURL().endswith("analyses"):
            # Do not display the viewlet if not in manage analyses
            return None

        spec = self.context.getSpecification()
        if spec:
            return spec.getDynamicAnalysisSpec()
        return None
