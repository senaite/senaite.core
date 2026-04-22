# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections
import datetime
import json
from calendar import monthrange
from operator import itemgetter
from time import time

from AccessControl import getSecurityManager
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api import get_current_client
from bika.lims.api import get_url
from bika.lims.api import search
from bika.lims.browser import BrowserView
from bika.lims.utils import get_strings
from DateTime import DateTime
from plone import api as ploneapi
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.permissions import AddAnalysisRequest
from senaite.core.permissions import EditResults
from senaite.core.permissions import ManageBika
from senaite.core.permissions import TransitionPublishResults
from senaite.core.permissions import TransitionReceiveSample
from senaite.core.permissions import TransitionVerify
from senaite.core.permissions import ViewDashboard
from senaite.core.permissions import ViewResults

DASHBOARD_FILTER_COOKIE = "dashboard_filter_cookie"

# Cache TTL for search counts (5 minutes)
SEARCH_CACHE_TTL = 60 * 5

# Supported periodicities for evolution charts
PERIODICITY_DAILY = "d"
PERIODICITY_WEEKLY = "w"
PERIODICITY_MONTHLY = "m"
PERIODICITY_QUARTERLY = "q"
PERIODICITY_BIANNUAL = "b"
PERIODICITY_YEARLY = "y"
PERIODICITY_ALL = "a"


