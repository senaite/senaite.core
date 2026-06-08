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


IntId helpers
.............

The site's ``IIntIds`` utility maps every persistent content object to a
stable integer id used by relation storage and other cross-reference machinery.
``senaite.core.api`` wraps the bare utility with four thin helpers.

The setup folder and the clients folder are both persistent containers that
``five.intid`` registered with the ``IIntIds`` utility on site creation:

    >>> setup = self.portal.setup
    >>> clients = self.portal.clients

``get_intid`` returns the IntId of an object:

    >>> setup_intid = api.get_intid(setup)
    >>> isinstance(setup_intid, int)
    True

    >>> clients_intid = api.get_intid(clients)
    >>> isinstance(clients_intid, int)
    True

    >>> setup_intid != clients_intid
    True

``get_object_by_intid`` is the inverse — given an IntId, return the object it
points to:

    >>> api.get_object_by_intid(setup_intid).getPhysicalPath() == \
    ...     setup.getPhysicalPath()
    True

    >>> api.get_object_by_intid(clients_intid).getPhysicalPath() == \
    ...     clients.getPhysicalPath()
    True

Looking up an unknown IntId raises by default…

    >>> try:
    ...     api.get_object_by_intid(-1)
    ... except KeyError:
    ...     print("missing")
    missing

…unless a ``default`` is supplied, in which case it is returned:

    >>> api.get_object_by_intid(-1, default=None) is None
    True

    >>> api.get_object_by_intid(-1, default="absent")
    'absent'

To exercise the write helpers on a disposable object, create a new client.
``api.create`` requires elevated permissions:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(self.portal, TEST_USER_ID, ['Manager',])

    >>> from bika.lims import api as bika_api
    >>> client = bika_api.create(clients, "Client", title="IntId Client")

``five.intid``'s add-subscriber registered the new client automatically, so
``get_intid`` already returns a value:

    >>> client_intid = api.get_intid(client)
    >>> isinstance(client_intid, int)
    True

    >>> api.get_object_by_intid(client_intid).getPhysicalPath() == \
    ...     client.getPhysicalPath()
    True

Calling ``add_intid`` on an object that already has an IntId is a no-op — it
returns the existing IntId without allocating a new one:

    >>> api.add_intid(client) == client_intid
    True

    >>> api.get_intid(client) == client_intid
    True

Drop the registration with ``delete_intid`` and confirm the same default-marker
behaviour applies to ``get_intid``:

    >>> api.delete_intid(client)

    >>> try:
    ...     api.get_intid(client)
    ... except KeyError:
    ...     print("missing")
    missing

    >>> api.get_intid(client, default=None) is None
    True

The setup and clients folders are unaffected — ``delete_intid`` only touches
the object it is called with:

    >>> api.get_intid(setup) == setup_intid
    True

    >>> api.get_intid(clients) == clients_intid
    True

Calling ``delete_intid`` again on an already-unregistered object is a safe
no-op (the underlying ``KeyError`` is swallowed):

    >>> api.delete_intid(client)

``add_intid`` registers the object with every ``IIntIds`` utility and returns
the (possibly new) IntId:

    >>> new_intid = api.add_intid(client)
    >>> isinstance(new_intid, int)
    True

The registration is reachable from both sides again:

    >>> api.get_intid(client) == new_intid
    True

    >>> api.get_object_by_intid(new_intid).getPhysicalPath() == \
    ...     client.getPhysicalPath()
    True

Re-registering an already-registered object is idempotent — the returned IntId
does not change:

    >>> api.add_intid(client) == new_intid
    True

Clean up:

    >>> bika_api.delete(client, check_permissions=False)
