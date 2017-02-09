# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims import bikaMessageFactory as _
from calendar import monthrange
from DateTime import DateTime
import plone
import json
import datetime


class DashboardView(BrowserView):
    template = ViewPageTemplateFile("templates/dashboard.pt")

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

        if tofrontpage == True:
            self.request.response.redirect(self.portal_url + "/bika-frontpage")
        else:
            self._init_date_range()
            return self.template()

    def _init_date_range(self):
        """ Sets the date range from which the data must be retrieved.
            Sets the values to the class parameters 'date_from',
            'date_to', 'date_range', 'base_date_range' and self.periodicity
            Calculates the date range according to the value of the
            request's 'p' parameter:
            - 'd' (daily)
            - 'w' (weekly)
            - 'm' (monthly)
            - 'q' (quarterly)
            - 'b' (biannual)
            - 'y' (yearly)
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
        self.base_date_range = {'query': (DateTime('1990-01-01 00:00:00'), self.date_from - 1), 'range':'min:max'}
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

    def get_analysisrequests_section(self):
        """ Returns the section dictionary related with Analysis
            Requests, that contains some informative panels (like
            ARs to be verified, ARs to be published, etc.)
        """
        out = []
        sampenabled = self.context.bika_setup.getSamplingWorkflowEnabled()
        filtering_allowed =\
            self.context.bika_setup.getAllowDepartmentFiltering()
        cookie_dep_uid = \
            self.request.get('filter_by_department_info', '').split(',')\
            if filtering_allowed else ''

        # Analysis Requests
        active_rs = ['to_be_sampled',
                     'to_be_preserved',
                     'scheduled_sampling',
                     'sample_due',
                     'sample_received',
                     'assigned',
                     'to_be_verified',
                     'attachment_due',
                     'verified']
        catalog = getToolByName(self.context, CATALOG_ANALYSIS_REQUEST_LISTING)
        query_dic = {'portal_type': "AnalysisRequest",
                     'created': self.date_range,
                     'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        numars = len(catalog(query_dic))
        query_dic = {'portal_type': "AnalysisRequest",
                     'review_state': active_rs,
                     'created': self.base_date_range,
                     'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        numars += len(catalog(query_dic))
        if (sampenabled):
            # Analysis Requests awaiting to be sampled or scheduled
            review_state = ['to_be_sampled', ]
            query_dic = {
                'portal_type': "AnalysisRequest",
                'review_state': review_state,
                'cancellation_state': ['active']}
            if filtering_allowed:
                query_dic['getDepartmentUIDs'] = {
                    "query": cookie_dep_uid, "operator": "or"}
            ars = len(catalog(query_dic))
            ratio = (float(ars)/float(numars))*100 if\
                ars > 0 and numars > 0 else 0
            ratio = str("%%.%sf" % 1) % ratio
            msg = _("To be sampled")
            out.append({
                'type': 'simple-panel',
                'name': _('Analysis Requests to be sampled'),
                'class': 'informative',
                'description': msg,
                'number': ars,
                'total': numars,
                'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
                'link': self.portal_url +
                        '/samples?samples_review_state=to_be_sampled'})

            # Analysis Requests awaiting to be preserved
            review_state = ['to_be_preserved', ]
            query_dic = {
                'portal_type': "AnalysisRequest",
                'review_state': review_state,
                'cancellation_state': ['active']}
            if filtering_allowed:
                query_dic['getDepartmentUIDs'] = {
                    "query": cookie_dep_uid, "operator": "or"}
            ars = len(catalog(query_dic))
            ratio = (float(ars)/float(numars))*100\
                if ars > 0 and numars > 0 else 0
            ratio = str("%%.%sf" % 1) % ratio
            msg = _("To be preserved")
            out.append({
                'type': 'simple-panel',
                'name': _('Analysis Requests to be preserved'),
                'class': 'informative',
                'description': msg,
                'number': ars,
                'total': numars,
                'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
                'link': self.portal_url +
                        '/analysisrequests?' +
                        'analysisrequests_review_state=to_be_preserved'
                })
            # Analysis Requests awaiting to be sampled
            review_state = ['scheduled_sampling', ]
            query_dic = {
                'portal_type': "AnalysisRequest",
                'review_state': review_state,
                'cancellation_state': ['active']}
            if filtering_allowed:
                query_dic['getDepartmentUIDs'] = {
                    "query": cookie_dep_uid, "operator": "or"}
            ars = len(catalog(query_dic))
            ratio = (float(ars)/float(numars))*100 if\
                ars > 0 and numars > 0 else 0
            ratio = str("%%.%sf" % 1) % ratio
            msg = _("Scheduled sampling")
            out.append({
                'type': 'simple-panel',
                'name': _('Analysis Requests with scheduled sampling'),
                'class': 'informative',
                'description': msg,
                'number': ars,
                'total': numars,
                'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
                'link': self.portal_url +
                        '/samples?samples_review_state=to_be_sampled'})

        # Analysis Requests awaiting for reception
        review_state = ['sample_due', ]
        query_dic = {
            'portal_type': "AnalysisRequest",
            'review_state': review_state,
            'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        ars = len(catalog(query_dic))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Reception pending")
        out.append({
            'type': 'simple-panel',
            'name': _('Analysis Requests to be received'),
            'class': 'informative',
            'description': msg,
            'number': ars,
            'total': numars,
            'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
            'link': self.portal_url +
                    '/analysisrequests?' +
                    'analysisrequests_review_state=sample_due'})

        # Analysis Requests under way
        review_state = ['attachment_due', 'sample_received', 'assigned']
        query_dic = {
            'portal_type': "AnalysisRequest",
            'review_state': review_state,
            'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        ars = len(catalog(query_dic))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Results pending")
        out.append({
            'type': 'simple-panel',
            'name': _('Analysis Requests with results pending'),
            'class': 'informative',
            'description': msg,
            'number': ars,
            'total': numars,
            'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
            'link': self.portal_url +
                    '/analysisrequests?' +
                    'analysisrequests_review_state=sample_received'})

        # Analysis Requests to be verified
        review_state = ['to_be_verified', ]
        query_dic = {
            'portal_type': "AnalysisRequest",
            'review_state': review_state,
            'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        ars = len(catalog(query_dic))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be verified")
        out.append({
            'type': 'simple-panel',
            'name': _('Analysis Requests to be verified'),
            'class': 'informative',
            'description': msg,
            'number': ars,
            'total': numars,
            'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
            'link': self.portal_url +
                    '/analysisrequests?' +
                    'analysisrequests_review_state=to_be_verified'})

        # Analysis Requests to be published
        review_state = ['verified', ]
        query_dic = {
            'portal_type': "AnalysisRequest",
            'review_state': review_state,
            'cancellation_state': ['active']}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        ars = len(catalog(query_dic))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be published")
        out.append({
            'type': 'simple-panel',
            'name': _('Analysis Requests to be published'),
            'class': 'informative',
            'description': msg,
            'number': ars,
            'total': numars,
            'legend': _('of') + " " + str(numars) + ' (' + ratio + '%)',
            'link': self.portal_url +
                    '/analysisrequests?analysisrequests_review_state=verified'
            })

        # Chart with the evolution of ARs over a period, grouped by
        # periodicity
        workflow = getToolByName(self.context, 'portal_workflow')
        query_dic = {
            'portal_type': "AnalysisRequest",
            'sort_on': "created",
            'created': self.min_date_range}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = {
                "query": cookie_dep_uid, "operator": "or"}
        allars = catalog(query_dic)
        outevo = []
        for ar in allars:
            state = 'other_status'
            states_dict = ar.getObjectWorkflowStates
            state = states_dict.get('cancellation_state', '')
            if (state == 'active'):
                state = states_dict.get('review_state', 'inactive')
            else:
                state = 'inactive'

            created = self._getDateStr(self.periodicity, ar.created)
            state = 'sample_due' if \
                state in ['to_be_sampled', 'to_be_preserved'] else state
            state = 'sample_received' if \
                state in ['assigned', 'attachment_due'] else state
            if (len(outevo) > 0 and outevo[-1]['date'] == created):
                key = state if _(state) in outevo[-1] else 'other_status'
                outevo[-1][_(key)] += 1
            else:
                currow = {
                    'date': created,
                    _('sample_due'): 0,
                    _('sample_received'): 0,
                    _('to_be_verified'): 0,
                    _('verified'): 0,
                    _('published'): 0,
                    _('inactive'): 0,
                    _('other_status'): 0,
                   }
                key = state if _(state) in currow else 'other_status'
                currow[_(key)] += 1
                outevo.append(currow)

        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Analysis Requests'),
                    'class':        'informative',
                    'description':  _('Evolution of Analysis Requests'),
                    'data':         json.dumps(outevo)})

        return {'id': 'analysisrequests',
                'title': _('Analysis Requests'),
                'panels': out}

    def get_worksheets_section(self):
        """ Returns the section dictionary related with Worksheets,
            that contains some informative panels (like
            WS to be verified, WS with results pending, etc.)
        """
        out = []
        bc = getToolByName(self.context, "bika_catalog")
        filtering_allowed=self.context.bika_setup.getAllowDepartmentFiltering()
        cookie_dep_uid = self.request.get('filter_by_department_info', '').split(',') if filtering_allowed else ''
        active_ws = ['open', 'to_be_verified', 'attachment_due']

        query_dic = {'portal_type':"Worksheet",
                 'created':self.date_range}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = { "query":cookie_dep_uid,"operator":"or" }
        numws = len(bc(query_dic))

        query_dic = {'portal_type':"Worksheet",
                 'review_state':active_ws,
                 'created':self.base_date_range}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = { "query":cookie_dep_uid,"operator":"or" }
        numws += len(bc(query_dic))

        # Open worksheets
        review_state = ['open', 'attachment_due']
        query_dic = {'portal_type':"Worksheet",
                 'review_state':review_state,
                   'created':self.base_date_range}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = { "query":cookie_dep_uid,"operator":"or" }
        ws = len(bc(query_dic))
        ratio = (float(ws)/float(numws))*100 if ws > 0 and numws > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Results pending")
        out.append({'type':         'simple-panel',
                    'name':         _('Results pending'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ws,
                    'total':        numws,
                    'legend':       _('of') + " " + str(numws) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/worksheets?list_review_state=open'})

        # Worksheets to be verified
        review_state = ['to_be_verified', ]
        query_dic = {'portal_type':"Worksheet",
                 'review_state':review_state}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = { "query":cookie_dep_uid,"operator":"or" }
        ws = len(bc(query_dic))
        ratio = (float(ws)/float(numws))*100 if ws > 0 and numws > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be verified")
        out.append({'type':         'simple-panel',
                    'name':         _('To be verified'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ws,
                    'total':        numws,
                    'legend':       _('of') + " " + str(numws) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/worksheets?list_review_state=to_be_verified'})

        # Chart with the evolution of WSs over a period, grouped by
        # periodicity
        workflow = getToolByName(self.context, 'portal_workflow')
        query_dic = {'portal_type':"Worksheet",
                 'sort_on':"created",
                 'created':self.min_date_range}
        if filtering_allowed:
            query_dic['getDepartmentUIDs'] = { "query":cookie_dep_uid,"operator":"or" }
        allws = bc(query_dic)
        outevo = []
        for ws in allws:
            ws = ws.getObject()
            state = 'other_status'
            try:
                state = workflow.getInfoFor(ws, 'cancellation_state')
                if (state == 'active'):
                    state = workflow.getInfoFor(ws, 'review_state')
                else:
                    state = 'inactive'
            except:
                pass

            created = self._getDateStr(self.periodicity, ws.created())

            if (len(outevo) > 0 and outevo[-1]['date'] == created):
                key = state if _(state) in outevo[-1] else 'other_status'
                outevo[-1][_(key)] += 1
            else:
                currow = {'date': created,
                   _('open'): 0,
                   _('to_be_verified'): 0,
                   _('attachment_due'): 0,
                   _('verified'): 0,
                   _('inactive'): 0,
                   _('other_status'): 0,
                   }
                key = state if _(state) in currow else 'other_status'
                currow[_(key)] += 1
                outevo.append(currow);

        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Worksheets'),
                    'class':        'informative',
                    'description':  _('Evolution of Worksheets'),
                    'data':         json.dumps(outevo)})

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
        active_rs = ['sample_received',
                     'assigned',
                     'attachment_due',
                     'to_be_verified',
                     'verified']
        bac = getToolByName(self.context, "bika_analysis_catalog")
        filtering_allowed=self.context.bika_setup.getAllowDepartmentFiltering()
        cookie_dep_uid = self.request.get('filter_by_department_info', '').split(',') if filtering_allowed else ''

        query_dic = {'portal_type':"Analysis",
                 'created':self.date_range,
                 'cancellation_state':['active']}
        if filtering_allowed:
            query_dic['getDepartmentUID'] = { "query":cookie_dep_uid,"operator":"or" }
        numans = len(bac(query_dic))

        query_dic = {'portal_type':"Analysis",
                 'created':self.base_date_range,
                 'review_state':active_rs,
                 'cancellation_state':['active']}
        if filtering_allowed:
            query_dic['getDepartmentUID'] = { "query":cookie_dep_uid,"operator":"or" }
        numans += len(bac(query_dic))

        # Analyses pending
        review_state = ['sample_received',
                        'assigned',
                        'attachment_due']
        query_dic = {'portal_type':"Analysis",
                 'review_state':review_state}
        if filtering_allowed:
            query_dic['getDepartmentUID'] = { "query":cookie_dep_uid,"operator":"or" }
        ans = len(bac(query_dic))
        ratio = (float(ans)/float(numans))*100 if ans > 0 and numans > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Analyses pending")
        out.append({'type':         'simple-panel',
                    'name':         _('Analyses pending'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ans,
                    'total':        numans,
                    'legend':       _('of') + " " + str(numans) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/aggregatedanalyses'})

        # Analyses to be verified
        review_state = ['to_be_verified', ]
        query_dic = {'portal_type':"Analysis",
                 'review_state':review_state}
        if filtering_allowed:
            query_dic['getDepartmentUID'] = { "query":cookie_dep_uid,"operator":"or" }
        ans = len(bac(query_dic))
        ratio = (float(ans)/float(numans))*100 if ans > 0 and numans > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be verified")
        out.append({'type':         'simple-panel',
                    'name':         _('To be verified'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ans,
                    'total':        numans,
                    'legend':       _('of') + " " + str(numans) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/worksheets?list_review_state=to_be_verified'})

        # Chart with the evolution of WSs over a period, grouped by
        # periodicity
        workflow = getToolByName(self.context, 'portal_workflow')
        query_dic = {'portal_type':"Analysis",
                 'sort_on':"created",
                 "created":self.min_date_range}
        if filtering_allowed:
            query_dic['getDepartmentUID'] = { "query":cookie_dep_uid,"operator":"or" }
        allans = bac(query_dic)
        outevo = []
        for an in allans:
            an = an.getObject()
            state = 'other_status'
            try:
                state = workflow.getInfoFor(an, 'cancellation_state')
                if (state == 'active'):
                    state = workflow.getInfoFor(an, 'review_state')
                else:
                    state = 'inactive'
            except:
                pass

            created = self._getDateStr(self.periodicity, an.created())

            if (len(outevo) > 0 and outevo[-1]['date'] == created):
                key = state if _(state) in outevo[-1] else 'other_status'
                outevo[-1][_(key)] += 1
            else:
                currow = {'date': created,
                   _('assigned'): 0,
                   _('to_be_verified'): 0,
                   _('attachment_due'): 0,
                   _('verified'): 0,
                   _('inactive'): 0,
                   _('other_status'): 0,
                   }
                key = state if _(state) in currow else 'other_status'
                currow[_(key)] += 1
                outevo.append(currow)

        out.append({'type':         'bar-chart-panel',
                    'name':         _('Evolution of Analyses'),
                    'class':        'informative',
                    'description':  _('Evolution of Analyses'),
                    'data':         json.dumps(outevo)})
        return {'id': 'analyses',
                'title': _('Analyses'),
                'panels': out}

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
        else:
            created = '%s-%s-%s' % (str(created.year())[2:], str(created.month()).zfill(2), str(created.day()).zfill(2))
        return created
