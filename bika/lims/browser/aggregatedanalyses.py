# coding=utf-8

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import getSecurityManager
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict, format_supsub
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView ####
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import getUsers
from bika.lims.utils import to_utf8
from bika.lims.utils import formatDecimalMark
from DateTime import DateTime
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils.analysis import format_numeric_result
from zope.interface import implements
from zope.interface import Interface
from zope.component import getAdapters

import json


class AggregatedAnalysesView(AnalysesView):
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        super(AggregatedAnalysesView, self).__init__(context,
                                           request,
                                           show_categories=False,
                                           expand_all_categories=False)
        self.title = _("Analyses pending")
        self.catalog = "bika_analysis_catalog"
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
             'title':  _('All'),
             'transitions': [{'id': 'sample'},
                             {'id': 'submit'},
                             {'id': 'cancel'},
                             {'id': 'assign'}],
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
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

    def isItemAllowed(self, obj):
        """
        It checks if the item can be added to the list depending on the
        department filter. If the analysis service is not assigned to a
        department, show it.
        @Obj: it is an analysis object.
        @return: boolean
        """
        if not obj:
            return None
        # Gettin the department from analysis service
        serv_dep = obj.getService().getDepartment()
        result = True
        if serv_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            result = True if serv_dep.UID() in\
                self.request.get('filter_by_department_info', '').split(',') else False
        return result

    def folderitem(self, obj, item, index):
        parent = obj.aq_parent
        # Analysis Request
        item['AnalysisRequest'] = parent.Title()
        anchor = '<a href="%s">%s</a>' % (parent.absolute_url(), parent.Title())
        item['replace']['AnalysisRequest'] = anchor
        # Worksheet
        item['Worksheet'] = ''
        wss = obj.getBackReferences('WorksheetAnalysis')
        if wss and len(wss) > 0:
            ws = wss[0]
            item['Worksheet'] = ws.Title()
            anchor = '<a href="%s">%s</a>' % (ws.absolute_url(), ws.Title())
            item['replace']['Worksheet'] = anchor
        return item
