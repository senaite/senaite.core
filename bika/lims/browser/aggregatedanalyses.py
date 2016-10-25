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
from bika.lims.browser.bika_listing import BikaListingView
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


class AggregatedAnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        self.catalog = "bika_analysis_catalog"
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.contentFilter['sort_on'] = 'created'
        self.sort_order = 'reverse'
        self.contentFilter['sort_order'] = self.sort_order
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 50
        self.form_id = 'analyses_form'

        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

        request.set('disable_plone.rightcolumn', 1)

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = {
            'AnalysisRequest': {
                'title': _('AnalysisRequest'),
                'sortable': False
            },
            'Worksheet': {
                'title': _('Worksheet'),
                'sortable': False
            },
            'Service': {
                'title': _('Analysis'),
                'sortable': False
            },
            'Partition': {
                'title': _("Partition"),
                'sortable':False
            },
        }

        self.review_states = [
            {'id': 'default',
             'title':  _('All'),
             'contentFilter': {},
             'columns': ['AnalysisRequest',
                         'Worksheet',
                         'Service',
                         'Partition',
                         ]
             },
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

        super(AggregatedAnalysesView, self).__init__(context,
                                           request,
                                           show_categories=False,
                                           expand_all_categories=True)

    def folderitem(self, obj, item, index):
        if not obj:
            return None

        item = super(AggregatedAnalysesView, self).folderitem(obj, item, index)
        if not item:
            return None

        parent = obj.aq_parent
        if (parent.portal_type != 'AnalysisRequest'):
            # Parent is not an AnalysisRequest, probably this object is a
            # QC analysis, so do nothing
            return None

        item['AnalysisRequest'] = parent.Title()
        anchor = '<a href="%s">%s</a>' % (parent.absolute_url(), parent.Title())
        item['replace']['AnalysisRequest'] = anchor
        item['Worksheet'] = ''
        wss = obj.getBackReferences('WorksheetAnalysis')
        if wss and len(wss) > 0:
            ws = wss[0]
            item['Worksheet'] = ws.Title()
            anchor = '<a href="%s">%s</a>' % (ws.absolute_url(), ws.Title())
            item['replace']['Worksheet'] = anchor

        serv = obj.getService()
        item['Service'] = serv.Title()
        anchor = '<a href="%s">%s</a>' % (serv.absolute_url(), serv.Title())
        item['replace']['Service'] = anchor

        try:
            item['Partition'] = obj.getSamplePartition().getId()
        except AttributeError:
            items['Partition'] = ''
        return item
