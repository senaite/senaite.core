PublishTraverseView / JSONView
------------------------------

`senaite.core.browser.views.PublishTraverseView` is a base browser view that
dispatches traversal subpaths to `ajax_<name>` methods. `JSONView` is its
JSON-only flavor: a bare call or an unknown route returns a JSON 404.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PublishTraverseView


Test Setup
..........

    >>> import json
    >>> from bika.lims.decorators import returns_json
    >>> from senaite.core.browser.views import JSONView
    >>> from senaite.core.browser.views import PublishTraverseView

    >>> portal = self.portal
    >>> request = self.request


A demo JSON view with two endpoints
...................................

    >>> class DemoView(JSONView):
    ...     @returns_json
    ...     def ajax_hello(self, name="world"):
    ...         return self.success(greeting="hello {}".format(name))
    ...     @returns_json
    ...     def ajax_echo(self):
    ...         return self.success(data=self.get_json())

Helper to drive the view through a traversal subpath:

    >>> def call(*subpath):
    ...     view = DemoView(portal, request)
    ...     view.traverse_subpath = list(subpath)
    ...     return json.loads(view())


Dispatch a subpath to its `ajax_` method
........................................

    >>> result = call("hello")
    >>> result["success"]
    True
    >>> print(result["greeting"])
    hello world

Remaining subpath segments are passed as positional arguments:

    >>> print(call("hello", "bob")["greeting"])
    hello bob


Unknown routes and bare calls return a JSON 404
...............................................

    >>> call("unknown")["success"]
    False
    >>> print(call("unknown")["error"])
    Not found
    >>> request.response.getStatus()
    404

A bare call (no subpath) is also handled as not found:

    >>> view = DemoView(portal, request)
    >>> json.loads(view())["success"]
    False


Reading the JSON body
.....................

    >>> request["BODY"] = '{"a": 1, "b": 2}'
    >>> body = call("echo")["data"]
    >>> sorted(body.items())
    [(u'a', 1), (u'b', 2)]

    >>> request["BODY"] = "not json"
    >>> call("echo")["data"]
    {}


Non-JSON views raise a 404 on an unknown route
..............................................

`PublishTraverseView` (the non-JSON base) raises a `NotFound` instead, so a
page view does not accidentally return a JSON body for a wrong URL:

    >>> from zExceptions import NotFound
    >>> plain = PublishTraverseView(portal, request)
    >>> plain.traverse_subpath = ["nope"]
    >>> plain()
    Traceback (most recent call last):
    ...
    NotFound: ...
