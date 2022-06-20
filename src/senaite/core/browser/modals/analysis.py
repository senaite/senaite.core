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
from bika.lims import FieldEditAnalysisConditions
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.interfaces.analysis import IRequestAnalysis
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SetAnalysisConditionsView(BrowserView):
    """View for the update of analysis conditions
    """
    template = ViewPageTemplateFile("templates/set_analysis_conditions.pt")

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_submit()
        return self.template()

    def redirect(self, message=None, level="info"):
        """Redirect with a message
        """
        redirect_url = api.get_url(self.context)
        if message is not None:
            self.context.plone_utils.addPortalMessage(message, level)
        return self.request.response.redirect(redirect_url)

    def get_analysis(self):
        uid = self.get_uid_from_request()
        obj = api.get_object_by_uid(uid)
        if IRequestAnalysis.providedBy(obj):
            # Only analyses that implement IRequestAnalysis support conditions
            return obj
        return None

    def get_uid_from_request(self):
        """Returns the uid from the request, if any
        """
        uid = self.request.form.get("uid", self.request.get("uid"))
        if api.is_uid(uid):
            return uid
        return None

    def get_analysis_name(self):
        analysis = self.get_analysis()
        return api.get_title(analysis)

    def get_conditions(self):
        """Returns the conditions to display in the form, those with empty or
        non-set value included
        """
        conditions = self.get_analysis().getConditions(empties=True)
        conditions = copy.deepcopy(conditions)
        for condition in conditions:
            choices = condition.get("choices", "")
            options = filter(None, choices.split("|"))
            condition.update({"options": options})
        return conditions

    def handle_submit(self):
        analysis = self.get_analysis()
        title = safe_unicode(api.get_title(analysis))
        if not check_permission(FieldEditAnalysisConditions, analysis):
            message = _("Not allowed to update conditions: {}").format(title)
            return self.redirect(message=message, level="error")

        # Update the conditions
        conditions = self.request.form.get("conditions", [])
        analysis.setConditions(conditions)
        message = _("Analysis conditions updated: {}").format(title)
        return self.redirect(message=message)
