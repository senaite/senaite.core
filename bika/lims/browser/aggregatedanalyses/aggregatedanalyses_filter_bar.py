# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.sample.samples_filter_bar\
    import SamplesBikaListingFilterBar


class AggregatedanalysesBikaListingFilterBar(SamplesBikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
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
        filter_dict = self.get_filter_bar_dict()
        query_dict =\
            SamplesBikaListingFilterBar.get_filter_bar_queryaddition(self)
        # Sample condition filter
        if filter_dict.get('sample_condition', ''):
            query_dict['getSampleConditionUID'] =\
                filter_dict.get('sample_condition', '')
        # Print state filter
        if filter_dict.get('print_state', ''):
            query_dict['getAnalysisRequestPrintStatus'] =\
                filter_dict.get('print_state', '')
        return query_dict

    def filter_bar_check_item(self, item):
        return True
