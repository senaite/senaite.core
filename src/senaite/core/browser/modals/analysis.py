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

import copy

from bika.lims import api
from bika.lims import FieldEditAnalysisConditions
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.content.attachment import Attachment
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

            if condition.get("type") == "file":
                uid = condition.get("value")
                condition["attachment"] = self.get_attachment_info(uid)

        # Move conditions from "file" type to the end:
        #   Cannot set conditions with a '<' char when others are from file
        #   https://github.com/senaite/senaite.core/pulls/2231
        def files_last(condition1, condition2):
            type1 = condition1.get("type")
            type2 = condition2.get("type")
            if "file" not in [type1, type2]:
                return 0
            return 1 if type1 == "file" else -1
        return sorted(conditions, cmp=files_last)

    def get_attachment_info(self, uid):
        attachment = api.get_object_by_uid(uid, default=None)
        if not isinstance(attachment, Attachment):
            return {}

        url = api.get_url(attachment)
        at_file = attachment.getAttachmentFile()
        return {
            "uid": api.get_uid(attachment),
            "id": api.get_id(attachment),
            "url": url,
            "download_url": "{}/at_download/AttachmentFile".format(url),
            "filename": at_file.filename,
        }

    def handle_submit(self):
        analysis = self.get_analysis()
        title = safe_unicode(api.get_title(analysis))
        if not check_permission(FieldEditAnalysisConditions, analysis):
            message = _("Not allowed to update conditions: {}").format(title)
            return self.redirect(message=message, level="error")

        # Sort the conditions as they were initially set
        conditions = self.request.form.get("conditions", [])
        original = self.get_analysis().getConditions(empties=True)
        original = [cond.get("title") for cond in original]

        def original_order(condition1, condition2):
            index1 = original.index(condition1.get("title"))
            index2 = original.index(condition2.get("title"))
            return (index1 > index2) - (index1 < index2)
        conditions = sorted(conditions, cmp=original_order)

        # Update the conditions
        analysis.setConditions(conditions)
        message = _("Analysis conditions updated: {}").format(title)
        return self.redirect(message=message)
