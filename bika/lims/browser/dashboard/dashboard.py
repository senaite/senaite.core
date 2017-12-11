# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import datetime
import json
from calendar import monthrange

from DateTime import DateTime
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING


DASHBOARD_FILTER_COOKIE = 'dashboard_filter_cookie'


class DashboardView(BrowserView):
    template = ViewPageTemplateFile("templates/dashboard.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.dashboard_cookie = None

    def __call__(self):
        tofrontpage = True
        mtool=getToolByName(self.context, 'portal_membership')
        if not mtool.isAnonymousUser() and self.context.bika_setup.getDashboardByDefault():
            # If authenticated user with labman role,
            # display the Main Dashboard view
            pm = getToolByName(self.context, "portal_membership")
            member = pm.getAuthenticatedMember()
            roles = member.getRoles()
            tofrontpage = 'Manager' not in roles and 'LabManager' not in roles

        if tofrontpage:
            self.request.response.redirect(self.portal_url + "/bika-frontpage")
        else:
            self._init_date_range()
            self.dashboard_cookie = self.check_dashboard_cookie()
            return self.template()

    def check_dashboard_cookie(self):
        """
        Check if the dashboard cookie should exist through bikasetup
        configuration.

        If it should exist but doesn't exist yet, the function creates it
        with all values as default.
        If it should exist and already exists, it returns the value.
        Otherwise, the function returns None.

        :return: a dictionary or None
        """
        # Check setup configuration
        if not self.is_filter_enable():
            self.request.RESPONSE.setCookie(
                DASHBOARD_FILTER_COOKIE, None, path='/', max_age=0)
            return None
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
        return cookie_raw

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

    def _init_date_range(self):
        """ Sets the date range from which the data must be retrieved.
            Sets the values to the class parameters 'date_from',
            'date_to', 'date_range', and self.periodicity
            Calculates the date range according to the value of the
            request's 'p' parameter:
            - 'd' (daily)
            - 'w' (weekly)
            - 'm' (monthly)
            - 'q' (quarterly)
            - 'b' (biannual)
            - 'y' (yearly)
            - 'a' (all-time)
        """
        # By default, weekly
        self.periodicity = self.request.get('p', 'w')
        if (self.periodicity == 'd'):
            # Daily
            self.date_from = DateTime()
            self.date_to = DateTime() + 1
            # For time-evolution data, load last 30 days
            self.min_date = self.date_from - 30
        elif (self.periodicity == 'm'):
            # Monthly
            today = datetime.date.today()
            self.date_from = DateTime(today.year, today.month, 1)
            self.date_to = DateTime(today.year, today.month, monthrange(today.year, today.month)[1], 23, 59, 59)
            # For time-evolution data, load last two years
            min_year = today.year - 1 if today.month == 12 else today.year - 2
            min_month = 1 if today.month == 12 else today.month
            self.min_date = DateTime(min_year, min_month, 1)
        elif (self.periodicity == 'q'):
            # Quarterly
            today = datetime.date.today()
            m = (((today.month-1)/3)*3)+1
            self.date_from = DateTime(today.year, m, 1)
            self.date_to = DateTime(today.year, m+2, monthrange(today.year, m+2)[1], 23, 59, 59)
            # For time-evolution data, load last four years
            min_year = today.year - 4 if today.month == 12 else today.year - 5
            self.min_date = DateTime(min_year, m, 1)
        elif (self.periodicity == 'b'):
            # Biannual
            today = datetime.date.today()
            m = (((today.month-1)/6)*6)+1
            self.date_from = DateTime(today.year, m, 1)
            self.date_to = DateTime(today.year, m+5, monthrange(today.year, m+5)[1], 23, 59, 59)
            # For time-evolution data, load last ten years
            min_year = today.year - 10 if today.month == 12 else today.year - 11
            self.min_date = DateTime(min_year, m, 1)
        elif (self.periodicity == 'y'):
            # Yearly
            today = datetime.date.today()
            self.date_from = DateTime(today.year, 1, 1)
            self.date_to = DateTime(today.year, 12, 31, 23, 59, 59)
            # For time-evolution data, load last 15 years
            min_year = today.year - 15 if today.month == 12 else today.year - 16
            self.min_date = DateTime(min_year, 1, 1)
        elif (self.periodicity == 'a'):
            # All time
            today = datetime.date.today()
            self.date_from = DateTime('1990-01-01 00:00:00')
            self.date_to = DateTime(today.year, 12, 31, 23, 59, 59)
            # For time-evolution data, load last 15 years
            min_year = today.year - 15 if today.month == 12 else today.year - 16
            self.min_date = DateTime(min_year, 1, 1)
        else:
            # weekly
            today = datetime.date.today()
            year, weeknum, dow = today.isocalendar()
            self.date_from = DateTime() - dow
            self.date_to = self.date_from + 7
            # For time-evolution data, load last six months
            min_year = today.year if today.month > 6 else today.year - 1
            min_month = today.month - 6 if today.month > 6 else (today.month - 6)+12
            self.min_date = DateTime(min_year, min_month, 1)

        self.date_range = {'query': (self.date_from, self.date_to), 'range': 'min:max'}
        self.base_date_range = {'query': (DateTime('1990-01-01 00:00:00'), DateTime()+1), 'range':'min:max'}
        self.min_date_range = {'query': (self.min_date, self.date_to), 'range': 'min:max'}

    def get_sections(self):
        """ Returns an array with the sections to be displayed.
            Every section is a dictionary with the following structure:
                {'id': <section_identifier>,
                 'title': <section_title>,
                'panels': <array of panels>}
        """
        sections = [self.get_analyses_section(),
                    self.get_analysisrequests_section(),
                    self.get_worksheets_section()]
        return sections

    def is_filter_enable(self):
        """
        Returns whether the dashboard filter is enabled.
        :return: Boolean
        """
        return self.portal.bika_setup.getDashboardAllMine()

    def get_filter_options(self):
        """
        Returns whether the dashboard filter is enabled.
        :return: Boolean
        """
        dash_opt = DisplayList((
            ('all', _('All')),
            ('mine', _('Mine')),
        ))
        return dash_opt

    def _getStatistics(self, name, description, url, catalog, criterias, total):
        out = {'type':        'simple-panel',
               'name':        name,
               'class':       'informative',
               'description': description,
               'total':       total,
               'link':        self.portal_url + '/' + url}

        results = 0
        ratio = 0
        if total > 0:
            results = len(catalog(criterias))
            results = results if total >= results else total
            ratio = (float(results)/float(total))*100 if results > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        out['legend'] = _('of') + " " + str(total) + ' (' + ratio +'%)'
        out['number'] = results
        return out

    def get_analysisrequests_section(self):
        """ Returns the section dictionary related with Analysis
            Requests, that contains some informative panels (like
            ARs to be verified, ARs to be published, etc.)
        """
        out = []
        catalog = getToolByName(self.context, CATALOG_ANALYSIS_REQUEST_LISTING)
        query = {'portal_type': "AnalysisRequest",
                 'cancellation_state': ['active']}
        filtering_allowed = self.context.bika_setup.getAllowDepartmentFiltering()
        if filtering_allowed:
            cookie_dep_uid = self.request.get('filter_by_department_info', '').split(',') if filtering_allowed else ''
            query['getDepartmentUIDs'] = { "query": cookie_dep_uid,"operator":"or" }

        # Active Analysis Requests (All)
        total = len(catalog(query))

        # Sampling workflow enabled?
        if (self.context.bika_setup.getSamplingWorkflowEnabled()):
            # Analysis Requests awaiting to be sampled or scheduled
            name = _('Analysis Requests to be sampled')
            desc = _("To be sampled")
            purl = 'samples?samples_review_state=to_be_sampled'
            query['review_state'] = ['to_be_sampled', ]
            out.append(self._getStatistics(name, desc, purl, catalog, query, total))

            # Analysis Requests awaiting to be preserved
            name = _('Analysis Requests to be preserved')
            desc = _("To be preserved")
            purl = 'samples?samples_review_state=to_be_preserved'
            query['review_state'] = ['to_be_preserved', ]
            out.append(self._getStatistics(name, desc, purl, catalog, query, total))

            # Analysis Requests scheduled for Sampling
            name = _('Analysis Requests scheduled for sampling')
            desc = _("Sampling scheduled")
            purl = 'samples?samples_review_state=scheduled_sampling'
            query['review_state'] = ['scheduled_sampling', ]
            out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Analysis Requests awaiting for reception
        name = _('Analysis Requests to be received')
        desc = _("Reception pending")
        purl = 'analysisrequests?analysisrequests_review_state=sample_due'
        query['review_state'] = ['sample_due', ]
        out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Analysis Requests under way
        name = _('Analysis Requests with results pending')
        desc = _("Results pending")
        purl = 'analysisrequests?analysisrequests_review_state=sample_received'
        query['review_state'] = ['attachment_due',
                                 'sample_received',
                                 'assigned']
        out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Analysis Requests to be verified
        name = _('Analysis Requests to be verified')
        desc = _("To be verified")
        purl = 'analysisrequests?analysisrequests_review_state=to_be_verified'
        query['review_state'] = ['to_be_verified', ]
        out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Analysis Requests verified (to be published)
        name = _('Analysis Requests verified')
        desc = _("Verified")
        purl = 'analysisrequests?analysisrequests_review_state=verified'
        query['review_state'] = ['verified', ]
        out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Analysis Requests published
        name = _('Analysis Requests published')
        desc = _("Published")
        purl = 'analysisrequests?analysisrequests_review_state=published'
        query['review_state'] = ['published', ]
        out.append(self._getStatistics(name, desc, purl, catalog, query, total))

        # Chart with the evolution of ARs over a period, grouped by
        # periodicity
        del query['review_state']
        query['sort_on'] = 'created'
        query['created'] = self.min_date_range
        outevo = self._fill_dates_evo(catalog, query)
        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Analysis Requests'),
                    'class':        'informative',
                    'description':  _('Evolution of Analysis Requests'),
                    'data':         json.dumps(outevo),
                    'datacolors':   json.dumps(self.get_colors_palette())})

        return {'id': 'analysisrequests',
                'title': _('Analysis Requests'),
                'panels': out}

    def get_worksheets_section(self):
        """ Returns the section dictionary related with Worksheets,
            that contains some informative panels (like
            WS to be verified, WS with results pending, etc.)
        """
        out = []
        bc = getToolByName(self.context, CATALOG_WORKSHEET_LISTING)
        query = {'portal_type':"Worksheet",}
        filtering_allowed = self.context.bika_setup.getAllowDepartmentFiltering()
        if filtering_allowed:
            cookie_dep_uid = self.request.get('filter_by_department_info', '').split(',') if filtering_allowed else ''
            query['getDepartmentUIDs'] = { "query": cookie_dep_uid,"operator":"or" }

        # Active Worksheets (all)
        total = len(bc(query))

        # Open worksheets
        name = _('Results pending')
        desc = _('Results pending')
        purl = 'worksheets?list_review_state=open'
        query['review_state'] = ['open', 'attachment_due']
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Worksheets to be verified
        name = _('To be verified')
        desc =_('To be verified')
        purl = 'worksheets?list_review_state=to_be_verified'
        query['review_state'] = ['to_be_verified', ]
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Worksheets verified
        name = _('Verified')
        desc =_('Verified')
        purl = 'worksheets?list_review_state=verified'
        query['review_state'] = ['verified', ]
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Chart with the evolution of WSs over a period, grouped by
        # periodicity
        del query['review_state']
        query['sort_on'] = 'created'
        query['created'] = self.min_date_range
        outevo = self._fill_dates_evo(bc, query)
        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Worksheets'),
                    'class':        'informative',
                    'description':  _('Evolution of Worksheets'),
                    'data':         json.dumps(outevo),
                    'datacolors':   json.dumps(self.get_colors_palette())})

        return {'id': 'worksheets',
                'title': _('Worksheets'),
                'panels': out}

    def get_analyses_section(self):
        """ Returns the section dictionary related with Analyses,
            that contains some informative panels (analyses pending
            analyses assigned, etc.)

            sample_registered, not_requested, published, retracted,
            sample_due, sample_received, sample_prep, sampled, to_be_preserved,
            to_be_sampled, , to_be_verified, rejected, verified, to_be_verified,
            assigned
        """
        out = []
        bc = getToolByName(self.context, CATALOG_ANALYSIS_LISTING)
        query = {'portal_type': "Analysis",
                 'cancellation_state': ['active']}
        filtering_allowed = self.context.bika_setup.getAllowDepartmentFiltering()
        if filtering_allowed:
            cookie_dep_uid = self.request.get('filter_by_department_info', '').split(',') if filtering_allowed else ''
            query['getDepartmentUID'] = { "query": cookie_dep_uid,"operator":"or" }

        # Active Analyses (All)
        total = len(bc(query))

        # Analyses to be assigned
        name = _('Assignment pending')
        desc = _('Assignment pending')
        purl = 'aggregatedanalyses'
        query['review_state'] = ['sample_received', ]
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Analyses pending
        name = _('Results pending')
        desc = _('Results pending')
        purl = 'aggregatedanalyses'
        query['review_state'] = ['assigned','attachment_due']
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Analyses to be verified
        name = _('To be verified')
        desc = _('To be verified')
        purl = 'aggregatedanalyses'
        query['review_state'] = ['to_be_verified', ]
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Analyses verified
        name = _('Verified')
        desc = _('Verified')
        purl = 'aggregatedanalyses'
        query['review_state'] = ['verified', ]
        out.append(self._getStatistics(name, desc, purl, bc, query, total))

        # Chart with the evolution of Analyses over a period, grouped by
        # periodicity
        del query['review_state']
        query['sort_on'] = 'created'
        query['created'] = self.min_date_range
        outevo = self._fill_dates_evo(bc, query)
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
            return {'to_be_sampled':   _('Sample reception pending'),
                    'sample_due':      _('Sample reception pending'),
                    'sample_received': _('Assignment pending'),
                    'assigned':        _('Results pending'),
                    'attachment_due':  _('Results pending'),
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
            'to_be_sampled':                '#FA6900',
            _('To be sampled'):             '#FA6900',

            'to_be_preserved':              '#C44D58',
            _('To be preserved'):           '#C44D58',

            'scheduled_sampling':           '#FA6900',
            _('Sampling scheduled'):        '#FA6900',

            'sample_due':                   '#F38630',
            _('Sample reception pending'):  '#F38630',
            _('Reception pending'):         '#F38630',

            'sample_received':              '#E0E4CC',
            _('Assignment pending'):        '#E0E4CC',

            'assigned':                     '#dcdcdc',
            'attachment_due':               '#dcdcdc',
            'open':                         '#dcdcdc',
            _('Results pending'):           '#dcdcdc',

            'rejected':                     '#FF6B6B',
            'retracted':                    '#FF6B6B',
            _('Rejected'):                  '#FF6B6B',
            _('Retracted'):                 '#FF6B6B',

            'to_be_verified':               '#A7DBD8',
            _('To be verified'):            '#A7DBD8',

            'verified':                     '#69D2E7',
            _('Verified'):                  '#69D2E7',

            'published':                    '#83AF9B',
            _('Published'):                 '#83AF9B',
        }

    def _getDateStr(self, period, created):
        if period == 'y':
            created = created.year()
        elif period == 'b':
            m = (((created.month()-1)/6)*6)+1
            created = '%s-%s' % (str(created.year())[2:], str(m).zfill(2))
        elif period == 'q':
            m = (((created.month()-1)/3)*3)+1
            created = '%s-%s' % (str(created.year())[2:], str(m).zfill(2))
        elif period == 'm':
            created = '%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2))
        elif period == 'w':
            d = (((created.day()-1)/7)*7)+1
            year, weeknum, dow = created.asdatetime().isocalendar()
            created = created - dow
            created = '%s-%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2), str(created.day()).zfill(2))
        elif period == 'a':
            # All time, but evolution chart grouped by year
            created = created.year()
        else:
            created = '%s-%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2), str(created.day()).zfill(2))
        return created

    def _fill_dates_evo(self, catalog, query):
        outevoidx = {}
        outevo = []
        days = 1
        if self.periodicity == 'y':
            days = 336
        elif self.periodicity == 'b':
            days = 168
        elif self.periodicity == 'q':
            days = 84
        elif self.periodicity == 'm':
            days = 28
        elif self.periodicity == 'w':
            days = 7
        elif self.periodicity == 'a':
            days = 336

        otherstate = _('Other status')
        statesmap = self.get_states_map(query['portal_type'])
        stats = statesmap.values()
        stats.sort()
        stats.append(otherstate)
        statscount = {s:0 for s in stats}
        # Add first all periods, cause we want all segments to be displayed
        curr = self.min_date.asdatetime()
        end = self.date_to.asdatetime()
        while curr < end:
            currstr = self._getDateStr(self.periodicity, DateTime(curr))
            if currstr not in outevoidx:
                outdict = {'date':currstr}
                for k in stats:
                    outdict[k] = 0
                outevo.append(outdict)
                outevoidx[currstr] = len(outevo)-1
            curr = curr + datetime.timedelta(days=days)
        for brain in catalog(query):
            # Check if we can use the brain
            if query.get('portal_type', '') in ['AnalysisRequest', 'Analysis']:
                created = brain.created
            # I not, get the object
            else:
                created = brain.getObject().created()
            state = brain.review_state
            if state not in statesmap:
                logger.warn("'%s' State for '%s' not available" % (state, query['portal_type']))
            state = statesmap[state] if state in statesmap else otherstate
            created = self._getDateStr(self.periodicity, created)
            if created in outevoidx:
                oidx = outevoidx[created]
                statscount[state] += 1
                if state in outevo[oidx]:
                    outevo[oidx][state] += 1
                else:
                    outevo[oidx][state] = 1
            else:
                # Create new row
                currow = {'date': created,
                          state: 1 }
                outevo.append(currow)

        # Remove all those states for which there is no data
        rstates = [k for k,v in statscount.items() if v==0]
        for o in outevo:
            for r in rstates:
                if r in o:
                    del o[r]

        return outevo