class DashboardView(BrowserView):
    template = ViewPageTemplateFile("templates/dashboard.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.dashboard_cookie = None
        self.member = None

    def __call__(self):
        login_url = self.portal_url + "/login"

        # Client contacts go to their client page
        client = get_current_client()
        if client:
            return self.request.response.redirect(
                get_url(client))

        # Anonymous users go to login
        mtool = getToolByName(
            self.context, "portal_membership")
        if mtool.isAnonymousUser():
            return self.request.response.redirect(login_url)

        self.member = mtool.getAuthenticatedMember()
        self.periodicity = self.request.get(
            "p", PERIODICITY_WEEKLY)
        self.dashboard_cookie = self.check_dashboard_cookie()
        date_range = self.get_date_range(self.periodicity)
        self.date_from = date_range[0]
        self.date_to = date_range[1]

        return self.template()

    # --- Permission helpers ---

    def has_permission(self, permission):
        sm = getSecurityManager()
        return sm.checkPermission(permission, self.context)

    def can_view_statistics(self):
        """Check if user can see the statistics panels
        """
        return self.has_permission(ViewDashboard)

    def is_admin_user(self):
        """Check if the user has admin-level access
        """
        user = ploneapi.user.get_current()
        roles = user.getRoles()
        return "LabManager" in roles or "Manager" in roles

    # --- Greeting and status data ---

    def get_user_fullname(self):
        user = api.get_current_user()
        return api.get_user_fullname(user)

    def get_current_date(self):
        return datetime.datetime.now().strftime(
            "%A, %d %B %Y")

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M")

    def get_status_cards(self):
        cards = []

        if self.has_permission(TransitionReceiveSample):
            cards.append(self._make_card(
                title="Samples to Receive",
                portal_type="AnalysisRequest",
                review_state="sample_due",
                catalog=SAMPLE_CATALOG,
                url="samples?samples_review_state="
                    "sample_due",
                icon="fa-inbox",
            ))

        if self.has_permission(ViewResults):
            cards.append(self._make_card(
                title="Results Pending",
                portal_type="AnalysisRequest",
                review_state="sample_received",
                catalog=SAMPLE_CATALOG,
                url="samples?samples_review_state="
                    "sample_received",
                icon="fa-flask",
            ))

        if self.has_permission(TransitionVerify):
            cards.append(self._make_card(
                title="To be Verified",
                portal_type="AnalysisRequest",
                review_state="to_be_verified",
                catalog=SAMPLE_CATALOG,
                url="samples?samples_review_state="
                    "to_be_verified",
                icon="fa-check-circle",
            ))

        if self.has_permission(TransitionPublishResults):
            cards.append(self._make_card(
                title="To be Published",
                portal_type="AnalysisRequest",
                review_state="verified",
                catalog=SAMPLE_CATALOG,
                url="samples?samples_review_state=verified",
                icon="fa-paper-plane",
            ))

        if self.has_permission(EditResults):
            cards.append(self._make_card(
                title="Open Worksheets",
                portal_type="Worksheet",
                review_state="open",
                catalog=WORKSHEET_CATALOG,
                url="worksheets?list_review_state=open",
                icon="fa-th-list",
            ))

        return cards

    def _make_card(self, title, portal_type, review_state,
                   catalog, url, icon):
        count = len(search({
            "portal_type": portal_type,
            "review_state": review_state,
        }, catalog))
        return {
            "title": title,
            "count": count,
            "url": "{}/{}".format(self.portal_url, url),
            "icon": icon,
        }

    def get_quick_links(self):
        links = []

        if self.has_permission(AddAnalysisRequest):
            links.append({
                "title": "Register Samples",
                "url": "{}/{}".format(
                    self.portal_url, "samples"),
                "icon": "fa-plus-circle",
            })

        if self.has_permission(EditResults):
            links.append({
                "title": "Worksheets",
                "url": "{}/{}".format(
                    self.portal_url, "worksheets"),
                "icon": "fa-th-list",
            })

        if self.has_permission(TransitionVerify):
            links.append({
                "title": "Verify Results",
                "url": "{}/{}".format(
                    self.portal_url,
                    "samples?samples_review_state="
                    "to_be_verified"),
                "icon": "fa-check-double",
            })

        if self.has_permission(TransitionPublishResults):
            links.append({
                "title": "Publish Reports",
                "url": "{}/{}".format(
                    self.portal_url,
                    "samples?samples_review_state="
                    "verified"),
                "icon": "fa-paper-plane",
            })

        if self.has_permission(ManageBika):
            links.append({
                "title": "SENAITE Setup",
                "url": "{}/{}".format(
                    self.portal_url, "setup"),
                "icon": "fa-cog",
            })

        return links

    # --- Statistics sections ---

    def get_sections(self):
        """Returns the statistics sections
        """
        if not self.can_view_statistics():
            return []
        return [
            self.get_analysisrequests_section(),
            self.get_analyses_section(),
            self.get_worksheets_section(),
        ]

    # --- Cookie handling ---

    def check_dashboard_cookie(self):
        cookie_raw = self.request.get(
            DASHBOARD_FILTER_COOKIE, None)
        if cookie_raw is None:
            cookie_raw = self._create_raw_data()
            self.request.response.setCookie(
                DASHBOARD_FILTER_COOKIE,
                json.dumps(cookie_raw),
                quoted=False,
                path="/")
            return cookie_raw
        return get_strings(json.loads(cookie_raw))

    def _create_raw_data(self):
        result = {}
        for section in self.get_sections():
            result[section.get("id")] = "all"
        return result

    # --- Date range ---

    def get_date_range(self, periodicity=PERIODICITY_WEEKLY):
        today = datetime.date.today()
        if periodicity == PERIODICITY_DAILY:
            date_from = DateTime() - 30
            date_to = DateTime() + 1
            return date_from, date_to

        if periodicity == PERIODICITY_MONTHLY:
            min_year = (today.year - 1
                        if today.month == 12
                        else today.year - 2)
            min_month = (1
                         if today.month == 12
                         else today.month)
            date_from = DateTime(min_year, min_month, 1)
            date_to = DateTime(
                today.year, today.month,
                monthrange(today.year, today.month)[1],
                23, 59, 59)
            return date_from, date_to

        if periodicity == PERIODICITY_QUARTERLY:
            m = (((today.month - 1) / 3) * 3) + 1
            min_year = (today.year - 4
                        if today.month == 12
                        else today.year - 5)
            date_from = DateTime(min_year, m, 1)
            date_to = DateTime(
                today.year, m + 2,
                monthrange(today.year, m + 2)[1],
                23, 59, 59)
            return date_from, date_to

        if periodicity == PERIODICITY_BIANNUAL:
            m = (((today.month - 1) / 6) * 6) + 1
            min_year = (today.year - 10
                        if today.month == 12
                        else today.year - 11)
            date_from = DateTime(min_year, m, 1)
            date_to = DateTime(
                today.year, m + 5,
                monthrange(today.year, m + 5)[1],
                23, 59, 59)
            return date_from, date_to

        if periodicity in [PERIODICITY_YEARLY, PERIODICITY_ALL]:
            min_year = (today.year - 15
                        if today.month == 12
                        else today.year - 16)
            date_from = DateTime(min_year, 1, 1)
            date_to = DateTime(
                today.year, 12, 31, 23, 59, 59)
            return date_from, date_to

        # Default Weekly
        year, weeknum, dow = today.isocalendar()
        min_year = (today.year
                    if today.month > 6
                    else today.year - 1)
        min_month = (today.month - 6
                     if today.month > 6
                     else (today.month - 6) + 12)
        date_from = DateTime(min_year, min_month, 1)
        date_to = DateTime() - dow + 7
        return date_from, date_to

    # --- Statistics helpers ---

    def _getStatistics(
            self, name, description, url, catalog,
            criterias, total):
        out = {
            "type": "simple-panel",
            "name": name,
            "class": "informative",
            "description": description,
            "total": total,
            "link": self.portal_url + "/" + url,
        }

        results = 0
        ratio = 0
        if total > 0:
            results = self.search_count(
                criterias, catalog.id)
            results = (results
                       if total >= results
                       else total)
            ratio = ((float(results) / float(total)) * 100
                     if results > 0
                     else 0)
        ratio = str("%%.%sf" % 1) % ratio
        out["legend"] = (
            _("of") + " " + str(total)
            + " (" + ratio + "%)")
        out["number"] = results
        out["percentage"] = float(ratio)
        return out

    def get_analysisrequests_section(self):
        out = []
        catalog = getToolByName(
            self.context, SAMPLE_CATALOG)
        query = {
            "portal_type": "AnalysisRequest",
            "is_active": True,
        }
        query = self._update_criteria_with_filters(
            query, "analysisrequests")
        total = self.search_count(query, catalog.id)

        if self.context.bika_setup\
                .getSamplingWorkflowEnabled():
            name = _("Samples to be sampled")
            desc = _("To be sampled")
            purl = ("samples?samples_review_state="
                    "to_be_sampled")
            query["review_state"] = ["to_be_sampled"]
            out.append(self._getStatistics(
                name, desc, purl, catalog, query, total))

            name = _("Samples to be preserved")
            desc = _("To be preserved")
            purl = ("samples?samples_review_state="
                    "to_be_preserved")
            query["review_state"] = ["to_be_preserved"]
            out.append(self._getStatistics(
                name, desc, purl, catalog, query, total))

            name = _("Samples scheduled for sampling")
            desc = _("Sampling scheduled")
            purl = ("samples?samples_review_state="
                    "scheduled_sampling")
            query["review_state"] = ["scheduled_sampling"]
            out.append(self._getStatistics(
                name, desc, purl, catalog, query, total))

        name = _("Samples to be received")
        desc = _("Reception pending")
        purl = "samples?samples_review_state=sample_due"
        query["review_state"] = ["sample_due"]
        out.append(self._getStatistics(
            name, desc, purl, catalog, query, total))

        name = _("Samples with results pending")
        desc = _("Results pending")
        purl = ("samples?samples_review_state="
                "sample_received")
        query["review_state"] = ["sample_received"]
        out.append(self._getStatistics(
            name, desc, purl, catalog, query, total))

        name = _("Samples to be verified")
        desc = _("To be verified")
        purl = ("samples?samples_review_state="
                "to_be_verified")
        query["review_state"] = ["to_be_verified"]
        out.append(self._getStatistics(
            name, desc, purl, catalog, query, total))

        name = _("Samples verified")
        desc = _("Verified")
        purl = "samples?samples_review_state=verified"
        query["review_state"] = ["verified"]
        out.append(self._getStatistics(
            name, desc, purl, catalog, query, total))

        name = _("Samples published")
        desc = _("Published")
        purl = "samples?samples_review_state=published"
        query["review_state"] = ["published"]
        out.append(self._getStatistics(
            name, desc, purl, catalog, query, total))

        if self.context.bika_setup\
                .getPrintingWorkflowEnabled():
            name = _("Samples to be printed")
            desc = _("To be printed")
            purl = "samples?samples_getPrinted=0"
            query["getPrinted"] = "0"
            query["review_state"] = ["published"]
            out.append(self._getStatistics(
                name, desc, purl, catalog, query, total))

        outevo = self.fill_dates_evo(catalog, query)
        out.append({
            "type": "bar-chart-panel",
            "name": _("Evolution of Samples"),
            "class": "informative",
            "description": _("Evolution of Samples"),
            "data": json.dumps(outevo),
            "datacolors": json.dumps(
                self.get_colors_palette()),
        })

        return {
            "id": "analysisrequests",
            "title": _("Samples"),
            "panels": out,
        }

    def get_worksheets_section(self):
        out = []
        bc = getToolByName(self.context, WORKSHEET_CATALOG)
        query = {"portal_type": "Worksheet"}
        query = self._update_criteria_with_filters(
            query, "worksheets")
        total = self.search_count(query, bc.id)

        ws_folder = "worksheets?list_review_state={}"

        name = _("Results pending")
        desc = _("Results pending")
        purl = ws_folder.format("open")
        query["review_state"] = ["open"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        name = _("To be verified")
        desc = _("To be verified")
        purl = ws_folder.format("to_be_verified")
        query["review_state"] = ["to_be_verified"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        name = _("Verified")
        desc = _("Verified")
        purl = ws_folder.format("verified")
        query["review_state"] = ["verified"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        outevo = self.fill_dates_evo(bc, query)
        out.append({
            "type": "bar-chart-panel",
            "name": _("Evolution of Worksheets"),
            "class": "informative",
            "description": _("Evolution of Worksheets"),
            "data": json.dumps(outevo),
            "datacolors": json.dumps(
                self.get_colors_palette()),
        })

        return {
            "id": "worksheets",
            "title": _("Worksheets"),
            "panels": out,
        }

    def get_analyses_section(self):
        out = []
        bc = getToolByName(self.context, ANALYSIS_CATALOG)
        query = {
            "portal_type": "Analysis",
            "is_active": True,
        }
        query = self._update_criteria_with_filters(
            query, "analyses")
        total = self.search_count(query, bc.id)

        name = _("Assignment pending")
        desc = _("Assignment pending")
        purl = "#"
        query["review_state"] = ["unassigned"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        name = _("Results pending")
        desc = _("Results pending")
        purl = "#"
        query["review_state"] = ["unassigned", "assigned"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        name = _("To be verified")
        desc = _("To be verified")
        purl = "#"
        query["review_state"] = ["to_be_verified"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        name = _("Verified")
        desc = _("Verified")
        purl = "#"
        query["review_state"] = ["verified"]
        out.append(self._getStatistics(
            name, desc, purl, bc, query, total))

        outevo = self.fill_dates_evo(bc, query)
        out.append({
            "type": "bar-chart-panel",
            "name": _("Evolution of Analyses"),
            "class": "informative",
            "description": _("Evolution of Analyses"),
            "data": json.dumps(outevo),
            "datacolors": json.dumps(
                self.get_colors_palette()),
        })
        return {
            "id": "analyses",
            "title": _("Analyses"),
            "panels": out,
        }

    # --- Chart helpers ---

    def get_states_map(self, portal_type):
        if portal_type == "Analysis":
            return {
                "registered": _("Registered"),
                "unassigned": _("Assignment pending"),
                "assigned": _("Results pending"),
                "to_be_verified": _("To be verified"),
                "rejected": _("Rejected"),
                "retracted": _("Retracted"),
                "verified": _("Verified"),
                "published": _("Published"),
            }
        elif portal_type == "AnalysisRequest":
            return {
                "to_be_sampled": _("To be sampled"),
                "to_be_preserved": _("To be preserved"),
                "scheduled_sampling": _(
                    "Sampling scheduled"),
                "sample_due": _("Reception pending"),
                "rejected": _("Rejected"),
                "invalid": _("Invalid"),
                "sample_received": _("Results pending"),
                "assigned": _("Results pending"),
                "to_be_verified": _("To be verified"),
                "verified": _("Verified"),
                "published": _("Published"),
            }
        elif portal_type == "Worksheet":
            return {
                "open": _("Results pending"),
                "to_be_verified": _("To be verified"),
                "verified": _("Verified"),
            }
        return {}

    def get_colors_palette(self):
        """State color palette

        Colors aligned with base.scss state variables used in
        senaite.app.listing and throughout the UI.
        """
        return {
            # to_be_sampled (sampling specific)
            "to_be_sampled": "#917A4C",
            _("To be sampled"): "#917A4C",
            # to_be_preserved (sampling specific)
            "to_be_preserved": "#C2803E",
            _("To be preserved"): "#C2803E",
            # scheduled_sampling (sampling specific)
            "scheduled_sampling": "#F38630",
            _("Sampling scheduled"): "#F38630",
            # $state-sample_due-color
            "sample_due": "#ffff8d",
            _("Reception pending"): "#ffff8d",
            # $state-sample_received-color
            "sample_received": "#a1887f",
            _("Assignment pending"): "#a1887f",
            _("Sample received"): "#a1887f",
            # $state-unassigned-color
            "unassigned": "#f8f9fa",
            # $state-unassigned-active-color
            "assigned": "#ced4da",
            "open": "#ced4da",
            _("Results pending"): "#ced4da",
            # $state-rejected-color
            "rejected": "#6c757d",
            _("Rejected"): "#6c757d",
            # $state-retracted-color
            "retracted": "#ff6f00",
            _("Retracted"): "#ff6f00",
            # $state-invalid-color
            "invalid": "#e65100",
            _("Invalid"): "#e65100",
            # $state-to_be_verified-color
            "to_be_verified": "#18ffff",
            _("To be verified"): "#18ffff",
            # $state-verified-color
            "verified": "#0091ea",
            _("Verified"): "#0091ea",
            # $state-published-color
            "published": "#00c853",
            _("Published"): "#00c853",
            # $state-cancelled-color
            "cancelled": "#000000",
            _("Cancelled"): "#000000",
            # $state-active-color (registered/active)
            "registered": "#007bff",
            _("Registered"): "#007bff",
        }

    def _getDateStr(self, period, created):
        if period == PERIODICITY_YEARLY:
            created = created.year()
        elif period == PERIODICITY_BIANNUAL:
            m = (((created.month() - 1) / 6) * 6) + 1
            created = "%s-%s" % (
                str(created.year())[2:],
                str(m).zfill(2))
        elif period == PERIODICITY_QUARTERLY:
            m = (((created.month() - 1) / 3) * 3) + 1
            created = "%s-%s" % (
                str(created.year())[2:],
                str(m).zfill(2))
        elif period == PERIODICITY_MONTHLY:
            created = "%s-%s" % (
                str(created.year())[2:],
                str(created.month()).zfill(2))
        elif period == PERIODICITY_WEEKLY:
            year, weeknum, dow = (
                created.asdatetime().isocalendar())
            created = created - dow
            created = "%s-%s-%s" % (
                str(created.year())[2:],
                str(created.month()).zfill(2),
                str(created.day()).zfill(2))
        elif period == PERIODICITY_ALL:
            created = created.year()
        else:
            created = "%s-%s-%s" % (
                str(created.year())[2:],
                str(created.month()).zfill(2),
                str(created.day()).zfill(2))
        return created

    def fill_dates_evo(self, catalog, query):
        sorted_query = collections.OrderedDict(
            sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._fill_dates_evo(
            query_json, catalog.id, self.periodicity)

    def _fill_dates_evo_cachekey(
            _method, self, query_json, catalog_name,
            periodicity):
        hour = time() // (60 * 60 * 2)
        return hour, catalog_name, query_json, periodicity

    @ram.cache(_fill_dates_evo_cachekey)
    def _fill_dates_evo(
            self, query_json, catalog_name, periodicity):
        outevoidx = {}
        outevo = []
        days = 1
        if periodicity == PERIODICITY_YEARLY:
            days = 336
        elif periodicity == PERIODICITY_BIANNUAL:
            days = 168
        elif periodicity == PERIODICITY_QUARTERLY:
            days = 84
        elif periodicity == PERIODICITY_MONTHLY:
            days = 28
        elif periodicity == PERIODICITY_WEEKLY:
            days = 7
        elif periodicity == PERIODICITY_ALL:
            days = 336

        date_from, date_to = self.get_date_range(
            periodicity)
        query = json.loads(query_json)
        if "review_state" in query:
            del query["review_state"]
        query["sort_on"] = "created"
        query["created"] = {
            "query": (date_from, date_to),
            "range": "min:max",
        }

        otherstate = _("Other status")
        statesmap = self.get_states_map(
            query["portal_type"])
        stats = statesmap.values()
        stats.sort()
        stats.append(otherstate)
        statscount = {s: 0 for s in stats}
        curr = date_from.asdatetime()
        end = date_to.asdatetime()
        while curr < end:
            currstr = self._getDateStr(
                periodicity, DateTime(curr))
            if currstr not in outevoidx:
                outdict = {"date": currstr}
                for k in stats:
                    outdict[k] = 0
                outevo.append(outdict)
                outevoidx[currstr] = len(outevo) - 1
            curr = curr + datetime.timedelta(days=days)

        brains = search(query, catalog_name)
        for brain in brains:
            created = brain.created
            state = brain.review_state
            if state not in statesmap:
                logger.warn(
                    "'%s' State for '%s' not available"
                    % (state, query["portal_type"]))
            state = statesmap.get(state, otherstate)
            created = self._getDateStr(
                periodicity, created)
            statscount[state] += 1
            if created in outevoidx:
                oidx = outevoidx[created]
                if state in outevo[oidx]:
                    outevo[oidx][state] += 1
                else:
                    outevo[oidx][state] = 1
            else:
                currow = {"date": created, state: 1}
                outevo.append(currow)

        rstates = [
            k for k, v in statscount.items() if v == 0]
        for o in outevo:
            for r in rstates:
                if r in o:
                    del o[r]

        sorted_states = sorted(
            statscount.items(), key=itemgetter(1))
        sorted_states = map(
            lambda item: item[0], sorted_states)
        sorted_states.reverse()
        return {"data": outevo, "states": sorted_states}

    def search_count(self, query, catalog_name):
        sorted_query = collections.OrderedDict(
            sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._search_count(
            query_json, catalog_name)

    def _search_count_cachekey(
            _method, self, query_json, catalog_name):
        period = time() // SEARCH_CACHE_TTL
        return period, catalog_name, query_json

    @ram.cache(_search_count_cachekey)
    def _search_count(self, query_json, catalog_name):
        query = json.loads(query_json)
        brains = search(query, catalog_name)
        return len(brains)

    def _update_criteria_with_filters(
            self, query, section_name):
        if self.dashboard_cookie is None:
            return query
        cookie_criteria = self.dashboard_cookie.get(
            section_name)
        if cookie_criteria == "mine":
            query["Creator"] = self.member.getId()
        return query


class DashboardDataView(BrowserView):
    """JSON endpoint for async dashboard data loading

    Returns section data as JSON. Accepts a `section`
    parameter: status_cards, analysisrequests, analyses,
    worksheets, or quick_links.
    """

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json")

        mtool = getToolByName(
            self.context, "portal_membership")
        if mtool.isAnonymousUser():
            self.request.response.setStatus(403)
            return json.dumps({"error": "Unauthorized"})

        section = self.request.get("section", "")

        # Reuse DashboardView for all data methods
        view = DashboardView(self.context, self.request)
        view.member = mtool.getAuthenticatedMember()
        view.periodicity = self.request.get(
            "p", PERIODICITY_WEEKLY)
        view.dashboard_cookie = view.check_dashboard_cookie()
        date_range = view.get_date_range(view.periodicity)
        view.date_from = date_range[0]
        view.date_to = date_range[1]

        if section == "status_cards":
            return json.dumps(view.get_status_cards())

        if section == "quick_links":
            return json.dumps(view.get_quick_links())

        if section == "analysisrequests":
            data = view.get_analysisrequests_section()
            return json.dumps(data)

        if section == "analyses":
            data = view.get_analyses_section()
            return json.dumps(data)

        if section == "worksheets":
            data = view.get_worksheets_section()
            return json.dumps(data)

        self.request.response.setStatus(400)
        return json.dumps({"error": "Unknown section"})
