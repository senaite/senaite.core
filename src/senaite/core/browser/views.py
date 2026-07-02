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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import inspect
import json

from bika.lims.decorators import returns_json
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PublishTraverseView(BrowserView):
    """Base browser view that dispatches traversal subpaths to methods.

    A request to `<context>/@@view/foo/bar` traverses to this view and
    dispatches to the `ajax_foo` method, passing the remaining subpath
    segments (`bar`) as positional arguments. When no subpath is traversed,
    `render` is called instead.

    Subclasses expose their endpoints as `ajax_<name>` methods and typically
    decorate them with `bika.lims.decorators.returns_json`::

        class MyView(PublishTraverseView):
            @returns_json
            def ajax_hello(self, name):
                return {"hello": name}

    reachable at `@@my_view/hello/world`.

    Access control: this view enforces no permission on its own. Access to the
    view (and therefore to every subpath endpoint) is gated by the `permission`
    of its `<browser:page>` registration. Register it with a permission that
    Anonymous does not hold (a role-based one) to prevent anonymous calls;
    `zope2.View` is not enough, as Anonymous usually holds View. Use the
    `require_permission` decorator for finer, per-endpoint checks.
    """

    def __init__(self, context, request):
        super(PublishTraverseView, self).__init__(context, request)
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """Collect the traversed path segments for `__call__` to dispatch
        """
        self.traverse_subpath.append(name)
        return self

    def __call__(self):
        """Dispatch the traversed subpath, or render when there is none
        """
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()
        return self.render()

    def render(self):
        """Render the view when no subpath was traversed.

        Subclasses that also serve a page should override this, e.g. to return
        a page template. The default treats a bare call as not found.
        """
        return self.handle_not_found()

    def handle_subpath(self):
        """Dispatch the first subpath segment to an `ajax_<name>` method.

        The remaining subpath segments are passed as positional arguments to
        the method. Returns `handle_not_found` when no matching method exists
        or when not enough arguments were provided.
        """
        name = self.traverse_subpath[0]
        func = getattr(self, "ajax_{}".format(name), None)
        if func is None:
            return self.handle_not_found()
        # The remaining subpath segments become positional arguments
        args = self.traverse_subpath[1:]
        required = inspect.getargspec(func).args[1:]
        if len(args) < len(required):
            return self.handle_not_found()
        return func(*args)

    def handle_not_found(self):
        """Called when the subpath cannot be dispatched. Raises a 404 by
        default; JSON views return a JSON body instead (see `JSONView`).
        """
        raise NotFound(self.request.get("ACTUAL_URL", ""))

    def get_json(self):
        """Return the JSON body of the request as a dict (empty on failure)
        """
        body = self.request.get("BODY", "") or "{}"
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            return {}

    def error(self, message, status=400):
        """Return an error payload and set the response status. Meant to be
        returned from a `returns_json`-decorated endpoint.
        """
        self.request.response.setStatus(status)
        return {"success": False, "error": message}

    def success(self, **data):
        """Return a success payload. Meant to be returned from a
        `returns_json`-decorated endpoint.
        """
        data["success"] = True
        return data


class JSONView(PublishTraverseView):
    """`PublishTraverseView` for views that only serve JSON endpoints.

    A bare call or an unknown subpath returns a JSON 404 instead of raising,
    so the JSON contract stays symmetric for every route.
    """

    @returns_json
    def handle_not_found(self):
        return self.error("Not found", status=404)
