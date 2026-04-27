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

# Periodicities for evolution charts
PERIODICITY_DAILY = "d"
PERIODICITY_WEEKLY = "w"
PERIODICITY_MONTHLY = "m"
PERIODICITY_QUARTERLY = "q"
PERIODICITY_BIANNUAL = "b"
PERIODICITY_YEARLY = "y"
PERIODICITY_ALL = "a"

# Days per bar segment for each periodicity
PERIODICITY_DAYS = {
    PERIODICITY_DAILY: 1,
    PERIODICITY_WEEKLY: 7,
    PERIODICITY_MONTHLY: 28,
    PERIODICITY_QUARTERLY: 84,
    PERIODICITY_BIANNUAL: 168,
    PERIODICITY_YEARLY: 336,
    PERIODICITY_ALL: 336,
}

# Status cards: (permission, title, portal_type,
#                review_state, catalog, url, icon)
STATUS_CARD_DEFS = [
    (TransitionReceiveSample, "Samples to Receive",
     "AnalysisRequest", "sample_due", SAMPLE_CATALOG,
     "samples?samples_review_state=sample_due",
     "fa-inbox"),
    (ViewResults, "Results Pending",
     "AnalysisRequest", "sample_received", SAMPLE_CATALOG,
     "samples?samples_review_state=sample_received",
     "fa-flask"),
    (TransitionVerify, "To be Verified",
     "AnalysisRequest", "to_be_verified", SAMPLE_CATALOG,
     "samples?samples_review_state=to_be_verified",
     "fa-check-circle"),
    (TransitionPublishResults, "To be Published",
     "AnalysisRequest", "verified", SAMPLE_CATALOG,
     "samples?samples_review_state=verified",
     "fa-paper-plane"),
    (EditResults, "Open Worksheets",
     "Worksheet", "open", WORKSHEET_CATALOG,
     "worksheets?list_review_state=open",
     "fa-th-list"),
]

# Quick action links: (permission, title, url, icon)
QUICK_LINK_DEFS = [
    (AddAnalysisRequest, "Register Samples",
     "samples", "fa-plus-circle"),
    (EditResults, "Worksheets",
     "worksheets", "fa-th-list"),
    (TransitionVerify, "Verify Results",
     "samples?samples_review_state=to_be_verified",
     "fa-check-double"),
    (TransitionPublishResults, "Publish Reports",
     "samples?samples_review_state=verified",
     "fa-paper-plane"),
    (ManageBika, "SENAITE Setup",
     "setup", "fa-cog"),
]

# State labels for evolution charts
ANALYSIS_STATES = collections.OrderedDict([
    ("registered", _("Registered")),
    ("unassigned", _("Assignment pending")),
    ("assigned", _("Results pending")),
    ("to_be_verified", _("To be verified")),
    ("rejected", _("Rejected")),
    ("retracted", _("Retracted")),
    ("verified", _("Verified")),
    ("published", _("Published")),
])

SAMPLE_STATES = collections.OrderedDict([
    ("to_be_sampled", _("To be sampled")),
    ("to_be_preserved", _("To be preserved")),
    ("scheduled_sampling", _("Sampling scheduled")),
    ("sample_due", _("Reception pending")),
    ("rejected", _("Rejected")),
    ("invalid", _("Invalid")),
    ("sample_received", _("Results pending")),
    ("assigned", _("Results pending")),
    ("to_be_verified", _("To be verified")),
    ("verified", _("Verified")),
    ("published", _("Published")),
])

WORKSHEET_STATES = collections.OrderedDict([
    ("open", _("Results pending")),
    ("to_be_verified", _("To be verified")),
    ("verified", _("Verified")),
])

STATES_MAP = {
    "Analysis": ANALYSIS_STATES,
    "AnalysisRequest": SAMPLE_STATES,
    "Worksheet": WORKSHEET_STATES,
}

OTHER_STATE_LABEL = _("Other status")

