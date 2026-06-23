Client
------

Tests for the Client content type.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t Client


Test Setup
..........

Needed Imports:

    >>> from AccessControl import getSecurityManager
    >>> from bika.lims import api
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.permissions import ManageSenaite

Variables:

    >>> portal = self.portal
    >>> request = self.request

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])

Create a Client:

    >>> client = api.create(
    ...     portal.clients,
    ...     "Client",
    ...     Name="Happy Hills",
    ...     ClientID="HH",
    ... )


Discount Fields
...............

`BulkDiscount` and `MemberDiscountApplies` drive pricing logic and must be
controlled by lab staff only. Client contacts (Owner on their Client) must
not be able to toggle them on the edit form.

Both fields are gated by the `ManageSenaite` permission:

    >>> bulk_field = client.getField("BulkDiscount")
    >>> bulk_field.write_permission == ManageSenaite
    True

    >>> member_field = client.getField("MemberDiscountApplies")
    >>> member_field.write_permission == ManageSenaite
    True

With the `LabManager` role, the current user is allowed to write the
discount flags:

    >>> sm = getSecurityManager()
    >>> sm.checkPermission(ManageSenaite, client) and True or False
    True

After dropping all lab roles and keeping only `Owner` (the role a client
contact gets on their own Client object), the permission is denied:

    >>> setRoles(portal, TEST_USER_ID, ["Owner"])
    >>> sm = getSecurityManager()
    >>> sm.checkPermission(ManageSenaite, client) and True or False
    False

Reading the flags stays unaffected so existing pricing/listing/invoice
code paths keep working:

    >>> bulk_field.checkPermission("r", client) and True or False
    True
    >>> member_field.checkPermission("r", client) and True or False
    True
