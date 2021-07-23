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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections
import datetime
import json
from calendar import monthrange
from operator import itemgetter
from time import time

from DateTime import DateTime
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.utils import get_strings
from bika.lims.utils import get_unicode
from plone import api as ploneapi
from plone import protect
from plone.api.exc import InvalidParameterError
from plone.memoize import ram
from plone.memoize import view as viewcache

DASHBOARD_FILTER_COOKIE = 'dashboard_filter_cookie'

# Supported periodicities for evolution charts
PERIODICITY_DAILY = "d"
PERIODICITY_WEEKLY = "w"
PERIODICITY_MONTHLY = "m"
PERIODICITY_QUARTERLY = "q"
PERIODICITY_BIANNUAL = "b"
PERIODICITY_YEARLY = "y"
PERIODICITY_ALL = "a"


def get_dashboard_registry_record():
    """
    Return the 'bika.lims.dashboard_panels_visibility' values.
    :return: A dictionary or None
    """
    try:
        registry = ploneapi.portal.get_registry_record(
            'bika.lims.dashboard_panels_visibility')
        return registry
    except InvalidParameterError:
        # No entry in the registry for dashboard panels roles.
        # Maybe upgradestep 1.1.8 was not run?
        logger.warn("Cannot find a record with name "
                    "'bika.lims.dashboard_panels_visibility' in "
                    "registry_record. Missed upgrade 1.1.8?")
    return dict()


def set_dashboard_registry_record(registry_info):
    """
    Sets the 'bika.lims.dashboard_panels_visibility' values.

    :param registry_info: A dictionary type object with all its values as
    *unicode* objects.
    :return: A dictionary or None
    """
    try:
        ploneapi.portal.set_registry_record(
            'bika.lims.dashboard_panels_visibility', registry_info)
    except InvalidParameterError:
        # No entry in the registry for dashboard panels roles.
        # Maybe upgradestep 1.1.8 was not run?
        logger.warn("Cannot find a record with name "
                    "'bika.lims.dashboard_panels_visibility' in "
                    "registry_record. Missed upgrade 1.1.8?")


def setup_dashboard_panels_visibility_registry(section_name):
    """
    Initializes the values for panels visibility in registry_records. By
    default, only users with LabManager or Manager roles can see the panels.
    :param section_name:
    :return: An string like: "role1,yes,role2,no,rol3,no"
    """
    registry_info = get_dashboard_registry_record()
    role_permissions_list = []
    # Getting roles defined in the system
    roles = []
    acl_users = api.get_tool("acl_users")
    roles_tree = acl_users.portal_role_manager.listRoleIds()
    for role in roles_tree:
        roles.append(role)
    # Set view permissions to each role as 'yes':
    # "role1,yes,role2,no,rol3,no"
    for role in roles:
        role_permissions_list.append(role)
        visible = 'no'
        if role in ['LabManager', 'Manager']:
            visible = 'yes'
        role_permissions_list.append(visible)
    role_permissions = ','.join(role_permissions_list)

    # Set permissions string into dict
    registry_info[get_unicode(section_name)] = get_unicode(role_permissions)
    # Set new values to registry record
    set_dashboard_registry_record(registry_info)
    return registry_info


def get_dashboard_panels_visibility_by_section(section_name):
    """
    Return a list of pairs as values that represents the role-permission
    view relation for the panel section passed in.
    :param section_name: the panels section id.
    :return: a list of tuples.
    """
    registry_info = get_dashboard_registry_record()
    if section_name not in registry_info:
        # Registry hasn't been set, do it at least for this section
        registry_info = \
            setup_dashboard_panels_visibility_registry(section_name)

    pairs = registry_info.get(section_name)
    pairs = get_strings(pairs)
    if pairs is None:
        # In the registry, but with None value?
        setup_dashboard_panels_visibility_registry(section_name)
        return get_dashboard_panels_visibility_by_section(section_name)

    pairs = pairs.split(',')
    if len(pairs) == 0 or len(pairs) % 2 != 0:
        # Non-valid or malformed value
        setup_dashboard_panels_visibility_registry(section_name)
        return get_dashboard_panels_visibility_by_section(section_name)

    result = [
        (pairs[i], pairs[i + 1]) for i in range(len(pairs)) if i % 2 == 0]
    return result


