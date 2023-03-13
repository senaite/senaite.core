API Label
---------

The label API provides a simple interface to manage object labels.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_label

Test Setup
..........

Needed Imports:

    >>> from senaite.core.api.label import *

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Environment Setup
.................

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()

List all Labels
...............

List all active global labels in the system:

    >>> list_labels()
    []

Create some Labels
..................

Create global labels:

    >>> new = map(create_label, ["Important", "Urgent", "Critical"])
    >>> list_labels()
    ['Urgent', 'Critical', 'Important']

Duplicates are ignored per default:

    >>> new = create_label("Important")
    >>> list_labels()
    ['Urgent', 'Critical', 'Important']

Label content objects
.....................

Basically all objects can be labeled, both AT or DX based.

Try first to label some AT based objects

    >>> client1 = api.create(portal.clients, "Client", Name="NARALABS", ClientID="NL")
    >>> client2 = api.create(portal.clients, "Client", Name="RIDINGBYTES", ClientID="RB")

Add a string label:

    >>> add_obj_labels(client1, "Important")
    ('Important',)
