# coding=utf-8

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.permissions import *
from bika.lims.browser.bika_listing import BikaListingFilterBar\
    as BaseBikaListingFilterBar
from Products.Archetypes.public import DisplayList
import json
from datetime import datetime, date
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


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
        # Check if the filter bar functionality is activated or not
        self.filter_bar_enabled =\
            self.context.bika_setup.getSamplingBarEnabledAnalyses()

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
        if self.filter_bar_enabled and not self.filter_bar_check_item(obj):
            return False
        serv_dep = obj.getService().getDepartment()
        result = True
        if serv_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            result = True if serv_dep.UID() in\
                cookie_dep_uid.split(',') else False
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

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :return: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            BikaListingFilterBar(context=self.context, request=self.request)
        return self._advfilterbar


class BikaListingFilterBar(BaseBikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    # TODO-performance: Improve filter bar using catalogs
    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a query accordingly.
        Only returns the once that can be added to contentFilter dictionary.
        in this case, the catalog is bika_catalog
        In this case the keys with index representation are:
        - date_received - getDateReceived
        - date_received - BatchUID
        :return: a dictionary to be added to contentFilter.
        """
        query_dict = {}
        filter_dict = self.get_filter_bar_dict()
        # Date received filter
        if filter_dict.get('date_received_0', '') or\
                filter_dict.get('date_received_1', ''):
            date_0 = filter_dict.get('date_received_0') \
                if filter_dict.get('date_received_0', '')\
                else '1900-01-01'
            date_1 = filter_dict.get('date_received_1')\
                if filter_dict.get('date_received_1', '')\
                else datetime.strftime(date.today(), "%Y-%m-%d")
            date_range_query = {
                'query':
                (date_0 + ' 00:00', date_1 + ' 23:59'), 'range': 'min:max'}
            query_dict['getDateReceived'] = date_range_query
        # Batch(case) filter
        if filter_dict.get('case', ''):
            # removing the empty and space values and gettin their UIDs
            clean_list_ids = [
                a.strip() for a in filter_dict.get('case', '').split(',')
                if a.strip()]
            # Now we have the case(batch) ids, lets get their UIDs
            catalog = getToolByName(self, 'bika_catalog')
            brains = catalog(
                portal_type='Batch',
                cancellation_state='active',
                review_state='open',
                id=clean_list_ids
                )
            query_dict['getBatchUID'] = [a.UID for a in brains]
        # sample type filter
        if filter_dict.get('sample_type', ''):
            query_dict['getSampleTypeUID'] = filter_dict.get('sample_type', '')
        # Sample condition filter
        if filter_dict.get('sample_condition', ''):
            query_dict['getSampleConditionUID'] =\
                filter_dict.get('sample_condition', '')
        # Print state filter
        if filter_dict.get('print_state', ''):
            query_dict['getAnalysisRequestPrintStatus'] =\
                filter_dict.get('print_state', '')
        return query_dict

    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :return: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = [{
            'name': 'sample_condition',
            'label': _('Sample condition'),
            'type': 'select',
            'voc': self._getSampleConditionsVoc(),
        }, {
            'name': 'print_state',
            'label': _('Print state'),
            'type': 'select',
            'voc': self._getPrintStatesVoc(),
        }, {
            'name': 'sample_type',
            'label': _('Sample type'),
            'type': 'select',
            'voc': self._getSampleTypesVoc(),
        }, {
            'name': 'case',
            'label': _('Cases'),
            'type': 'autocomplete_text',
            'voc': json.dumps(self._getCasesVoc()),
        }, {
            'name': 'date_received',
            'label': _('Date received'),
            'type': 'date_range',
        },
        ]
        return fields_dict

    def _getSampleConditionsVoc(self):
        """
        Returns a DisplayList object with sample condtions.
        """
        cons = self.context.bika_setup.\
            bika_sampleconditions.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in cons])

    def _getPrintStatesVoc(self):
        """
        Returns a DisplayList object with print states.
        """
        return DisplayList([
            ('0', _('Never printed')),
            ('1', _('Printed after last publish')),
            ('2', _('Printed but republished afterwards')),
            ])

    def _getSampleTypesVoc(self):
        """
        Returns a DisplayList object with sample types.
        """
        types = self.context.bika_setup.bika_sampletypes.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in types])

    def _getCasesVoc(self):
        """
        Returns a list object with active cases ids.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog({
            'portal_type': 'Batch',
            'review_state': 'open',
        })
        return [brain.id for brain in brains]
