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

Get all Labels
..............

Get all active labels in the system:

    >>> get_all_labels()
    []

Create some Labels
..................

Create a bunch of labels:

    >>> new = map(create_label, ["Important", "Urgent", "Critical"])
    >>> get_all_labels()
    ['Urgent', 'Critical', 'Important']

Duplicates are ignored per default:

    >>> new = create_label("Important")
    >>> get_all_labels()
    ['Urgent', 'Critical', 'Important']
