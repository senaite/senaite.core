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
                obj = obj.ISO8601()
            # Convert objects and brains to UIDs
            if api.is_object(obj):
                obj = api.get_uid(obj)
            if isinstance(obj, basestring):
                return obj
            return str(obj)

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
        url = self.context.absolute_url()
        view_name = self.__name__
        return "{}/{}".format(url, view_name)

    def get_allowed_transitions_for(self, objects):
        """Retrieves all transitions from the given objects and calculate the
        ones which have all in common (intersection).
        """

        # Handle empty list of objects
        if not objects:
            return []

        # allowed transitions
        transitions = []

        # allowed transitions of the current workflow
        allowed_transitions = self.review_state.get("transitions", [])
        allowed_transition_ids = map(
            lambda t: t.get("id"), allowed_transitions)

        # internal mapping of transition id -> transition
        transitions_by_tid = {}

        # get the custom transitions of the current review_state
        custom_transitions = self.review_state.get("custom_transitions", [])

        # N.B. we use set() here to handle dupes in the views gracefully
        custom_tids = set()
        for transition in custom_transitions:
            tid = transition.get("id")
            custom_tids.add(tid)
            transitions_by_tid[tid] = transition

        # transition ids all objects have in common
        common_tids = None

        for obj in objects:
            # get the allowed transitions for this object
            obj_transitions = api.get_transitions_for(obj)
            tids = []
            for transition in obj_transitions:
                tid = transition.get("id")
                if tid not in allowed_transition_ids:
                    continue
                tids.append(tid)
                transitions_by_tid[tid] = transition

            if common_tids is None:
                common_tids = set(tids)

            common_tids = common_tids.intersection(tids)

        # union the common and custom transitions
        all_transition_ids = common_tids.union(custom_tids)

        def sort_transitions(a, b):
            transition_weights = {
                "invalidate": 100,
                "retract": 90,
                "cancel": 80,
                "deactivate": 70,
                "assign": 30,
                "receive": 20,
                "submit": 10,
            }
            w1 = transition_weights.get(a, 0)
            w2 = transition_weights.get(b, 0)
            return cmp(w1, w2)

        for tid in sorted(all_transition_ids, cmp=sort_transitions):
            transition = transitions_by_tid.get(tid)
            transitions.append(transition)

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

    def base_info(self, brain_or_object):
        """Object/Brain Base info
        """
        info = {
            "id": api.get_id(brain_or_object),
            "uid": api.get_uid(brain_or_object),
            "url": api.get_url(brain_or_object),
            "title": api.get_title(brain_or_object),
            "portal_type": api.get_portal_type(brain_or_object),
        }
        return info

    def get_category_uid(self, brain_or_object, accessor="getCategoryUID"):
        """Get the category UID from the brain or object

        This will be used to speed up the listing by categories
        """
        attr = getattr(brain_or_object, accessor, None)
        if attr is None:
            return ""
        if callable(attr):
            return attr()
        return attr

    def get_folderitems(self):
        """This method calls the folderitems method

        For performance reasons this method should do the following:

        1. Check if categories are requested
        2. Extract the category data from the brains
        3. Return the minimum brain information if categories are requested
        """
        # workaround for `pagesize` handling in BikaListing
        pagesize = self.get_pagesize()
        self.pagesize = pagesize

        # get the folderitems
        self.update()
        self.before_render()

        return self.folderitems()

    def get_selected_uids(self, folderitems, uids_to_keep=None):
        """Lookup selected UIDs from the folderitems
        """
        selected_uids = []
        if uids_to_keep:
            selected_uids = uids_to_keep

        for folderitem in folderitems:
            uid = folderitem.get("uid")
            if uid in selected_uids:
                continue
            if folderitem.get("selected", False):
                selected_uids.append(folderitem.get("uid"))
        return selected_uids

    def get_listing_config(self):
        """Get the configuration settings of the current listing view
        """

        config = {
            # N.B.: form_id, review_states and columns are passed in as data
            #       attributes and therefore not needed here.
            # "form_id": self.form_id,
            # "review_states": self.review_states,
            # "columns": self.columns,
            "allow_edit": self.allow_edit,
            "api_url": self.get_api_url(),
            "catalog": self.catalog,
            "catalog_indexes": self.get_catalog_indexes(),
            "categories": self.categories,
            "expand_all_categories": self.expand_all_categories,
            "limit_from": self.limit_from,
            "pagesize": self.pagesize,
            "post_action": self.getPOSTAction(),
            "review_state": self.review_state.get("id", "default"),
            "select_checkbox_name": self.select_checkbox_name,
            "show_categories": self.show_categories,
            "show_column_toggles": self.show_column_toggles,
            "show_more": self.show_more,
            "show_select_all_checkbox": self.show_select_all_checkbox,
            "show_select_column": self.show_select_column,
            "show_table_footer": self.show_table_footer,
            "show_workflow_action_buttons": self.show_workflow_action_buttons,
            "sort_on": self.get_sort_on(),
            "sort_order": self.get_sort_order(),
        }

        return config

    def ajax_folderitems(self):
        """Calls the `folderitems` method of the view and returns it as JSON

        1. Extract the HTTP POST payload from the request
        2. Convert the payload to HTTP form data and inject it to the request
        3. Call the `folderitems` method
        4. Prepare a data structure for the ReactJS listing app
        """

        # take the start time
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

        # generate a query string from the form data
        query_string = urllib.urlencode(form_data)

        # get the folder items
        folderitems = self.get_folderitems()

        # Process selected UIDs and their allowed transitions
        uids_to_keep = payload.get("selected_uids")
        selected_uids = self.get_selected_uids(folderitems, uids_to_keep)
        selected_objs = map(api.get_object_by_uid, selected_uids)
        transitions = self.get_allowed_transitions_for(selected_objs)

        # get the view config
        config = self.get_listing_config()

        # take the end time
        end = time()

        # calculate the total runtime
        runtime = end - start

        # prepare the response object
        data = {
            "_runtime": runtime,
            "count": len(folderitems),
            "folderitems": folderitems,
            "query_string": query_string,
            "selected_uids": selected_uids,
            "total": self.total,
            "transitions": transitions,
        }

        # update the config
        data.update(config)

        # XXX fix broken `sort_on` lookup in BikaListing
        sort_on = payload.get("sort_on")
        if sort_on in self.get_catalog_indexes():
            data["sort_on"] = sort_on

        # some performance logging
        logger.info("AjaxListingView::ajax_folderitems:"
                    "Loaded {} folderitems in {:.2f}s".format(
                        len(folderitems), runtime))

        # set the json content type header
        # Note: This is not really needed for the ReactJS App, but more correct
        #       and to show the results nicely in the browser
        self.set_content_type_header()

        return self.to_safe_json(data)
