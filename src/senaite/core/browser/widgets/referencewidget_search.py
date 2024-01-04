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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims.browser import BrowserView
from plone import protect
from senaite.core.interfaces.widget import IReferenceWidgetDataProvider
from senaite.core.interfaces.widget import IReferenceWidgetVocabulary
from senaite.jsonapi import request as req
from senaite.jsonapi.api import make_batch
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


# Make route provider for senaite.jsonapi
@implementer(IPublishTraverse)
class ReferenceWidgetSearch(BrowserView):
    """Search endpoint for new UID referencewidget
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def __call__(self):
        protect.CheckAuthenticator(self.request)
        return self.search()

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    def get_ref_data(self, brain):
        """Extract the data for the ference item

        :param brain: ZCatalog Brain Object
        :returns: Dictionary with extracted attributes
        """
        data = {}
        for name, adapter in getAdapters(
                (self.context, self.request), IReferenceWidgetDataProvider):
            data.update(adapter.to_dict(brain, data=dict(data)))
        return data

    def search_results(self):
        """Returns the list of brains that match with the request criteria
        """
        brains = []
        for name, adapter in getAdapters(
                (self.context, self.request), IReferenceWidgetVocabulary):
            brains.extend(adapter())
        return brains

    def search(self):
        # Do the search
        brains = self.search_results()

        size = req.get_batch_size()
        start = req.get_batch_start()
        batch = make_batch(brains, size, start)
        data = {
            "pagesize": batch.get_pagesize(),
            "next": batch.make_next_url(),
            "previous": batch.make_prev_url(),
            "page": batch.get_pagenumber(),
            "pages": batch.get_numpages(),
            "count": batch.get_sequence_length(),
            "items": map(self.get_ref_data, batch.get_batch()),
        }
        return json.dumps(data)