def is_panel_visible_for_user(panel, user):
    """
    Checks if the user is allowed to see the panel
    :param panel: panel ID as string
    :param user: a MemberData object
    :return: Boolean
    """
    roles = user.getRoles()
    visibility = get_dashboard_panels_visibility_by_section(panel)
    for pair in visibility:
        if pair[0] in roles and pair[1] == 'yes':
            return True
    return False


class DashboardView(BrowserView):
    template = ViewPageTemplateFile("templates/dashboard.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.dashboard_cookie = None
        self.member = None

    def __call__(self):
        frontpage_url = self.portal_url + "/senaite-frontpage"
        if not self.context.bika_setup.getDashboardByDefault():
            # Do not render dashboard, render frontpage instead
            self.request.response.redirect(frontpage_url)
            return

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            # Anonymous user, redirect to frontpage
            self.request.response.redirect(frontpage_url)
            return

        self.member = mtool.getAuthenticatedMember()
        self.periodicity = self.request.get('p', PERIODICITY_WEEKLY)
        self.dashboard_cookie = self.check_dashboard_cookie()
        date_range = self.get_date_range(self.periodicity)
        self.date_from = date_range[0]
        self.date_to = date_range[1]

        return self.template()

    def check_dashboard_cookie(self):
        """
        Check if the dashboard cookie should exist through bikasetup
        configuration.

        If it should exist but doesn't exist yet, the function creates it
        with all values as default.
        If it should exist and already exists, it returns the value.
        Otherwise, the function returns None.

        :return: a dictionary of strings
        """
        # Getting cookie
        cookie_raw = self.request.get(DASHBOARD_FILTER_COOKIE, None)
        # If it doesn't exist, create it with default values
        if cookie_raw is None:
            cookie_raw = self._create_raw_data()
            self.request.response.setCookie(
                DASHBOARD_FILTER_COOKIE,
                json.dumps(cookie_raw),
                quoted=False,
                path='/')
            return cookie_raw
        return get_strings(json.loads(cookie_raw))

    def is_filter_selected(self, selection_id, value):
        """
        Compares whether the 'selection_id' parameter value saved in the
        cookie is the same value as the "value" parameter.

        :param selection_id: a string as a dashboard_cookie key.
        :param value: The value to compare against the value from
        dashboard_cookie key.
        :return: Boolean.
        """
        selected = self.dashboard_cookie.get(selection_id)
        return selected == value

    def is_admin_user(self):
        """
        Checks if the user is the admin or a SiteAdmin user.
        :return: Boolean
        """
        user = ploneapi.user.get_current()
        roles = user.getRoles()
        return "LabManager" in roles or "Manager" in roles

    def _create_raw_data(self):
        """
        Gathers the different sections ids and creates a string as first
        cookie data.

        :return: A dictionary like:
            {'analyses':'all','analysisrequest':'all','worksheets':'all'}
        """
        result = {}
        for section in self.get_sections():
            result[section.get('id')] = 'all'
        return result

    def get_date_range(self, periodicity=PERIODICITY_WEEKLY):
        """Returns a date range (date from, date to) that suits with the passed
        in periodicity.

        :param periodicity: string that represents the periodicity
        :type periodicity: str
        :return: A date range
        :rtype: [(DateTime, DateTime)]
        """
        today = datetime.date.today()
        if periodicity == PERIODICITY_DAILY:
            # Daily, load last 30 days
            date_from = DateTime() - 30
            date_to = DateTime() + 1
            return date_from, date_to

        if periodicity == PERIODICITY_MONTHLY:
            # Monthly, load last 2 years
            min_year = today.year - 1 if today.month == 12 else today.year - 2
            min_month = 1 if today.month == 12 else today.month
            date_from = DateTime(min_year, min_month, 1)
            date_to = DateTime(today.year, today.month,
                               monthrange(today.year, today.month)[1],
                               23, 59, 59)
            return date_from, date_to

        if periodicity == PERIODICITY_QUARTERLY:
            # Quarterly, load last 4 years
            m = (((today.month - 1) / 3) * 3) + 1
            min_year = today.year - 4 if today.month == 12 else today.year - 5
            date_from = DateTime(min_year, m, 1)
            date_to = DateTime(today.year, m + 2,
                               monthrange(today.year, m + 2)[1], 23, 59,
                               59)
            return date_from, date_to
        if periodicity == PERIODICITY_BIANNUAL:
            # Biannual, load last 10 years
            m = (((today.month - 1) / 6) * 6) + 1
            min_year = today.year - 10 if today.month == 12 else today.year - 11
            date_from = DateTime(min_year, m, 1)
            date_to = DateTime(today.year, m + 5,
                               monthrange(today.year, m + 5)[1], 23, 59,
                               59)
            return date_from, date_to

        if periodicity in [PERIODICITY_YEARLY, PERIODICITY_ALL]:
            # Yearly or All time, load last 15 years
            min_year = today.year - 15 if today.month == 12 else today.year - 16
            date_from = DateTime(min_year, 1, 1)
            date_to = DateTime(today.year, 12, 31, 23, 59, 59)
            return date_from, date_to

        # Default Weekly, load last six months
        year, weeknum, dow = today.isocalendar()
        min_year = today.year if today.month > 6 else today.year - 1
        min_month = today.month - 6 if today.month > 6 \
            else (today.month - 6) + 12
        date_from = DateTime(min_year, min_month, 1)
        date_to = DateTime() - dow + 7
        return date_from, date_to

    def get_sections(self):
        """ Returns an array with the sections to be displayed.
            Every section is a dictionary with the following structure:
                {'id': <section_identifier>,
                 'title': <section_title>,
                'panels': <array of panels>}
        """
        sections = []
        user = ploneapi.user.get_current()
        if is_panel_visible_for_user('analyses', user):
            sections.append(self.get_analyses_section())
        if is_panel_visible_for_user('analysisrequests', user):
            sections.append(self.get_analysisrequests_section())
        if is_panel_visible_for_user('worksheets', user):
            sections.append(self.get_worksheets_section())
        return sections

    def get_filter_options(self):
        """
        Returns dasboard filter options.
        :return: Boolean
        """
        dash_opt = DisplayList((
            ('all', _('All')),
            ('mine', _('Mine')),
        ))
        return dash_opt

    def translate_review_state(self, state, portal_type):
        """Translates the review state to the current set language

        :param state: Review state title
        :type state: basestring
        :returns: Translated review state title
        """
        ts = api.get_tool("translation_service")
        wf = api.get_tool("portal_workflow")
        state_title = wf.getTitleForStateOnType(state, portal_type)
        return ts.translate(_(state_title or state), context=self.request)

    def get_statistics(self, name, num, total, url=None):
        url = url or "#"
        out = {'type':        'simple-panel',
               'name':        name.capitalize(),
               'class':       'informative',
               #'description': name,
               'total':       total,
               'link':        self.portal_url + '/' + url}

        ratio = 0
        if total > 0:
            ratio = (float(num) / float(total)) * 100
        ratio = str("%%.%sf" % 1) % ratio
        out['legend'] = _('of') + " " + str(total) + ' (' + ratio + '%)'
        out['number'] = num
        out['percentage'] = float(ratio)
        return out

    def get_analysisrequests_section(self):
        """ Returns the section dictionary related with Analysis
            Requests, that contains some informative panels (like
            ARs to be verified, ARs to be published, etc.)
        """
        out = []

        # Display a box for each status, but published
        query = {"portal_type": "AnalysisRequest",
                 "is_active": True,
                 "is_published": False}

        # Check if dashboard_cookie contains additional query values
        query = self._update_criteria_with_filters(query, "analysisrequests")

        # Do the search and group by status
        total = 0
        groups = {}
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        for brain in brains:
            status = api.get_review_status(brain)
            groups.update({status: groups.get(status, 0) + 1})
            total += 1

        def sort_state(a, b):
            # Sort them. Status not present here are added at the end
            sort_order = [
                "to_be_sampled",
                "to_be_preserved",
                "scheduled_sampling",
                "sample_due",
                "attachment_due",
                "sample_received",
                "to_be_verified",
                "verified",
            ]
            a = a in sort_order and sort_order.index(a) or 98
            b = b in sort_order and sort_order.index(b) or 99
            return (a > b) - (a < b)

        statuses = sorted(groups.keys(), cmp=sort_state)
        for status in statuses:
            num = groups[status]
            name = self.translate_review_state(status, "AnalysisRequest")
            url = "analysisrequests?analysisrequests_review_state={}"
            url = url.format(status)
            stats = self.get_statistics(name, num, total, url)
            out.append(stats)

        # Samples to be printed
        if self.context.bika_setup.getPrintingWorkflowEnabled():
            not_printed = {
                "review_state": "published",
                "getPrinted": "0",
            }
            brains = api.search(not_printed, CATALOG_ANALYSIS_REQUEST_LISTING)
            total = len(brains)
            name = _("To be printed")
            url = 'analysisrequests?analysisrequests_getPrinted=0'
            stats = self.get_statistics(name, total, total, url)
            out.append(stats)

        # Chart with the evolution of ARs over a period, grouped by
        # periodicity
        query = {"portal_type": "AnalysisRequest"}
        catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
        out_evo = self.fill_dates_evo(catalog, query)
        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Samples'),
                    'class':        'informative',
                    'description':  _('Evolution of Samples'),
                    'data':         json.dumps(out_evo),
                    'datacolors':   json.dumps(self.get_colors_palette())})

        return {'id': 'analysisrequests',
                'title': _('Samples'),
                'panels': out}

    def get_worksheets_section(self):
        """ Returns the section dictionary related with Worksheets,
            that contains some informative panels (like
            WS to be verified, WS with results pending, etc.)
        """
        out = []
        statuses = ["open", "attachment_due", "to_be_verified"]
        query = {"portal_type": "Worksheet",
                 "review_state": statuses}

        # Check if dashboard_cookie contains additional query values
        query = self._update_criteria_with_filters(query, "worksheets")

        # Do the search
        total = 0
        groups = {}
        brains = api.search(query, CATALOG_WORKSHEET_LISTING)
        for brain in brains:
            status = api.get_review_status(brain)
            groups.update({status: groups.get(status, 0) + 1})
            total += 1

        statuses = filter(lambda s: s in groups.keys(), statuses)
        for status in statuses:
            num = groups[status]
            name = self.translate_review_state(status, "Worksheet")
            url = "worksheets?list_review_state={}".format(status)
            stats = self.get_statistics(name, num, total, url)
            out.append(stats)

        # Chart with the evolution of WSs over a period, grouped by
        query = {"portal_type": "Worksheet"}
        catalog = api.get_tool(CATALOG_WORKSHEET_LISTING)
        out_evo = self.fill_dates_evo(catalog, query)
        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Worksheets'),
                    'class':        'informative',
                    'description':  _('Evolution of Worksheets'),
                    'data':         json.dumps(out_evo),
                    'datacolors':   json.dumps(self.get_colors_palette())})

        return {'id': 'worksheets',
                'title': _('Worksheets'),
                'panels': out}

    def get_analyses_section(self):
        """ Returns the section dictionary related with Analyses,
            that contains some informative panels (analyses pending
            analyses assigned, etc.)
        """
        out = []
        statuses = ["unassigned", "assigned", "to_be_verified", "verified"]
        query = {"portal_type": "Analysis",
                 "review_state": statuses}

        # Check if dashboard_cookie contains additional query values
        query = self._update_criteria_with_filters(query, "analyses")

        # Do the search
        total = 0
        groups = {}
        brains = api.search(query, CATALOG_ANALYSIS_LISTING)
        for brain in brains:
            status = api.get_review_status(brain)
            groups.update({status: groups.get(status, 0) + 1})
            total += 1

        statuses = filter(lambda s: s in groups.keys(), statuses)
        for status in statuses:
            num = groups[status]
            name = self.translate_review_state(status, "Worksheet")
            stats = self.get_statistics(name, num, total)
            out.append(stats)

        # Chart with the evolution of Analyses over a period, grouped by
        # periodicity
        query = {"portal_type": "Analysis"}
        catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
        outevo = self.fill_dates_evo(catalog, query)
        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Analyses'),
                    'class':        'informative',
                    'description':  _('Evolution of Analyses'),
                    'data':         json.dumps(outevo),
                    'datacolors':   json.dumps(self.get_colors_palette())})
        return {'id': 'analyses',
                'title': _('Analyses'),
                'panels': out}

    def get_states_map(self, portal_type):
        if portal_type == 'Analysis':
            return {'unassigned':      _('Assignment pending'),
                    'assigned':        _('Results pending'),
                    'to_be_verified':  _('To be verified'),
                    'rejected':        _('Rejected'),
                    'retracted':       _('Retracted'),
                    'verified':        _('Verified'),
                    'published':       _('Published')}
        elif portal_type == 'AnalysisRequest':
            return {'to_be_sampled':       _('To be sampled'),
                    'to_be_preserved':     _('To be preserved'),
                    'scheduled_sampling':  _('Sampling scheduled'),
                    'sample_due':          _('Reception pending'),
                    'rejected':            _('Rejected'),
                    'invalid':             _('Invalid'),
                    'sample_received':     _('Results pending'),
                    'assigned':            _('Results pending'),
                    'attachment_due':      _('Results pending'),
                    'to_be_verified':      _('To be verified'),
                    'verified':            _('Verified'),
                    'published':           _('Published')}
        elif portal_type == 'Worksheet':
            return {'open':            _('Results pending'),
                    'attachment_due':  _('Results pending'),
                    'to_be_verified':  _('To be verified'),
                    'verified':        _('Verified')}

    def get_colors_palette(self):
        return {
            'to_be_sampled':                '#917A4C',
            _('To be sampled'):             '#917A4C',

            'to_be_preserved':              '#C2803E',
            _('To be preserved'):           '#C2803E',

            'scheduled_sampling':           '#F38630',
            _('Sampling scheduled'):        '#F38630',

            'sample_due':                   '#FA6900',
            _('Reception pending'):         '#FA6900',

            'sample_received':              '#E0E4CC',
            _('Assignment pending'):        '#E0E4CC',
            _('Sample received'):           '#E0E4CC',

            'assigned':                     '#dcdcdc',
            'attachment_due':               '#dcdcdc',
            'open':                         '#dcdcdc',
            _('Results pending'):           '#dcdcdc',

            'rejected':                     '#FF6B6B',
            'retracted':                    '#FF6B6B',
            _('Rejected'):                  '#FF6B6B',
            _('Retracted'):                 '#FF6B6B',

            'invalid':                      '#C44D58',
            _('Invalid'):                   '#C44D58',

            'to_be_verified':               '#A7DBD8',
            _('To be verified'):            '#A7DBD8',

            'verified':                     '#69D2E7',
            _('Verified'):                  '#69D2E7',

            'published':                    '#83AF9B',
            _('Published'):                 '#83AF9B',

            _('Other status'):              '#CDCDCD',

        }

    def _getDateStr(self, period, created):
        if period == PERIODICITY_YEARLY:
            created = created.year()
        elif period == PERIODICITY_BIANNUAL:
            m = (((created.month()-1)/6)*6)+1
            created = '%s-%s' % (str(created.year())[2:], str(m).zfill(2))
        elif period == PERIODICITY_QUARTERLY:
            m = (((created.month()-1)/3)*3)+1
            created = '%s-%s' % (str(created.year())[2:], str(m).zfill(2))
        elif period == PERIODICITY_MONTHLY:
            created = '%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2))
        elif period == PERIODICITY_WEEKLY:
            d = (((created.day()-1)/7)*7)+1
            year, weeknum, dow = created.asdatetime().isocalendar()
            created = created - dow
            created = '%s-%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2), str(created.day()).zfill(2))
        elif period == PERIODICITY_ALL:
            # All time, but evolution chart grouped by year
            created = created.year()
        else:
            created = '%s-%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2), str(created.day()).zfill(2))
        return created

    def fill_dates_evo(self, catalog, query):
        sorted_query = collections.OrderedDict(sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._fill_dates_evo(query_json, catalog.id, self.periodicity)

    def _fill_dates_evo_cachekey(method, self, query_json, catalog_name,
                                 periodicity):
        hour = time() // (60 * 60 * 2)
        return hour, catalog_name, query_json, periodicity

    @ram.cache(_fill_dates_evo_cachekey)
    def _fill_dates_evo(self, query_json, catalog_name, periodicity):
        """Returns an array of dictionaries, where each dictionary contains the
        amount of items created at a given date and grouped by review_state,
        based on the passed in periodicity.

        This is an expensive function that will not be called more than once
        every 2 hours (note cache decorator with `time() // (60 * 60 * 2)
        """
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

        # Get the date range
        date_from, date_to = self.get_date_range(periodicity)
        query = json.loads(query_json)
        if 'review_state' in query:
            del query['review_state']
        query['sort_on'] = 'created'
        query['created'] = {'query': (date_from, date_to),
                            'range': 'min:max'}

        otherstate = _('Other status')
        statesmap = self.get_states_map(query['portal_type'])
        stats = statesmap.values()
        stats.sort()
        stats.append(otherstate)
        statscount = {s: 0 for s in stats}
        # Add first all periods, cause we want all segments to be displayed
        curr = date_from.asdatetime()
        end = date_to.asdatetime()
        while curr < end:
            currstr = self._getDateStr(periodicity, DateTime(curr))
            if currstr not in outevoidx:
                outdict = {'date': currstr}
                for k in stats:
                    outdict[k] = 0
                outevo.append(outdict)
                outevoidx[currstr] = len(outevo)-1
            curr = curr + datetime.timedelta(days=days)

        brains = api.search(query, catalog_name)
        for brain in brains:
            created = brain.created
            state = brain.review_state
            state = statesmap[state] if state in statesmap else otherstate
            created = self._getDateStr(periodicity, created)
            statscount[state] += 1
            if created in outevoidx:
                oidx = outevoidx[created]
                if state in outevo[oidx]:
                    outevo[oidx][state] += 1
                else:
                    outevo[oidx][state] = 1
            else:
                # Create new row
                currow = {'date': created,
                          state: 1}
                outevo.append(currow)

        # Remove all those states for which there is no data
        rstates = [k for k, v in statscount.items() if v == 0]
        for o in outevo:
            for r in rstates:
                if r in o:
                    del o[r]

        # Sort available status by number of occurences descending
        sorted_states = sorted(statscount.items(), key=itemgetter(1))
        sorted_states = map(lambda item: item[0], sorted_states)
        sorted_states.reverse()
        return {'data': outevo, 'states': sorted_states}

    def search_count(self, query, catalog_name):
        sorted_query = collections.OrderedDict(sorted(query.items()))
        query_json = json.dumps(sorted_query)
        return self._search_count(query_json, catalog_name)

    @viewcache.memoize
    def _search_count(self, query_json, catalog_name):
        query = json.loads(query_json)
        brains = api.search(query, catalog_name)
        return len(brains)

    def _update_criteria_with_filters(self, query, section_name):
        """
        This method updates the 'query' dictionary with the criteria stored in
        dashboard cookie.

        :param query: A dictionary with search criteria.
        :param section_name: The dashboard section name
        :return: The 'query' dictionary
        """
        if self.dashboard_cookie is None:
            return query
        cookie_criteria = self.dashboard_cookie.get(section_name)
        if cookie_criteria == 'mine':
            query['Creator'] = self.member.getId()
        return query

    def get_dashboard_panels_visibility(self, section_name):
        """
        Return a list of pairs as values that represents the role-permission
        view relation for the panel section.
        :param section_name: the panels section id.
        :return: a list of tuples.
        """
        return get_dashboard_panels_visibility_by_section(section_name)


class DashboardViewPermissionUpdate(BrowserView):
    """
    Updates the values in 'bika.lims.dashboard_panels_visibility' registry.
    """

    def __call__(self):
        protect.CheckAuthenticator(self.request)
        # Getting values from post
        section_name = self.request.get('section_name', None)
        if section_name is None:
            return None
        role_id = self.request.get('role_id', None)
        if role_id is None:
            return None
        check_state = self.request.get('check_state', None)
        if check_state is None:
            return None
        elif check_state == 'false':
            check_state = 'no'
        else:
            check_state = 'yes'
        # Update registry
        registry_info = get_dashboard_registry_record()
        pairs = get_dashboard_panels_visibility_by_section(section_name)
        role_permissions = list()
        for pair in pairs:
            visibility = pair[1]
            if pair[0] == role_id:
                visibility = check_state
            value = '{0},{1}'.format(pair[0], visibility)
            role_permissions.append(value)
        role_permissions = ','.join(role_permissions)
        # Set permissions string into dict
        registry_info[section_name] = get_unicode(role_permissions)
        set_dashboard_registry_record(registry_info)
        return True
