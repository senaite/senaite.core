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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from archetypes.schemaextender.interfaces import ISchemaModifier, \
    IOrderableSchemaExtender
from senaite.core.browser import BrowserView
from senaite.core.interfaces import IBatch, IAnalysisRequest
from senaite.core.permissions import *
from senaite.core.vocabularies import CatalogVocabulary
from operator import itemgetter
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from senaite.core.catalog import CATALOG_ANALYSIS_REQUEST_LISTING


import json
import plone
import plone.protect


class ClientContactVocabularyFactory(CatalogVocabulary):

    """XXX This seems to be a stub, handy though, needs some simple work.
    """

    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact'
        )


class getAnalysisContainers(BrowserView):

    """ Vocabulary source for jquery combo dropdown box
    Returns AnalysisRequst and Batch objects currently
    available to be inherited into this Batch.
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        ars = []
        catalog = getToolByName(self, CATALOG_ANALYSIS_REQUEST_LISTING)
        for x in [a.getObject() for a in
                catalog(
                    is_active=True,
                    sort_on="created",
                    sort_order="desc")]:
            if searchTerm in x.Title().lower():
                ars.append(x)

        batches = []
        for x in [a.getObject() for a in
                  self.bika_catalog(
                    portal_type='Batch',
                    is_active=True,
                    sort_on="created",
                    sort_order="desc")]:
            if searchTerm in x.Title().lower() \
            or searchTerm in x.Schema()['BatchID'].get(x).lower() \
            or searchTerm in x.Schema()['ClientBatchID'].get(x).lower():
                batches.append(x)

        _rows = []
        for item in batches:
            _rows.append({
                'Title': item.Title(),
                'ObjectID': item.id,
                'Description': item.Description(),
                'UID': item.UID()
            })
            _rows = sorted(_rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                           key=itemgetter(sidx and sidx or 'Title'))

        rows += _rows

        _rows = []
        for item in ars:
            _rows.append({
                'Title': item.Title(),
                'ObjectID': item.id,
                'Description': item.Description(),
                'UID': item.UID()
            })
            _rows = sorted(_rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                           key=itemgetter(sidx and sidx or 'Title'))

        rows += _rows

        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        start = (int(page) - 1) * int(nr_rows)
        end = int(page) * int(nr_rows)
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[start:end]}

        return json.dumps(ret)
