Show or Hide Prices
===================

There's a setting in BikaSetup called 'Include and display pricing information'.
If this setting is disabled, then no mention of pricing or invoicing should
appear in the system.  I still allowed the fields for Price to appear in
AnalysisService edit form, so that they may be modified while still remaining
hidden elsewhere.

Running this test from the buildout directory:

    bin/test -t ShowPrices



Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from time import sleep
    >>> import transaction

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def enableShowPrices():
    ...     self.portal.bika_setup.setShowPrices(True)
    ...     transaction.commit()

    >>> def disableShowPrices():
    ...     self.portal.bika_setup.setShowPrices(False)
    ...     transaction.commit()

Variables:

    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> request = self.request
    >>> portal = self.portal
    >>> bs = portal.bika_setup
    >>> laboratory = bs.laboratory
    >>> portal_url = portal.absolute_url()

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

Now we need to create some basic content for our tests:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(portal.bika_setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(portal.bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(portal.bika_setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(portal.bika_setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(portal.bika_setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="409.17", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(portal.bika_setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="208.20", Category=category.UID())
    >>> profile = api.create(portal.bika_setup.bika_analysisprofiles, "AnalysisProfile", title="Profile", Service=[Fe.UID(), Cu.UID()])
    >>> template = api.create(portal.bika_setup.bika_artemplates, "ARTemplate", title="Template", AnalysisProfile=[profile.UID()])

Enable accreditation for the lab

    >>> laboratory.setLaboratoryAccredited(True)

And start a browser:

    >>> transaction.commit()
    >>> browser = self.getBrowser()

Analysis Request Add form
-------------------------

Verify that the price and invoice fields are present when ShowPrices is enabled:

    >>> enableShowPrices()
    >>> browser.open(client.absolute_url() + "/ar_add")

    >>> True if "Discount" in browser.contents else "ShowPrices is True, and Discount field is missing from AR Add."
    True
    >>> True if "Subtotal" in browser.contents else "ShowPrices is True, and Subtotal field is missing from AR Add."
    True
    >>> True if "VAT" in browser.contents else "ShowPrices is True, and VAT field is missing from AR Add."
    True
    >>> True if "Total" in browser.contents else "ShowPrices is True, and Total field is missing from AR Add."
    True
    >>> True if "Invoice Exclude" in browser.contents else "ShowPrices is True, and Invoice Exclude field is missing from AR Add."
    True

And then that the opposite is true:

    >>> disableShowPrices()
    >>> browser.open(client.absolute_url() + "/ar_add")

    >>> True if "Discount" not in browser.contents else "ShowPrices is False, Discount field should not be present in AR Add."
    True
    >>> True if "Subtotal" not in browser.contents else "ShowPrices is False, Subtotal field should not be present in AR Add."
    True
    >>> True if "VAT" not in browser.contents else "ShowPrices is False, VAT field should not be present in AR Add."
    True
    >>> True if "Total" not in browser.contents else "ShowPrices is False, Total field should not be present in AR Add."
    True
    >>> True if "Invoice Exclude" not in browser.contents else "ShowPrices is False, Invoice Exclude field should not be present in AR Add."
    True

Disable MemberDiscountApplies, and verify that it always vanishes from AR add:

    >>> client.setMemberDiscountApplies(False)
    >>> transaction.commit()

    >>> enableShowPrices()
    >>> browser.open(client.absolute_url() + "/ar_add")
    >>> True if "Discount" not in browser.contents else "Discount field should be hidden."
    True
    >>> disableShowPrices()
    >>> browser.open(client.absolute_url() + "/ar_add")
    >>> True if "Discount" not in browser.contents else "Discount field should be hidden."
    True

Analysis Request View
---------------------

Test show/hide prices when viewing an AR.  First, create an AR:

    >>> values = {
    ...     'Client': client.UID(),
    ...     'Contact': contact.UID(),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype.UID()}
    >>> service_uids = [Cu.UID(), Fe.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)

With ShowPrices enabled, the Invoice tab should be rendered:

    >>> enableShowPrices()
    >>> browser.open(ar.absolute_url())
    >>> True if 'contentview-invoice' in browser.contents else "Invoice Tab is not visible, but ShowPrices is True."
    True

And when ShowPrices is off, the Invoice tab should not be present at all:

    >>> disableShowPrices()
    >>> browser.open(ar.absolute_url())
    >>> True if 'contentview-invoice' not in browser.contents else "Invoice Tab is visible, but ShowPrices is False."
    True

Client discount fields show/hide
--------------------------------

    >>> enableShowPrices()
    >>> browser.open(client.absolute_url() + "/edit")
    >>> True if 'discount' in browser.contents else "Client discount field should be visible, but is not"
    True

    >>> disableShowPrices()
    >>> browser.open(client.absolute_url() + "/edit")
    >>> True if 'discount' not in browser.contents else "Client discount field should not be visible, but here it is"
    True
