Labels API
----------

The `@@labels` view (`senaite.core.browser.label.api.LabelsAPI`) is a
`JSONView` that adds, removes and lists labels through subpath routes:
`@@labels/add`, `@@labels/remove`, `@@labels/available`.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t LabelsAPI


Test Setup
..........

    >>> import json
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from senaite.core.browser.label.api import LabelsAPI
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup

    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager'])
    >>> client = api.create(portal.clients, "Client", Name="ACME", ClientID="A")
    >>> contact = api.create(client, "Contact", Firstname="John", Surname="Doe")
    >>> sampletype = api.create(setup.sampletypes, "SampleType",
    ...     Prefix="water", MinimumVolume="100 ml")
    >>> service = api.create(bika_setup.bika_analysisservices,
    ...     "AnalysisService", title="PH", Keyword="PH")
    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "DateSampled": "2025-01-01",
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> sample = create_analysisrequest(client, request, values,
    ...                                 [service.UID()])

Helper to call a labels route on the sample:

    >>> def call(route, **form):
    ...     request.form.clear()
    ...     request.form.update(form)
    ...     view = LabelsAPI(sample, request)
    ...     view.traverse_subpath = [route]
    ...     return json.loads(view())


Add, list and remove labels
...........................

    >>> result = call("add", label="urgent")
    >>> result["success"]
    True
    >>> "urgent" in result["labels"]
    True

The label shows up in the available labels:

    >>> names = [l["name"] for l in call("available")["labels"]]
    >>> "urgent" in names
    True

Removing it works too:

    >>> result = call("remove", label="urgent")
    >>> result["success"]
    True
    >>> "urgent" in result["labels"]
    False


Empty input and unknown routes
..............................

    >>> call("add")["error"]
    u'No labels submitted'

    >>> print(call("bogus")["error"])
    Unknown route. Use one of: add, remove, available
    >>> request.response.getStatus()
    404


Permission enforcement via `require_permission`
...............................................

A user without the "Manage Labels" permission gets a 403 on the write
routes:

    >>> setRoles(portal, TEST_USER_ID, ['Authenticated'])
    >>> result = call("add", label="urgent")
    >>> result["success"]
    False
    >>> print(result["error"])
    Forbidden
    >>> request.response.getStatus()
    403

    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager'])
