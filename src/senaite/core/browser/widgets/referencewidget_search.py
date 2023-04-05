# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IReferenceWidgetVocabulary
from plone import protect
from senaite.app.supermodel import SuperModel
from senaite.jsonapi import request as req
from senaite.jsonapi.api import make_batch
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

DEFAULT_COLUMNS = ["Title", "Description"]


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

        for name, adapter in getAdapters((self.context, self.request),
                                         IReferenceWidgetVocabulary):
            brains.extend(adapter())
        return brains

    def get_info(self, brain):
        """Extract the data for the result items
        """
        model = SuperModel(brain)
        info = model.to_dict()
        column_names = self.request.form.get("column_names", DEFAULT_COLUMNS)
        for column in column_names:
            if column not in info:
                value = getattr(model.instance, column, None)
                if callable(value):
                    value = value()
                if api.is_string(value):
                    info[column] = value
        return info

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
            "items": map(self.get_info, batch.get_batch()),
        }
        return json.dumps(data)
