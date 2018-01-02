# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing_filter_bar import BikaListingFilterBar


class AnalysisRequestsBikaListingFilterBar(BikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    # TODO-performance: Improve filter bar using catalogs
    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :returns: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = [{
            'name': 'analysis_name',
            'label': _('Analysis name'),
            'type': 'select',
            'voc': self.getAnalysesNamesVoc(),
        }, {
            'name': 'print_state',
            'label': _('Print state'),
            'type': 'select',
            'voc': self.getPrintStatesVoc(),
        }, {
            'name': 'batch',
            'label': _('Batch'),
            'type': 'autocomplete_text',
            'voc': json.dumps(self.getCasesVoc()),
        }, {
            'name': 'date_received',
            'label': _('Date received'),
            'type': 'date_range',
        },
        ]
        return fields_dict

    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a query accordingly.
        Only returns the once that can be added to contentFilter dictionary.
        in this case, the catalog is bika_catalog
        In this case the keys with index representation are:
        - date_received - getDateReceived
        - date_received - BatchUID
        :returns: a dictionary to be added to contentFilter.
        """
        query_dict = {}
        filter_dict = self.get_filter_bar_dict()
        # Date received filter
        query_dict = self.createQueryForDateRange(
            filter_dict, query_dict, 'date_received', 'getDateReceived')
        # Batch filter
        query_dict = self.createQueryForBatch(filter_dict, query_dict)
        # Print state filter
        if filter_dict.get('print_state', ''):
            query_dict['getPrinted'] =\
                filter_dict.get('print_state', '')
        return query_dict

    def filter_bar_check_item(self, item):
        """
        This functions receives a key-value items, and checks if it should be
        displayed.
        It is recomended to be used in isItemAllowed() method.
        This function should be only used for those fields without
        representation as an index in the catalog.
        :item: The item to check. This is a brain
        :returns: boolean.
        """
        dbar = self.get_filter_bar_dict()
        keys = dbar.keys()
        item_obj = None
        for key in keys:
            if key == 'analysis_name' and dbar.get(key, '') != '':
                item_obj = item.getObject() if not item_obj else item_obj
                uids = [analysis.getServiceUID for analysis in
                        item_obj.getAnalyses(full_objects=False)]
                if dbar.get(key, '') not in uids:
                    return False
        return True
