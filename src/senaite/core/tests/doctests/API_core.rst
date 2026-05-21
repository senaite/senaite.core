SENAITE core API
----------------

The senaite.core.api module is the gradual replacement for the
long-standing bika.lims.api. It exposes general-purpose helpers
that do not depend on bika.lims.

Domain-specific helpers live in submodules covered by their own
doctests (e.g. ``API_hazard.rst`` for ``senaite.core.api.hazard``).

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API_core


Test Setup
..........

Imports

    >>> from senaite.core import api


Portal helpers
..............

Get the portal object:

    >>> portal = api.get_portal()
    >>> portal == self.portal
    True

Get the absolute URL of the portal:

    >>> url = api.get_portal_url()
    >>> url == self.portal.absolute_url()
    True

    >>> url.startswith("http")
    True


Generic attribute getter
........................

``api.get_attr`` returns an attribute from a content object or a
catalog brain, calling it when it is a method.

A small object stand-in is enough to illustrate the behaviour:

    >>> class Thing(object):
    ...     plain = 42
    ...     def method(self):
    ...         return "called"

    >>> obj = Thing()

A bare attribute is returned as-is:

    >>> api.get_attr(obj, "plain")
    42

A method-valued attribute is invoked and the call result is
returned:

    >>> api.get_attr(obj, "method")
    'called'

Missing attributes return ``None`` by default:

    >>> api.get_attr(obj, "nope") is None
    True

A custom default can be supplied:

    >>> api.get_attr(obj, "nope", default="fallback")
    'fallback'

When the attribute exists but the call raises ``TypeError`` (e.g.
expects extra arguments), ``default`` is returned instead of
propagating the error:

    >>> class Picky(object):
    ...     def method(self, required):
    ...         return required

    >>> api.get_attr(Picky(), "method", default="fallback")
    'fallback'

An empty input short-circuits to ``default``:

    >>> api.get_attr(None, "anything") is None
    True

    >>> api.get_attr("", "anything", default="missing")
    'missing'

Passing ``catalog`` normalizes the input to a brain via UID
lookup, so the same call accepts a content object, a catalog
brain or a UID string. Look up the bika setup folder three ways
and read its ``Title`` from the brain metadata:

    >>> from bika.lims import api as bika_api
    >>> setup = self.portal.bika_setup
    >>> uid = bika_api.get_uid(setup)
    >>> brain = self.portal.portal_catalog(UID=uid)[0]
    >>> expected = setup.Title()

    >>> api.get_attr(setup, "Title",
    ...              catalog="portal_catalog") == expected
    True

    >>> api.get_attr(brain, "Title",
    ...              catalog="portal_catalog") == expected
    True

    >>> api.get_attr(uid, "Title",
    ...              catalog="portal_catalog") == expected
    True

A bogus UID matches no brain and falls back to ``default``:

    >>> api.get_attr("does-not-exist", "Title",
    ...              catalog="portal_catalog", default="missing")
    'missing'
