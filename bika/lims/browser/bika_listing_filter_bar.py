# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from datetime import datetime
from datetime import date
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView


class BikaListingFilterBar(BrowserView):
    """
    Defines a filter bar to make advanced queries in BikaListingView. This
    filter doesn't override the 'filter by state' functionality
    """
    _render = ViewPageTemplateFile("templates/bika_listing_filter_bar.pt")
    _filter_bar_dict = {}

    def render(self):
        """
        Returns a ViewPageTemplateFile instance with the filter inputs and
        submit button.
        """
        return self._render()

    def setRender(self, new_template):
        """
        Defines a new template to render.
        :new_template: should be a ViewPageTemplateFile object such as
            'ViewPageTemplateFile("templates/bika_listing_filter_bar.pt")'
        """
        if new_template:
            self._render = new_template

    def filter_bar_button_title(self):
        """
        This function returns a string with the name for the input. A function
        is used in order to translate the name.
        :returns: an string with the title.
        """
        return _('Filter')

    def save_filter_bar_values(self, filter_bar_items={}):
        """
        This function saves the values to filter the bika_listing inside the
        BikaListingFilterBar object.
        The dictionary is saved inside a class attribute.
        This function tranforms the unicodes to strings and removes the
        'bika_listing_filter_bar_' starting string of each key.
        :filter_bar_items: a dictionary with the items to define the
        query.
        """
        if filter_bar_items:
            new_dict = {}
            for k in filter_bar_items.keys():
                value = str(filter_bar_items[k])
                key = str(k).replace("bika_listing_filter_bar_", "")
                new_dict[key] = value
            self._filter_bar_dict = new_dict

    def get_filter_bar_dict(self):
        """
        Returns the _filter_bar_dict attribute
        """
        return self._filter_bar_dict

    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a catalog query accordingly.
        Only returns the items that can be added to contentFilter dictionary,
        this means that only the dictionary items (key-value) with index
        representations should be returned.
        :returns: a dictionary to be added to contentFilter.
        """
        return {}

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
        return True

    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :returns: a list of dictionaries as the filtering fields or None.

        Each dictionary defines a field, those are the expected elements
        for each field type by the default template:
        - select/multiple:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'select/multiple',
                'voc': <a DisplayList object containing the options>,
            }
        - simple text input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'text',
            }
        - autocomplete text input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'autocomplete_text',
                'voc': <a List object containing the options in JSON>,
            }
        - value range input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'range',
            },
        - date range input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'date_range',
            },
        """
        return None

    def createQueryForDateRange(
            self, filter_dict, query_dict, term_name, cat_index):
        """
        If the dictionary variable 'filter_dict' contains a 'term_name',
        this function will get the date ranges from 'filter_dict' and
        will create a range query to query a catalog by getDateReceived index.
        :filter_dict: This dictionary contains the filter bar keys and values.
        :query_dict: is the final quering dictionary that will be used to
        filter the list of elements in the acatalog.
        :term_name: It is a string with the name of a filter bar's field with
        'date_range' type.
        :cat_index: It is a catalog index as string.
        """
        key_date_0 = term_name + '_0'
        Key_date_1 = term_name + '_1'
        if filter_dict.get(key_date_0, '') or\
                filter_dict.get(Key_date_1, ''):
            date_0 = filter_dict.get(key_date_0) \
                if filter_dict.get(key_date_0, '')\
                else '1900-01-01'
            date_1 = filter_dict.get(Key_date_1)\
                if filter_dict.get(Key_date_1, '')\
                else datetime.strftime(date.today(), "%Y-%m-%d")
            date_range_query = {
                'query':
                (date_0 + ' 00:00', date_1 + ' 23:59'), 'range': 'min:max'}
            query_dict[cat_index] = date_range_query
        return query_dict

    def createQueryForBatch(self, filter_dict, query_dict):
        """
        If the dictionary variable 'filter_dict' contains a 'batch'
        key, this function will get all the methods' UIDs in order to build
        a query dictionary with them.
        @filter_dict: This dictionary contains the filter bar values to filter
        by.
        @query_dict: is the final quering dictionary that will be used to
        filter the list elements.
        """
        if filter_dict.get('batch', ''):
            # removing the empty and space values and gettin their UIDs
            clean_list_ids = [
                a.strip() for a in filter_dict.get('batch', '').split(',')
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
        return query_dict

    def getSampleConditionsVoc(self):
        """
        Returns a DisplayList object with sample condtions.
        """
        cons = self.context.bika_setup.\
            bika_sampleconditions.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in cons])

    def getPrintStatesVoc(self):
        """
        Returns a DisplayList object with print states.
        """
        return DisplayList([
            ('0', _('Never printed')),
            ('1', _('Printed after last publish')),
            ('2', _('Printed but republished afterwards')),
            ])

    def getSampleTypesVoc(self):
        """
        Returns a DisplayList object with sample types.
        """
        types = self.context.bika_setup.bika_sampletypes.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in types])

    def getCasesVoc(self):
        """
        Returns a list object with active cases ids.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog({
            'portal_type': 'Batch',
            'review_state': 'open',
        })
        return [brain.id for brain in brains]

    def getAnalysesNamesVoc(self):
        """
        Returns a DisplayList object with analyses names.
        """
        ans = self.context.bika_setup.\
            bika_analysisservices.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in ans])
