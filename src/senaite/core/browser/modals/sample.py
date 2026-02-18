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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api.worksheet import create_worksheet
from senaite.core.browser.modals import Modal
from senaite.core.catalog import SETUP_CATALOG


class CreateWorksheetModal(Modal):
    """Modal form handler that allows to assign all analyses to a new worksheet
    """
    template = ViewPageTemplateFile("templates/create_worksheet.pt")

    def __init__(self, context, request):
        super(CreateWorksheetModal, self).__init__(context, request)

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_submit(REQUEST=self.request)
        return self.template()

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_selected_samples(self):
        """Return selected samples

        :returns: selected Samples
        """
        return map(api.get_object, self.uids)

    def handle_submit(self, REQUEST=None):
        """Extract categories from request and create worksheet
        """
        analyst = self.request.form.get("analyst")
        template = self.request.form.get("template", "")
        instrument = self.request.form.get("instrument", "")
        analyses = self.get_analyses()

        ws = create_worksheet(analyst=analyst, instrument=instrument,
                              template=template, analyses=analyses)

        if not ws:
            return self.template()
        message = _(
            u"worksheet_created",
            default=u"Created worksheet ${ws_id}",
            mapping={"ws_id": ws.getId()},
        )
        self.add_status_message(message)
        # redirect to the new worksheet
        return api.get_url(ws)

    def get_analyses(self):
        categories = self.request.form.get("categories", [])
        samples = list(map(api.get_object, self.uids))

        categories = filter(None, api.to_list(categories))
        # filter out non-UIDs
        categories = list(filter(api.is_uid, categories))

        analyses = []
        for sample in samples:
            for analysis in sample.getAnalyses(full_objects=True):
                # if categories not empty then skip analyses that do not belong
                # to the selected categories
                if categories and analysis.getRawCategory() not in categories:
                    continue
                analyses.append(analysis)
        return analyses

    def get_analysis_categories(self):
        """Return analysis categories of the selected samples

        :returns: List available categories for the selected samples
        """
        categories = []
        for sample in self.get_selected_samples():
            for analysis in sample.getAnalyses(full_objects=True):
                # only consider unassigned analyses
                if api.get_workflow_status_of(analysis) != "unassigned":
                    continue
                # get the category of the analysis
                category = analysis.getCategory()
                if category in categories:
                    continue
                categories.append(category)

        categories = list(map(self.get_category_info,
                          sorted(categories, key=lambda c: c.getSortKey())))
        return categories

    def get_category_info(self, category):
        """Extract category information for template

        :returns: Dictionary of category information for the page template
        """
        return {
            "title": api.get_title(category),
            "uid": api.get_uid(category),
            "obj": category,
        }

    def get_analysts(self):
        """Returns all analyst users

        This function searches for users which have at least the Analyst role,
        and prepares a list of dictionaries for each user containing the
        username and fullname.

        :returns: List of analyst data dictionaries
        """
        #
        users = api.get_users_by_roles(["Manager", "LabManager", "Analyst"])
        analysts = []
        for user in users:
            username = user.getUserName()
            fullname = api.get_user_fullname(username)
            analysts.append({
                "username": username,
                "fullname": fullname or username,
            })
        # sort by fullname
        return sorted(analysts, key=lambda x: x.get("fullname").lower())

    def get_worksheet_templates(self):
        """Returns all WS templates

        This function searches for worksheet templates and prepares a list of
        dictionaries for each template containing the UID and the title.

        :returns: List of worksheet template data dictionaries
        """
        templates = [{"uid": "", "title": ""}]
        query = {
            "portal_type": "WorksheetTemplate",
            "is_active": True,
            "sort_on": "sortable_title",
        }
        results = api.search(query, SETUP_CATALOG)
        for brain in results:
            templates.append({
                "uid": api.get_uid(brain),
                "title": api.get_title(brain)
            })
        return templates
