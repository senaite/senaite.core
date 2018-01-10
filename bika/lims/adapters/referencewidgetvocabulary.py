# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import ast
import json

from zope.interface import implements

from Products.AdvancedQuery import Or, MatchRegexp, Generic
from Products.CMFCore.utils import getToolByName

from bika.lims.utils import to_utf8 as _c
from bika.lims.utils import to_unicode as _u
from bika.lims.interfaces import IReferenceWidgetVocabulary


class DefaultReferenceWidgetVocabulary(object):
    implements(IReferenceWidgetVocabulary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, result=None, specification=None, **kwargs):
        searchTerm = _c(self.request.get('searchTerm', '')).lower()
        force_all = self.request.get('force_all', 'false')
        searchFields = 'search_fields' in self.request \
            and json.loads(_u(self.request.get('search_fields', '[]'))) \
            or ('Title',)
        # lookup objects from ZODB
        catalog_name = _c(self.request.get('catalog_name', 'portal_catalog'))
        catalog = getToolByName(self.context, catalog_name)

        # N.B. We don't use json.loads to avoid unicode conversion, which will
        #      fail in the catalog search for some cases
        # see: https://github.com/senaite/bika.lims/issues/443
        base_query = ast.literal_eval(self.request['base_query'])
        search_query = ast.literal_eval(self.request.get('search_query', "{}"))

        # first with all queries
        contentFilter = dict((k, v) for k, v in base_query.items())
        contentFilter.update(search_query)

        # Sorted by? (by default, Title)
        sort_on = self.request.get('sidx', 'Title')
        if sort_on == 'Title':
            sort_on = 'sortable_title'
        if sort_on:
            # Check if is an index and if is sortable. Otherwise, assume the
            # sorting must be done manually
            index = catalog.Indexes.get(sort_on, None)
            if index and index.meta_type in ['FieldIndex', 'DateIndex']:
                contentFilter['sort_on'] = sort_on
                # Sort order?
                sort_order = self.request.get('sord', 'asc')
                if (sort_order in ['desc', 'reverse', 'rev', 'descending']):
                    contentFilter['sort_order'] = 'descending'
                else:
                    contentFilter['sort_order'] = 'ascending'

        # Can do a search for indexes?
        criterias = []
        fields_wo_index = []
        if searchTerm:
            for field_name in searchFields:
                index = catalog.Indexes.get(field_name, None)
                if not index:
                    fields_wo_index.append(field_name)
                    continue
                if index.meta_type in ('ZCTextIndex'):
                    if searchTerm.isspace():
                        # earchTerm != ' ' added because of
                        # https://github.com/plone/Products.CMFPlone/issues
                        # /1537
                        searchTerm = ''
                        continue
                    else:
                        temp_st = searchTerm + '*'
                        criterias.append(MatchRegexp(field_name, temp_st))
                elif index.meta_type in ('FieldIndex'):
                    criterias.append(MatchRegexp(field_name, searchTerm))
                elif index.meta_type == 'DateIndex':
                    msg = "Unhandled DateIndex search on '%s'" % field_name
                    from bika.lims import logger
                    logger.warn(msg)
                else:
                    criterias.append(Generic(field_name, searchTerm))

        if criterias:
            # Advanced search
            advanced_query = catalog.makeAdvancedQuery(contentFilter)
            aq_or = Or()
            for criteria in criterias:
                aq_or.addSubquery(criteria)
            advanced_query &= aq_or
            brains = catalog.evalAdvancedQuery(advanced_query)
        else:
            brains = catalog(contentFilter)

        if brains and searchTerm and fields_wo_index:
            _brains = []
            for brain in brains:
                for field_name in fields_wo_index:
                    value = getattr(brain, field_name, None)
                    if not value:
                        instance = brain.getObject()
                        schema = instance.Schema()
                        if field_name in schema:
                            value = schema[field_name].get(instance)
                    if callable(value):
                        value = value()
                    if value and value.lower().find(searchTerm) > -1:
                        _brains.append(brain)
                        break
            brains = _brains

        # Then just base_query alone ("show all if no match")
        if not brains and force_all.lower() == 'true':
            if search_query:
                brains = catalog(base_query)
                if brains and searchTerm:
                    _brains = [p for p in brains
                               if p.Title.lower().find(searchTerm) > -1]
                    if _brains:
                        brains = _brains

        return brains
