# -*- coding: utf-8 -*-

import collections

import six
from bika.lims import api
from Products.Five.browser import BrowserView


class Modal(BrowserView):
    """Base Class for Modals
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.uids = self.get_uids_from_request()

    def get_uids_from_request(self):
        """Returns a list of uids from the request
        """
        uids = self.request.get("uids", "")
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)
