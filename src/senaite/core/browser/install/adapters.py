# -*- coding: utf-8 -*-

from zope.component import queryMultiAdapter
from zope.interface import Interface
from ZPublisher.BaseRequest import DefaultPublishTraverse


class SenaiteAppTraverser(DefaultPublishTraverse):
    def publishTraverse(self, request, name):
        if name == "index_html":
            view = queryMultiAdapter(
                (self.context, request),
                Interface, "senaite-overview")
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)
