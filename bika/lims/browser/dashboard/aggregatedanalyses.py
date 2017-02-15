# coding=utf-8

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING


class AggregatedAnalysesView(AnalysesView):
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to CATALOG_ANALYSIS_LISTING.
    """

    def __init__(self, context, request, **kwargs):
        super(AggregatedAnalysesView, self).__init__(context,
                                           request,
                                           show_categories=False,
                                           expand_all_categories=False)
        self.title = _("Analyses pending")
        self.catalog = CATALOG_ANALYSIS_LISTING
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.contentFilter['sort_on'] = 'created'
        self.sort_order = 'ascending'
        self.contentFilter['sort_order'] = self.sort_order
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.show_select_all_checkbox = False
        self.show_categories = False
        self.pagesize = 50
        self.form_id = 'analyses_form'
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()
        # Get temp objects that are too time consuming to obtain every time
        self.bika_catalog = getToolByName(context, 'bika_catalog')

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = True

        self.columns['AnalysisRequest'] = {
            'title': _('Analysis Request'),
            'sortable': False
            }
        self.columns['Worksheet'] = {
            'title': _('Worksheet'),
            'sortable': False
            }
        self.review_states = [
            {'id': 'default',
             'title':  _('Results pending'),
             'transitions': [{'id': 'sample'},
                             {'id': 'submit'},
                             {'id': 'cancel'},
                             # {'id': 'assign'}
                             ],
             'contentFilter': {'review_state': [
                'sample_received', 'assigned', 'attachment_due']},
             'columns': ['AnalysisRequest',
                         'Worksheet',
                         'Service',
                         'Result',
                         'Uncertainty',
                         'Partition',
                         'Method',
                         'Instrument',
                         'Analyst',
                         'state_title',
                         ]
             },
             {'id': 'to_be_verified',
              'title':  _('To be verified'),
              'transitions': [{'id': 'verify'},
                              {'id': 'cancel'}
                              ],
              'contentFilter': {'review_state': [
                 'to_be_verified']},
              'columns': ['AnalysisRequest',
                          'Worksheet',
                          'Service',
                          'Result',
                          'Uncertainty',
                          'Partition',
                          'Method',
                          'Instrument',
                          'Analyst',
                          'state_title',
                          ]
              },
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

    def getPOSTAction(self):
        return 'aggregatedanalyses_workflow_action'

    def isItemAllowed(self, obj):
        """
        It checks if the item can be added to the list depending on the
        department filter. If the analysis service is not assigned to a
        department, show it.
        If department filtering is disabled in bika_setup, will return True.
        @Obj: it is an analysis object.
        @return: boolean
        """
        if not obj:
            return None
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Gettin the department from analysis service
        serv_dep = obj.getDepartmentUID
        result = True
        if serv_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            result = True if serv_dep in\
                cookie_dep_uid.split(',') else False
        return result

    def folderitem(self, obj, item, index):
        # Analysis Request
        item['AnalysisRequest'] = obj.getAnalysisRequestTitle
        anchor = \
            '<a href="%s">%s</a>' % \
            (obj.getAnalysisRequestURL, obj.getAnalysisRequestTitle)
        item['replace']['AnalysisRequest'] = anchor
        # Worksheet
        item['Worksheet'] = ''
        wss = self.bika_catalog(getAnalysesUIDs={
                    "query": obj.UID,
                    "operator": "or"
                })
        if wss and len(wss) > 0:
            # TODO-performance: don't get the whole object
            ws = wss[0].getObject()
            item['Worksheet'] = ws.Title()
            anchor = '<a href="%s">%s</a>' % (ws.absolute_url(), ws.Title())
            item['replace']['Worksheet'] = anchor
        return item
