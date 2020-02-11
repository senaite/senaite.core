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

import re
from operator import itemgetter

from AccessControl import getSecurityManager

from Products.CMFPlone import PloneMessageFactory
from Products.CMFCore.permissions import ModifyPortalContent

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import EditResults
from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import ManageAnalysisRequests


class BatchBookView(BikaListingView):

    def __init__(self, context, request):
        super(BatchBookView, self).__init__(context, request)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/batchbook_big.png"
        self.context_actions = {}
        self.contentFilter = {"sort_on": "created"}
        self.title = context.Title()
        self.Description = context.Description()
        self.show_select_all_checkbox = True

        self.show_column_toggles = True
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 999999
        self.form_id = "list"
        self.page_start_index = 0
        self.show_categories = True
        self.expand_all_categories = True

        self.insert_submit_button = False

        request.set('disable_plone.rightcolumn', 1)

        self.columns = {
            'AnalysisRequest': {
                'title': _('Sample'),
                'index': 'id',
                'sortable': True,
            },

            'SampleType': {
                'title': _('Sample Type'),
                'sortable': True,
            },
            'SamplePoint': {
                'title': _('Sample Point'),
                'sortable': True,
            },
            'ClientOrderNumber': {
                'title': _('Client Order Number'),
                'sortable': True,
            },
            'created': {
                'title': PloneMessageFactory('Date Created'),
                'index': 'created',
                'toggle': False,
            },
            'state_title': {
                'title': _('State'),
                'index': 'review_state'
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['AnalysisRequest',
                         'ClientOrderNumber',
                         'SampleType',
                         'SamplePoint',
                         'created',
                         'state_title'],
             },
        ]

    @property
    def copy_to_new_allowed(self):
        mtool = api.get_tool('portal_membership')
        if mtool.checkPermission(ManageAnalysisRequests, self.context) \
                or mtool.checkPermission(ModifyPortalContent, self.context) \
                or mtool.checkPermission(AddAnalysisRequest, self.portal):
            return True
        return False

    def __call__(self):
        # Allow "Modify portal content" to see edit widgets
        mtool = api.get_tool('portal_membership')
        self.allow_edit = mtool.checkPermission("Modify portal content", self.context)
        # Allow certain users to duplicate ARs (Copy to new).
        if self.copy_to_new_allowed:
            review_states = []
            for review_state in self.review_states:
                custom_transitions = review_state.get('custom_transitions', [])
                custom_transitions.extend(
                    [{'id': 'copy_to_new',
                      'title': _('Copy to new'),
                      'url': 'workflow_action?action=copy_to_new'},
                     ])
                review_state['custom_transitions'] = custom_transitions
                review_states.append(review_state)
            self.review_states = review_states
        return super(BatchBookView, self).__call__()

    def folderitems(self):
        """Accumulate a list of all AnalysisRequest objects contained in
        this Batch, as well as those which are inherited.
        """
        wf = api.get_tool('portal_workflow')
        schema = self.context.Schema()

        ars = self.context.getAnalysisRequests(is_active=True)

        self.categories = []
        analyses = {}
        items = []
        distinct = []  # distinct analyses (each one a different service)
        keywords = []
        for ar in ars:
            analyses[ar.id] = []
            for analysis in ar.getAnalyses(full_objects=True):
                analyses[ar.id].append(analysis)
                if analysis.getKeyword() not in keywords:
                    # we use a keyword check, because versioned services are !=.
                    keywords.append(analysis.getKeyword())
                    distinct.append(analysis)

            batchlink = ""
            batch = ar.getBatch()
            if batch:
                batchlink = "<a href='%s'>%s</a>" % (
                    batch.absolute_url(), batch.Title())

            arlink = "<a href='%s'>%s</a>" % (
                ar.absolute_url(), ar.Title())

            subgroup = ar.Schema()['SubGroup'].get(ar)
            sub_title = subgroup.Title() if subgroup else 'No Subgroup'
            sub_sort = subgroup.getSortKey() if subgroup else '1'
            sub_class = re.sub(r"[^A-Za-z\w\d\-\_]", '', sub_title)

            if [sub_sort, sub_title] not in self.categories:
                self.categories.append([sub_sort, sub_title])

            review_state = wf.getInfoFor(ar, 'review_state')
            state_title = wf.getTitleForStateOnType(
                review_state, 'AnalysisRequest')

            item = {
                'obj': ar,
                'id': ar.id,
                'uid': ar.UID(),
                'category': sub_title,
                'title': ar.Title(),
                'type_class': 'contenttype-AnalysisRequest',
                'url': ar.absolute_url(),
                'relative_url': ar.absolute_url(),
                'view_url': ar.absolute_url(),
                'created': self.ulocalized_time(ar.created(), long_format=1),
                'sort_key': ar.created(),
                'replace': {
                    'Batch': batchlink,
                    'AnalysisRequest': arlink,
                },
                'before': {},
                'after': {},
                'choices': {},
                'class': {'Batch': 'Title'},
                'state_class': 'state-active subgroup_{0}'.format(sub_class) if sub_class else 'state-active',
                'allow_edit': [],
                'Batch': '',
                'SamplePoint': ar.getSamplePoint().Title() if ar.getSamplePoint() else '',
                'SampleType': ar.getSampleType().Title() if ar.getSampleType() else '',
                'ClientOrderNumber': ar.getClientOrderNumber(),
                'AnalysisRequest': '',
                'state_title': state_title,
            }
            items.append(item)

        unitstr = '<em class="discreet" style="white-space:nowrap;">%s</em>'
        checkPermission = getSecurityManager().checkPermission

        # Insert columns for analyses
        for d_a in distinct:
            keyword = d_a.getKeyword()
            short = d_a.getShortTitle()
            title = d_a.Title()
            self.columns[keyword] = {
                'title':  short if short else title,
                'sortable': True
            }
            self.review_states[0]['columns'].insert(
                len(self.review_states[0]['columns']) - 1, keyword)

            # Insert values for analyses
            for i, item in enumerate(items):
                for analysis in analyses[item['id']]:
                    if keyword not in items[i]:
                        items[i][keyword] = ''
                    if analysis.getKeyword() != keyword:
                        continue

                    edit = checkPermission(EditResults, analysis)
                    calculation = analysis.getCalculation()
                    if self.allow_edit and edit and not calculation:
                        items[i]['allow_edit'].append(keyword)
                        if not self.insert_submit_button:
                            self.insert_submit_button = True

                    value = analysis.getResult()
                    items[i][keyword] = value
                    items[i]['class'][keyword] = ''

                    if value or (edit and not calculation):

                        unit = unitstr % d_a.getUnit()
                        items[i]['after'][keyword] = unit

                if keyword not in items[i]['class']:
                    items[i]['class'][keyword] = 'empty'
        if self.insert_submit_button:
            transitions = self.review_states[0].get('custom_transitions', [])
            transitions.append({
                'id': 'submit',
                'title': _('Submit')
            })
            self.review_states[0]['custom_transitions'] = transitions

        self.categories.sort()
        self.categories = [x[1] for x in self.categories]

        items = sorted(items, key=itemgetter("sort_key"))

        return items
