# -*- coding: utf-8 -*-

import urllib

from zope import interface

from bika.lims.jsonapi import request as req
from bika.lims.jsonapi.interfaces import IBatch


class Batch(object):
    """Adapter for Plone 4.3 batching functionality
    """
    interface.implements(IBatch)

    def __init__(self, batch):
        self.batch = batch

    def get_batch(self):
        return self.batch

    def get_pagesize(self):
        return self.batch.pagesize

    def get_pagenumber(self):
        return self.batch.pagenumber

    def get_numpages(self):
        return self.batch.numpages

    def get_sequence_length(self):
        return self.batch.sequence_length

    def make_next_url(self):
        if not self.batch.has_next:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = self.batch.pagenumber * self.batch.pagesize
        return "%s?%s" % (request.URL, urllib.urlencode(params))

    def make_prev_url(self):
        if not self.batch.has_previous:
            return None
        request = req.get_request()
        params = request.form
        pagesize = self.batch.pagesize
        pagenumber = self.batch.pagenumber
        params["b_start"] = max(pagenumber - 2, 0) * pagesize
        return "%s?%s" % (request.URL, urllib.urlencode(params))


class Batch42(object):
    """Adapter for Plone 4.2 batching functionality
    """
    interface.implements(IBatch)

    def __init__(self, batch):
        self.batch = batch

    def get_batch(self):
        return self.batch

    def get_pagesize(self):
        return self.batch.size

    def get_pagenumber(self):
        return self.batch.pagenumber

    def get_numpages(self):
        return self.batch.numpages

    def get_sequence_length(self):
        return self.batch.sequence_length

    def make_next_url(self):
        if self.batch.next is not None:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = self.batch.numpages * self.batch.size
        return "%s?%s" % (request.URL, urllib.urlencode(params))

    def make_prev_url(self):
        if self.batch.previous is not None:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = max(self.batch.numpages - 2, 0) * self.batch.size
        return "%s?%s" % (request.URL, urllib.urlencode(params))
