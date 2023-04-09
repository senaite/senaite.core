# -*- coding: utf-8 -*-

import json

import Missing
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IReferenceWidgetVocabulary
from plone import protect
from senaite.jsonapi import request as req
from senaite.jsonapi.api import make_batch
from zope.component import getAdapters
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

_marker = object()
MISSING_VALUES = [_marker, Missing.Value]


class IReferenceWidgetDataProvider(Interface):
    """Extract required data for the reference widget
    """


@implementer(IReferenceWidgetDataProvider)
class ReferenceWidgetDataProvider(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def get_field_name(self):
        """Return the field name
        """
        return self.request.get("field_name", None)

    def get_columns(self):
        """Return the requested columns
        """
        return self.request.get("column_names", [])

    def lookup(self, brain_or_object, name, default=None):
        """Lookup a named attribute on the brain/object
        """
        value = getattr(brain_or_object, name, _marker)

        # wake up the object
        if value is _marker:
            brain_or_object = api.get_object(brain_or_object)
            value = getattr(brain_or_object, name, _marker)

        if value in MISSING_VALUES:
            return default

        if callable(value):
            value = value()

        try:
            json.dumps(value)
            return value
        except TypeError:
            # not JSON serializable
            return default

    def get_base_info(self, brain_or_object):
        """Return the base information for the brain or object
        """
        return {
            "uid": api.get_uid(brain_or_object),
            "url": api.get_url(brain_or_object),
            "Title": self.lookup(brain_or_object, "Title", ""),
            "Description": self.lookup(brain_or_object, "Description", ""),
        }

    def to_dict(self, reference, data=None, **kw):
        """Return the required data for the given object or uid

        :param reference: Catalog Brain, AT/DX object or UID
        :param data: Dictionary of collected data
        """
        info = {}

        if isinstance(data, dict):
            info.update(data)

        # Fetch the object if an UID is passed
        if api.is_uid(reference):
            brain_or_object = api.get_object(reference)
        else:
            brain_or_object = reference

        # always include base information
        info.update(self.get_base_info(brain_or_object))

        columns = self.get_columns()

        # always include all brain metadata
        if api.is_brain(brain_or_object):
            columns.extend(brain_or_object.schema())

        for column in self.get_columns():
            if column not in info:
                info[column] = self.lookup(brain_or_object, column, default="")

        return info


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
