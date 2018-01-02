# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing_filter_bar import BikaListingFilterBar


class SamplesBikaListingFilterBar(BikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :returns: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = [{
            'name': 'sample_condition',
            'label': _('Sample condition'),
            'type': 'select',
            'voc': self.getSampleConditionsVoc(),
        }, {
            'name': 'print_state',
            'label': _('Print state'),
            'type': 'select',
            'voc': self.getPrintStatesVoc(),
        }, {
            'name': 'sample_type',
            'label': _('Sample type'),
            'type': 'select',
            'voc': self.getSampleTypesVoc(),
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
        :returns: a dictionary to be added to contentFilter.
        """
        query_dict = {}
        filter_dict = self.get_filter_bar_dict()
        # Date received filter
        query_dict = self.createQueryForDateRange(
            filter_dict, query_dict, 'date_received', 'getDateReceived')
        # Sample type filter
        if filter_dict.get('sample_type', ''):
            query_dict['getSampleTypeUID'] = filter_dict.get('sample_type', '')
        return query_dict

    # TODO-performance: Improve filter bar using catalogs
    def filter_bar_check_item(self, item):
        """
        This functions receives a key-value items, and checks if it should be
        displayed.
        It is recomended to be used in isItemAllowed() method.
        This function should be only used for those fields without
        representation as an index in the catalog.
        :item: The item to check.
        :returns: boolean.
        """
        dbar = self.get_filter_bar_dict()
        keys = dbar.keys()
        final_decision = 'True'
        for key in keys:
            if key == 'sample_condition' and dbar.get(key, '') != '':
                if not item.getSampleCondition() or\
                        dbar.get(key, '') != item.getSampleCondition().UID():
                    return False
            if key == 'print_state' and dbar.get(key, '') != '':
                status = [ar.getPrinted() for ar in item.getAnalysisRequests()]
                if dbar.get(key, '') not in status:
                    return False
        return True