# Colors aligned with base.scss $state-*-color variables
STATE_COLORS = {
    "to_be_sampled": "#917A4C",
    "to_be_preserved": "#C2803E",
    "scheduled_sampling": "#F38630",
    "sample_due": "#ffff8d",        # $state-sample_due-color
    "sample_received": "#a1887f",   # $state-sample_received-color
    "unassigned": "#f8f9fa",        # $state-unassigned-color
    "assigned": "#ced4da",          # $state-unassigned-active-color
    "open": "#ced4da",
    "rejected": "#6c757d",          # $state-rejected-color
    "retracted": "#ff6f00",         # $state-retracted-color
    "invalid": "#e65100",           # $state-invalid-color
    "to_be_verified": "#18ffff",    # $state-to_be_verified-color
    "verified": "#0091ea",          # $state-verified-color
    "published": "#00c853",         # $state-published-color
    "cancelled": "#000000",         # $state-cancelled-color
    "registered": "#007bff",        # $state-active-color
}


def build_colors_palette():
    """Build the full color palette with both state keys
    and translated label keys for D3 chart lookups
    """
    palette = {}
    for states in STATES_MAP.values():
        for state_id, label in states.items():
            color = STATE_COLORS.get(state_id, "#999")
            palette[state_id] = color
            palette[label] = color
    return palette


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def format_date_label(period, created):
    """Format a DateTime into a chart x-axis label
    """
    year2 = str(created.year())[2:]
    if period in (PERIODICITY_YEARLY, PERIODICITY_ALL):
        return created.year()
    if period == PERIODICITY_BIANNUAL:
        m = (((created.month() - 1) / 6) * 6) + 1
        return "%s-%s" % (year2, str(m).zfill(2))
    if period == PERIODICITY_QUARTERLY:
        m = (((created.month() - 1) / 3) * 3) + 1
        return "%s-%s" % (year2, str(m).zfill(2))
    if period == PERIODICITY_MONTHLY:
        return "%s-%s" % (year2,
                          str(created.month()).zfill(2))
    if period == PERIODICITY_WEEKLY:
        _year, _week, dow = (
            created.asdatetime().isocalendar())
        created = created - dow
        return "%s-%s-%s" % (
            str(created.year())[2:],
            str(created.month()).zfill(2),
            str(created.day()).zfill(2))
    # Daily or fallback
    return "%s-%s-%s" % (
        year2,
        str(created.month()).zfill(2),
        str(created.day()).zfill(2))


# -------------------------------------------------------
# DashboardView
# -------------------------------------------------------

