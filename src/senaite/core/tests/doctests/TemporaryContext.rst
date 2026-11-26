Temporary Context
-----------------

The `temporary_context` view creates a temporary object of a portal type,
e.g. for the reference widgets in add forms. The first name of the path is
the portal type, a second name publishes a view of the temporary object with
its own permission.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t TemporaryContext


Test Setup
..........

    >>> import transaction
    >>> from bika.lims import api
    >>> from bika.lims.api import create
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles
    >>> from AccessControl.SecurityManagement import getSecurityManager
    >>> from AccessControl.SecurityManagement import newSecurityManager
    >>> from AccessControl.SecurityManagement import setSecurityManager
    >>> from plone.protect.authenticator import createToken
    >>> from plone.testing.zope import Browser
    >>> from senaite.core.browser.globals.temporary_context import TemporaryContext
    >>> from senaite.core.browser.widgets.referencewidget_search import ReferenceWidgetSearch
    >>> from zExceptions import NotFound

    >>> portal = self.portal
    >>> request = self.request
    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])

Two clients, each with a contact that is linked to a user:

    >>> clients = portal.clients
    >>> client1 = create(clients, "Client", title="Client-1", ClientID="C1")
    >>> client2 = create(clients, "Client", title="Client-2", ClientID="C2",
    ...                  EmailAddress="client-2@example.com")
    >>> contact1 = create(client1, "Contact", Firstname="Contact-1")
    >>> contact2 = create(client2, "Contact", Firstname="Contact-2")

    >>> user1 = ploneapi.user.create(email="contact-1@example.com",
    ...     username="user-1", password=TEST_USER_PASSWORD)
    >>> user2 = ploneapi.user.create(email="contact-2@example.com",
    ...     username="user-2", password=TEST_USER_PASSWORD)
    >>> contact1.setUser(user1)
    True
    >>> contact2.setUser(user2)
    True
    >>> transaction.commit()

Helper to traverse the view like the publisher does:

    >>> def traverse(context, *names):
    ...     obj = TemporaryContext(context, request)
    ...     for name in names:
    ...         obj = obj.publishTraverse(request, name)
    ...     return obj

Helper to open a path below the first client as the user of its contact:

    >>> def open_as_user1(path, token=None):
    ...     browser = Browser(self.layer["app"])
    ...     browser.handleErrors = False
    ...     browser.addHeader("Authorization", "Basic {}:{}".format(
    ...         "user-1", TEST_USER_PASSWORD))
    ...     if token:
    ...         browser.addHeader("X-CSRF-TOKEN", token)
    ...     url = "{}/@@temporary_context/{}".format(
    ...         api.get_url(client1), path)
    ...     browser.open(url)
    ...     return browser.contents

Helper to check that a path below the first client is not found:

    >>> def not_found(path):
    ...     try:
    ...         open_as_user1(path)
    ...     except NotFound:
    ...         return True
    ...     return False


Views of the temporary context
..............................

The reference widgets in add forms search with a view of the temporary
context:

    >>> view = traverse(client1, "Contact", "referencewidget_search")
    >>> isinstance(view, ReferenceWidgetSearch)
    True

    >>> api.is_temporary(view.context)
    True

    >>> api.get_portal_type(view.context)
    'Contact'

    >>> api.get_parent(view.context) == client1
    True

The view is published with its own checks, e.g. the CSRF token of the search:

    >>> open_as_user1("Contact/referencewidget_search/search")
    Traceback (most recent call last):
    ...
    Forbidden: ...

With the CSRF token of the user, as the widget sends it, the search works.
The test layer does not load the JSON API, so we register its batch adapter:

    >>> from Products.CMFPlone.PloneBatch import Batch as PloneBatch
    >>> from senaite.jsonapi.batch import Batch
    >>> from senaite.jsonapi.interfaces import IBatch
    >>> from zope.component import provideAdapter
    >>> provideAdapter(Batch, (PloneBatch, ), IBatch)

    >>> security_manager = getSecurityManager()
    >>> newSecurityManager(None, portal.acl_users.getUserById("user-1"))
    >>> token = createToken()
    >>> setSecurityManager(security_manager)

    >>> result = open_as_user1(
    ...     "Contact/referencewidget_search/search"
    ...     "?catalog=senaite_catalog_setup&portal_type=Label", token=token)
    >>> '"items": []' in result
    True

An unknown view is not found:

    >>> traverse(client1, "Contact", "unknown")
    Traceback (most recent call last):
    ...
    NotFound: ...


Other names are not traversed
.............................

The user of the first client can use the view on the first client:

    >>> "Contact_temporary" in open_as_user1("Contact")
    True

The path after the portal type does not reach objects of the other client:

    >>> not_found("Contact/client-2/getEmailAddress")
    True

    >>> not_found("Contact/{}/{}/getMobilePhone".format(
    ...     client2.getId(), contact2.getId()))
    True

Nor portal tools:

    >>> not_found("Contact/portal_membership/listMemberIds")
    True

Nor methods of the temporary object:

    >>> not_found("Contact/getId")
    True

The contact of the other client stays linked to its user:

    >>> contact2.getUsername()
    'user-2'
