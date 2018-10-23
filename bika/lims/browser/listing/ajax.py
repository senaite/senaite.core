# -*- coding: utf-8 -*-

import inspect
import json

from bika.lims import api
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.utils import t
from DateTime import DateTime
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.decorators import returns_json
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import Message
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AjaxListingView(BrowserView):
    """Mixin Class for the ajax enabled listing table
    """
    implements(IPublishTraverse)
    contents_table_template = ViewPageTemplateFile(
        "templates/contents_table.pt")

    def __init__(self, context, request):
        super(AjaxListingView, self).__init__(context, request)
        # we need the absolute view URL when we call subpaths
        self.absolute_view_url = "{}/{}".format(
            self.context.absolute_url(), self.__name__)
        self.traverse_subpath = []

    @property
    def review_states_by_id(self):
        """Returns a mapping of the review_states by id
        """
        return dict(map(lambda rs: (rs.get("id"), rs), self.review_states))

    def ajax_contents_table(self, *args, **kwargs):
        """Render the new contents table template
        """
        return self.contents_table_template()

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def handle_subpath(self, prefix="ajax_"):
        """Dispatch the path to a method prefixed by the given prefix
        """
        if len(self.traverse_subpath) < 1:
            return {}

        # check if the method exists
        func_arg = self.traverse_subpath[0]
        func_name = "{}{}".format(prefix, func_arg)
        func = getattr(self, func_name, None)
        if func is None:
            return self.fail("Invalid function", status=400)

        # Additional provided path segments after the function name are handled
        # as positional arguments
        args = self.traverse_subpath[1:]

        # check mandatory arguments
        func_sig = inspect.getargspec(func)
        # positional arguments after `self` argument
        required_args = func_sig.args[1:]

        if len(args) < len(required_args):
            return self.fail("Wrong signature, please use '{}/{}'"
                             .format(func_arg, "/".join(required_args)), 400)
        return func(*args)

    def get_json(self):
        """Extracts the JSON from the request
        """
        body = self.request.get("BODY", "{}")
        return json.loads(body)

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    def preprocess_json_data(self, thing):
        if isinstance(thing, list):
            return map(self.preprocess_json_data, thing)
        if isinstance(thing, dict):
            for k, v in thing.items():
                thing[k] = self.preprocess_json_data(v)
        if isinstance(thing, Message):
            return t(thing)
        return thing

    def to_safe_json(self, thing, default=None):
        """Returns a safe JSON string
        """
        def default(obj):
            if isinstance(obj, DateTime):
                return obj.ISO8601()
            if isinstance(obj, Message):
                return t(obj)
            if api.is_object(obj):
                return api.get_uid(obj)
            return repr(obj)

        thing = self.preprocess_json_data(thing)

        return json.dumps(thing, default=default)

    def ajax_columns(self):
        """Returns the column definition
        """
        return self.to_safe_json(self.columns)

    def ajax_review_states(self):
        """Returns the review states definition
        """
        return self.to_safe_json(self.review_states)

    def ajax_folderitems(self):
        """Returns the folderitems
        """
        payload = self.get_json()
        filter_by = payload.get("filter_by", self.default_review_state)

        # update the catalog query with the filter
        review_state_item = self.review_states_by_id.get(filter_by)
        if review_state_item:
            content_filter = review_state_item.get("contentFilter", {})
            if content_filter:
                self.contentFilter.update(content_filter)

        # bypass missing request paramerter check in `review_state` method
        self.default_review_state = filter_by

        logger.info("AjaxListingView::ajax_folderitems:contentFilter={}"
                    .format(self.contentFilter))

        return self.to_safe_json(self.folderitems())
