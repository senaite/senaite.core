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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import copy

from bika.lims import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.modals import Modal


class SetAnalysisConditionsModal(Modal):
    template = ViewPageTemplateFile("templates/set_analysis_conditions.pt")
    _analysis = None

    def __call__(self):
        if self.request.form.get("submitted", False):
            self.handle_submit()
        return self.template()

    @property
    def analysis(self):
        if self._analysis is None:
            uids = self.get_uids_from_request()
            self._analysis = api.get_object_by_uid(uids[0])
        return self._analysis

    def get_analysis_name(self):
        return api.get_title(self.analysis)

    def get_conditions(self):
        conditions = self.analysis.getConditions()
        conditions = copy.deepcopy(conditions)
        for condition in conditions:
            choices = condition.get("choices", "")
            options = filter(None, choices.split("|"))
            condition.update({"options": options})
        return conditions

    def handle_submit(self):
        pass
