# -*- coding: utf-8 -*-

import inspect
import json
import urllib
from time import time

from bika.lims import api
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.utils import t
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import Message
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AjaxListingView(BrowserView):
    """Mixin Class for the ajax enabled listing table

    The main purpose of this class is to provide a JSON API endpoint for the
    ReactJS based listing table.
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

    def set_content_type_header(self, content_type="application/json"):
        """Set the content-type response header
        """
        self.request.response.setHeader("content-type", content_type)

    @property
    def review_states_by_id(self):
        """Returns a mapping of the review_states by id
        """
        return dict(map(lambda rs: (rs.get("id"), rs), self.review_states))

    def ajax_contents_table(self, *args, **kwargs):
        """Render the ReactJS enabled contents table template

        It is called from the `BikaListingView.contents_table` method
        """
        return self.contents_table_template()

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    def handle_subpath(self, prefix="ajax_"):
        """Dispatch the subpath to a method prefixed with the given prefix

        N.B. Only the first subpath element will be dispatched to a method and
             the rest will be passed as arguments to this method
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

    def get_json(self, encoding="utf8"):
        """Extracts the JSON from the request
        """
        body = self.request.get("BODY", "{}")

        def encode_hook(pairs):
            """This hook is called for dicitionaries on JSON deserialization

            It is used to encode unicode strings with the given encoding,
            because ZCatalogs have sometimes issues with unicode queries.
            """
            new_pairs = []
            for key, value in pairs.iteritems():
                # Encode the key
                if isinstance(key, unicode):
                    key = key.encode(encoding)
                # Encode the value
                if isinstance(value, unicode):
                    value = value.encode(encoding)
                new_pairs.append((key, value))
            return dict(new_pairs)

        return json.loads(body, object_hook=encode_hook)

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    def translate_data(self, thing):
        """Translate i18n `Message` objects in data structures

        N.B. This is needed because only page templates translate i18n Message
             objects directly on rendering, but not when they are used in a JS
             application.
        """
        # Deconstruct lists
        if isinstance(thing, list):
            return map(self.translate_data, thing)
        # Deconstruct dictionaries
        if isinstance(thing, dict):
            for key, value in thing.items():
                thing[key] = self.translate_data(value)
        # Translate i18n Message strings
        if isinstance(thing, Message):
            return t(thing)
        return thing

    def to_safe_json(self, thing, default=None):
        """Returns a safe JSON string
        """
        def default(obj):
            """This function handles unhashable objects
            """
            # Convert `DateTime` objects to ISO8601 format
            if isinstance(obj, DateTime):
                return obj.ISO8601()
            # Convert objects and brains to UIDs
            if api.is_object(obj):
                return api.get_uid(obj)
            return repr(obj)

        # translate all i18n Message objects
        thing = self.translate_data(thing)

        return json.dumps(thing, default=default)

    def ajax_columns(self):
        """Returns the `column` dictionary of the view
        """
        return self.to_safe_json(self.columns)

    def ajax_review_states(self):
        """Returns the `review_states` list of the view
        """
        return self.to_safe_json(self.review_states)

    def to_form_data(self, data):
        """Prefix all data keys with `self.form_id`

        This is needed to inject the POST Body to the request form data, so
        that the `BikaListingView.folderitems` finds them.
        """
        out = {}
        for key, value in data.iteritems():
            if not key.startswith(self.form_id):
                k = "{}_{}".format(self.form_id, key)
            out[k] = value
        return out

    def get_api_url(self):
        """Calculate the API URL of this view
        """
        view_name = self.__name__
        url = self.context.absolute_url()
        return "{}/{}".format(url, view_name)

    def get_allowed_transitions_for(self, objects):
        """Retrieves all transitions from the given objects and calculate the
        ones which have all in common (intersection).
        """
        transitions = []

        # get the custom transitions of the current review_state
        custom_transitions = self.review_state.get("custom_transitions", [])

        transitions_by_tid = {}
        common_tids = None
        for obj in objects:
            obj_transitions = api.get_transitions_for(obj)
            tids = []
            for transition in obj_transitions:
                tid = transition.get("id")
                tids.append(tid)
                transitions_by_tid[tid] = transition
            if common_tids is None:
                common_tids = set(tids)
            common_tids = common_tids.intersection(tids)

        common_transitions = map(
            lambda tid: transitions_by_tid[tid], common_tids)
        transitions = custom_transitions + common_transitions

        return transitions

    def ajax_transitions(self):
        """Returns a list of possible transitions
        """
        start = time()
        # Get the HTTP POST JSON Payload
        payload = self.get_json()
        # Get the selected UIDs
        uids = payload.get("uids", [])
        objs = map(api.get_object_by_uid, uids)
        transitions = self.get_allowed_transitions_for(objs)
        end = time()

        # calculate the runtime
        _runtime = end - start

        logger.info("AjaxListingView::ajax_transitions:"
                    "Loaded transitions for {} UIDs in {:.2f}s".format(
                        len(uids), _runtime))

        data = {
            "transitions": transitions,
        }

        return self.to_safe_json(data)

    def ajax_folderitems(self):
        """Calls the `folderitems` method of the view and returns it as JSON

        1. Extract the HTTP POST payload from the request
        2. Convert the payload to HTTP form data and inject it to the request
        3. Call the `folderitems` method
        4. Prepare a data structure for the ReactJS listing app
        """
        start = time()

        # Get the HTTP POST JSON Payload
        payload = self.get_json()

        # Fake a HTTP GET request with parameters, so that the `bika_listing`
        # view handles them correctly.
        form_data = self.to_form_data(payload)

        # this serves `request.form.get` calls
        self.request.form.update(form_data)

        # this serves `request.get` calls
        self.request.other.update(form_data)

        api_url = self.get_api_url()
        catalog = self.catalog
        form_id = self.form_id
        sort_on = self.get_sort_on()
        sort_order = self.get_sort_order()
        review_state_item = self.review_state
        review_state = review_state_item.get("id", "default")
        review_states = self.review_states
        show_select_column = self.show_select_column
        show_select_all_checkbox = self.show_select_all_checkbox
        show_column_toggles = self.show_column_toggles
        allow_edit = self.allow_edit
        show_table_footer = self.show_table_footer

        # workaround for `pagesize` handling
        pagesize = self.get_pagesize()
        self.pagesize = pagesize

        # get the folderitems
        folderitems = self.folderitems()

        # get the number of the total results
        total = self.total
        # get the count of the current results
        count = len(folderitems)

        end = time()

        # calculate the runtime
        _runtime = end - start

        data = {
            "_runtime": _runtime,
            "api_url": api_url,
            "catalog": catalog,
            "count": count,
            "folderitems": folderitems,
            "form_id": form_id,
            "pagesize": pagesize,
            "review_state": review_state,
            "review_states": review_states,
            "review_state_item": review_state_item,
            "sort_on": sort_on,
            "sort_order": sort_order,
            "total": total,
            "url_query": urllib.urlencode(form_data),
            "show_select_column": show_select_column,
            "show_select_all_checkbox": show_select_all_checkbox,
            "show_column_toggles": show_column_toggles,
            "allow_edit": allow_edit,
            "show_table_footer": show_table_footer,
        }

        # some performance logging
        logger.info("AjaxListingView::ajax_folderitems:"
                    "Loaded {} folderitems in {:.2f}s".format(
                        len(folderitems), _runtime))

        self.set_content_type_header()
        return self.to_safe_json(data)
