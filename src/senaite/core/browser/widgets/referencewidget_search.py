# -*- coding: utf-8 -*-

import json

from bika.lims.browser import BrowserView
from bika.lims.interfaces import IReferenceWidgetVocabulary
from plone import protect
from senaite.core.interfaces import IReferenceWidgetDataProvider
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

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    def search(self):
        """Returns the list of brains that match with the request criteria
        """
        brains = []
        for name, adapter in getAdapters(
                (self.context, self.request), IReferenceWidgetVocabulary):
            brains.extend(adapter())
        return brains

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

    def __call__(self):
        protect.CheckAuthenticator(self.request)

        # Do the search
        brains = self.search()

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
