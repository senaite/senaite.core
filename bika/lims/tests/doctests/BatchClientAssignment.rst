Analysis publication guard and event
====================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t BatchClientAssignment


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from zope.lifecycleevent import modified

Variables and basic objects for the test:

    >>> portal = self.portal
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)


Batch creation and Client assignment
------------------------------------

Create a new Batch:

    >>> batches = portal.batches
    >>> batch = api.create(batches, "Batch", title="Test batch")
    >>> batch.aq_parent
    <BatchFolder at /plone/batches>

The batches folder contains the batch, while Client folder remains empty:

    >>> len(batches.objectValues("Batch"))
    1
    >>> len(client.objectValues("Batch"))
    0

Assign a client to the Batch and the latter is automatically moved inside
Client's folder:

    >>> batch.setClient(client)
    >>> modified(batch)
    >>> len(batches.objectValues("Batch"))
    0
    >>> len(client.objectValues("Batch"))
    1

If the client is assigned on creation, same behavior as before:

    >>> batch = api.create(portal.batches, "Batch", Client=client)
    >>> len(batches.objectValues("Batch"))
    0
    >>> len(client.objectValues("Batch"))
    2