class DashboardView(BrowserView):
    """Main dashboard view

    Renders the page skeleton and provides data methods
    used by both the template and the JSON data endpoint.
    """
    template = ViewPageTemplateFile("templates/dashboard.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.dashboard_cookie = None
        self.member = None

    def __call__(self):
        # Client contacts go to their client page
        client = get_current_client()
        if client:
            return self.request.response.redirect(
                get_url(client))

        # Anonymous users go to login
        mtool = getToolByName(
            self.context, "portal_membership")
        if mtool.isAnonymousUser():
            login_url = self.portal_url + "/login"
            return self.request.response.redirect(
                login_url)

        self._setup(mtool)
        return self.template()

    def _setup(self, mtool=None):
        """Initialize view state from request

        Called by __call__ and reused by DashboardDataView.
        """
        if mtool is None:
            mtool = getToolByName(
                self.context, "portal_membership")
        self.member = mtool.getAuthenticatedMember()
        self.periodicity = self.request.get(
            "p", PERIODICITY_WEEKLY)
        self.dashboard_cookie = (
            self._read_dashboard_cookie())
        self.date_from, self.date_to = (
            self.get_date_range(self.periodicity))

    # --- Permissions ---

    def has_permission(self, permission):
        sm = getSecurityManager()
        return sm.checkPermission(
            permission, self.context)

    def can_view_statistics(self):
        return self.has_permission(ViewDashboard)

    # --- User info ---

    def get_user_fullname(self):
        user = api.get_current_user()
        return api.get_user_fullname(user)

    def get_current_date(self):
        return datetime.datetime.now().strftime(
            "%A, %d %B %Y")

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M")

    # --- Status cards ---

    def get_status_cards(self):
        cards = []
        for perm, title, ptype, state, cat, url, icon \
                in STATUS_CARD_DEFS:
            if not self.has_permission(perm):
                continue
            count = len(search({
                "portal_type": ptype,
                "review_state": state,
            }, cat))
            cards.append({
                "title": title,
                "count": count,
                "url": "%s/%s" % (self.portal_url, url),
                "icon": icon,
            })
        return cards

    # --- Quick links ---

    def get_quick_links(self):
        links = []
        for perm, title, url, icon in QUICK_LINK_DEFS:
            if not self.has_permission(perm):
                continue
            links.append({
                "title": title,
                "url": "%s/%s" % (self.portal_url, url),
                "icon": icon,
            })
        return links

    # --- Statistics sections ---

    def get_sections(self):
        if not self.can_view_statistics():
            return []
        return [
            self._build_samples_section(),
            self._build_analyses_section(),
            self._build_worksheets_section(),
        ]

    def _build_samples_section(self):
        catalog = getToolByName(
            self.context, SAMPLE_CATALOG)
        query = {
            "portal_type": "AnalysisRequest",
            "is_active": True,
        }
        query = self._apply_cookie_filter(
            query, "analysisrequests")
        total = self._cached_count(query, catalog.id)

        panels = []
        bika_setup = self.context.bika_setup

        if bika_setup.getSamplingWorkflowEnabled():
            panels += [
                self._panel(
                    _("To be sampled"), "to_be_sampled",
                    "samples", catalog, query, total),
                self._panel(
                    _("To be preserved"), "to_be_preserved",
                    "samples", catalog, query, total),
                self._panel(
                    _("Sampling scheduled"),
                    "scheduled_sampling",
                    "samples", catalog, query, total),
            ]

        panels += [
            self._panel(
                _("Reception pending"), "sample_due",
                "samples", catalog, query, total),
            self._panel(
                _("Results pending"), "sample_received",
                "samples", catalog, query, total),
            self._panel(
                _("To be verified"), "to_be_verified",
                "samples", catalog, query, total),
            self._panel(
                _("Verified"), "verified",
                "samples", catalog, query, total),
            self._panel(
                _("Published"), "published",
                "samples", catalog, query, total),
        ]

        if bika_setup.getPrintingWorkflowEnabled():
            q = dict(query, getPrinted="0",
                     review_state=["published"])
            count = self._cached_count(q, catalog.id)
            panels.append({
                "type": "simple-panel",
                "description": _("To be printed"),
                "number": count,
                "percentage": self._pct(count, total),
                "legend": self._legend(count, total),
                "link": "%s/samples?samples_getPrinted=0"
                        % self.portal_url,
            })

        panels.append(self._chart_panel(
            _("Evolution of Samples"), catalog, query))

        return {
            "id": "analysisrequests",
            "title": _("Samples"),
            "panels": panels,
        }

    def _build_analyses_section(self):
        catalog = getToolByName(
            self.context, ANALYSIS_CATALOG)
        query = {
            "portal_type": "Analysis",
            "is_active": True,
        }
        query = self._apply_cookie_filter(
            query, "analyses")
        total = self._cached_count(query, catalog.id)

        panels = [
            self._panel(
                _("Assignment pending"), "unassigned",
                None, catalog, query, total),
        ]

        # "Results pending" counts both states
        q = dict(query,
                 review_state=["unassigned", "assigned"])
        count = self._cached_count(q, catalog.id)
        panels.append({
            "type": "simple-panel",
            "description": _("Results pending"),
            "number": count,
            "percentage": self._pct(count, total),
            "legend": self._legend(count, total),
            "link": "#",
        })

        panels += [
            self._panel(
                _("To be verified"), "to_be_verified",
                None, catalog, query, total),
            self._panel(
                _("Verified"), "verified",
                None, catalog, query, total),
        ]

        panels.append(self._chart_panel(
            _("Evolution of Analyses"), catalog, query))

        return {
            "id": "analyses",
            "title": _("Analyses"),
            "panels": panels,
        }

    def _build_worksheets_section(self):
        catalog = getToolByName(
            self.context, WORKSHEET_CATALOG)
        query = {"portal_type": "Worksheet"}
        query = self._apply_cookie_filter(
            query, "worksheets")
        total = self._cached_count(query, catalog.id)

        panels = [
            self._panel(
                _("Results pending"), "open",
                "worksheets", catalog, query, total),
            self._panel(
                _("To be verified"), "to_be_verified",
                "worksheets", catalog, query, total),
            self._panel(
                _("Verified"), "verified",
                "worksheets", catalog, query, total),
        ]

        panels.append(self._chart_panel(
            _("Evolution of Worksheets"),
            catalog, query))

        return {
            "id": "worksheets",
            "title": _("Worksheets"),
            "panels": panels,
        }

    # --- Panel builders ---

    def _panel(self, description, review_state,
               listing_view, catalog, base_query, total):
        """Build a simple statistics panel
        """
        q = dict(base_query,
                 review_state=[review_state])
        count = self._cached_count(q, catalog.id)

        if listing_view:
            link = "%s/%s?%s_review_state=%s" % (
                self.portal_url, listing_view,
                listing_view, review_state)
        else:
            link = "#"

        return {
            "type": "simple-panel",
            "description": description,
            "number": count,
            "percentage": self._pct(count, total),
            "legend": self._legend(count, total),
            "link": link,
        }

    def _chart_panel(self, title, catalog, query):
        """Build an evolution bar chart panel
        """
        evo_data = self._evolution_data(
            catalog, query)
        return {
            "type": "bar-chart-panel",
            "name": title,
            "description": title,
            "data": json.dumps(evo_data),
            "datacolors": json.dumps(
                build_colors_palette()),
        }

    # --- Percentage / legend ---

    def _pct(self, count, total):
        if total == 0 or count == 0:
            return 0.0
        return round(
            (float(count) / float(total)) * 100, 1)

    def _legend(self, count, total):
        pct = self._pct(count, total)
        return "%s %s (%s%%)" % (
            _("of"), total, pct)

    # --- Cookie filter ---

    def _read_dashboard_cookie(self):
        cookie_raw = self.request.get(
            DASHBOARD_FILTER_COOKIE, None)
        if cookie_raw is None:
            cookie_raw = {}
            self.request.response.setCookie(
                DASHBOARD_FILTER_COOKIE,
                json.dumps(cookie_raw),
                quoted=False,
                path="/")
            return cookie_raw
        return get_strings(json.loads(cookie_raw))

    def _apply_cookie_filter(self, query, section_name):
        if self.dashboard_cookie is None:
            return query
        if self.dashboard_cookie.get(
                section_name) == "mine":
            query["Creator"] = self.member.getId()
        return query

    # --- Date range ---

    def get_date_range(
            self, periodicity=PERIODICITY_WEEKLY):
        today = datetime.date.today()

        if periodicity == PERIODICITY_DAILY:
            return DateTime() - 30, DateTime() + 1

        if periodicity == PERIODICITY_MONTHLY:
            min_year = (today.year - 1
                        if today.month == 12
                        else today.year - 2)
            min_month = (1 if today.month == 12
                         else today.month)
            return (
                DateTime(min_year, min_month, 1),
                DateTime(today.year, today.month,
                         monthrange(
                             today.year,
                             today.month)[1],
                         23, 59, 59))

        if periodicity == PERIODICITY_QUARTERLY:
            m = (((today.month - 1) / 3) * 3) + 1
            years_back = 4 if today.month == 12 else 5
            return (
                DateTime(today.year - years_back, m, 1),
                DateTime(today.year, m + 2,
                         monthrange(
                             today.year, m + 2)[1],
                         23, 59, 59))

        if periodicity == PERIODICITY_BIANNUAL:
            m = (((today.month - 1) / 6) * 6) + 1
            years_back = 10 if today.month == 12 else 11
            return (
                DateTime(today.year - years_back, m, 1),
                DateTime(today.year, m + 5,
                         monthrange(
                             today.year, m + 5)[1],
                         23, 59, 59))

        if periodicity in (PERIODICITY_YEARLY,
                           PERIODICITY_ALL):
            years_back = 15 if today.month == 12 else 16
            return (
                DateTime(today.year - years_back, 1, 1),
                DateTime(today.year, 12, 31, 23, 59, 59))

        # Default: weekly (last 6 months)
        _year, _weeknum, dow = today.isocalendar()
        min_year = (today.year if today.month > 6
                    else today.year - 1)
        min_month = (today.month - 6 if today.month > 6
                     else (today.month - 6) + 12)
        return (
            DateTime(min_year, min_month, 1),
            DateTime() - dow + 7)

    # --- Cached search count ---

    def _cached_count(self, query, catalog_name):
        sorted_query = collections.OrderedDict(
            sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._search_count(
            query_json, catalog_name)

    def _search_count_cachekey(
            func, instance, query_json, catalog_name):
        period = time() // SEARCH_CACHE_TTL
        return period, catalog_name, query_json

    @ram.cache(_search_count_cachekey)
    def _search_count(self, query_json, catalog_name):
        query = json.loads(query_json)
        return len(search(query, catalog_name))

    # --- Evolution chart data ---

    def _evolution_data(self, catalog, query):
        sorted_query = collections.OrderedDict(
            sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._fill_evolution(
            query_json, catalog.id, self.periodicity)

    def _fill_evolution_cachekey(
            func, instance, query_json, catalog_name,
            periodicity):
        hour = time() // (60 * 60 * 2)
        return hour, catalog_name, query_json, periodicity

    @ram.cache(_fill_evolution_cachekey)
    def _fill_evolution(
            self, query_json, catalog_name, periodicity):
        """Build evolution chart data grouped by period

        Returns {"data": [...], "states": [...]}.
        Cached for 2 hours.
        """
        days = PERIODICITY_DAYS.get(periodicity, 7)
        date_from, date_to = self.get_date_range(
            periodicity)

        query = json.loads(query_json)
        query.pop("review_state", None)
        query["sort_on"] = "created"
        query["created"] = {
            "query": (date_from, date_to),
            "range": "min:max",
        }

        portal_type = query["portal_type"]
        statesmap = STATES_MAP.get(portal_type, {})
        other_label = OTHER_STATE_LABEL

        # Initialize time buckets
        buckets, bucket_index = (
            self._init_buckets(
                date_from, date_to, days,
                periodicity, statesmap, other_label))

        # Count per state per bucket
        state_totals = self._count_per_bucket(
            query, catalog_name, statesmap,
            other_label, periodicity,
            buckets, bucket_index)

        # Remove empty states
        self._remove_empty_states(
            buckets, state_totals)

        # Sort states by total count descending
        sorted_states = [
            s for s, _ in sorted(
                state_totals.items(),
                key=itemgetter(1),
                reverse=True)]

        return {"data": buckets, "states": sorted_states}

    def _init_buckets(self, date_from, date_to, days,
                      periodicity, statesmap,
                      other_label):
        """Create empty time buckets for the chart
        """
        labels = list(statesmap.values())
        labels.sort()
        labels.append(other_label)

        buckets = []
        bucket_index = {}
        curr = date_from.asdatetime()
        end = date_to.asdatetime()

        while curr < end:
            label = format_date_label(
                periodicity, DateTime(curr))
            if label not in bucket_index:
                bucket = {"date": label}
                for s in labels:
                    bucket[s] = 0
                buckets.append(bucket)
                bucket_index[label] = len(buckets) - 1
            curr += datetime.timedelta(days=days)

        return buckets, bucket_index

    def _count_per_bucket(self, query, catalog_name,
                          statesmap, other_label,
                          periodicity, buckets,
                          bucket_index):
        """Iterate brains and tally counts per bucket
        """
        state_totals = {
            v: 0 for v in list(statesmap.values())
            + [other_label]}

        for brain in search(query, catalog_name):
            state = brain.review_state
            if state not in statesmap:
                logger.warn(
                    "'%s' State for '%s' not available"
                    % (state, query["portal_type"]))
            label = statesmap.get(state, other_label)
            date_label = format_date_label(
                periodicity, brain.created)

            state_totals[label] += 1

            if date_label in bucket_index:
                idx = bucket_index[date_label]
                buckets[idx][label] = (
                    buckets[idx].get(label, 0) + 1)
            else:
                buckets.append({
                    "date": date_label, label: 1})

        return state_totals

    def _remove_empty_states(self, buckets,
                             state_totals):
        """Remove states with zero total from all buckets
        """
        empty = [k for k, v in state_totals.items()
                 if v == 0]
        for bucket in buckets:
            for state in empty:
                bucket.pop(state, None)


# -------------------------------------------------------
# DashboardDataView (JSON endpoint)
# -------------------------------------------------------

SECTION_HANDLERS = {
    "status_cards": "get_status_cards",
    "quick_links": "get_quick_links",
    "analysisrequests": "_build_samples_section",
    "analyses": "_build_analyses_section",
    "worksheets": "_build_worksheets_section",
}


class DashboardDataView(BrowserView):
    """JSON endpoint for async dashboard data loading

    Accepts a ``section`` parameter and returns the
    corresponding data as JSON.
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
        handler_name = SECTION_HANDLERS.get(section)
        if not handler_name:
            self.request.response.setStatus(400)
            return json.dumps(
                {"error": "Unknown section"})

        view = DashboardView(self.context, self.request)
        view._setup(mtool)

        data = getattr(view, handler_name)()
        return json.dumps(data)
