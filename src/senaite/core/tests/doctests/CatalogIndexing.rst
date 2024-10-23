Catalog Indexing
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t CatalogIndexing


Test Setup
..........

Needed Imports:

    >>> import os
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from Products.CMFCore.indexing import processQueue

    >>> from senaite.core.catalog import ANALYSIS_CATALOG
    >>> from senaite.core.catalog import AUDITLOG_CATALOG
    >>> from senaite.core.catalog import CLIENT_CATALOG
    >>> from senaite.core.catalog import CONTACT_CATALOG
    >>> from senaite.core.catalog import LABEL_CATALOG
    >>> from senaite.core.catalog import REPORT_CATALOG
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.catalog import SENAITE_CATALOG
    >>> from senaite.core.catalog import SETUP_CATALOG
    >>> from senaite.core.catalog import WORKSHEET_CATALOG

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

    >>> def is_indexed(obj, *catalogs, **kw):
    ...     """Checks if the passed in object is indexed in the catalogs
    ...     """
    ...     formatted = kw.get("formatted", True)
    ...     query = {"UID": api.get_uid(obj)}
    ...     results = []
    ...     summary = []
    ...     for catalog in catalogs:
    ...         cat = api.get_tool(catalog)
    ...         res = cat(query)
    ...         results.append((catalog, len(res)))
    ...         text = "%s: %s (found %s)" % (catalog, "YES" if len(res) > 0 else "NO", len(res))
    ...         summary.append(text)
    ...     if formatted:
    ...         print("\n".join(summary))
    ...         return
    ...     return results

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> ALL_SENAITE_CATALOGS = [
    ...    ANALYSIS_CATALOG,
    ...    AUDITLOG_CATALOG,
    ...    CLIENT_CATALOG,
    ...    CONTACT_CATALOG,
    ...    LABEL_CATALOG,
    ...    REPORT_CATALOG,
    ...    SAMPLE_CATALOG,
    ...    SENAITE_CATALOG,
    ...    SETUP_CATALOG,
    ...    WORKSHEET_CATALOG,
    ... ]

    >>> UID_CATALOG = "uid_catalog"
    >>> PORTAL_CATALOG = "portal_catalog"

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Sampler'])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Test catalog indexing of Samples
................................

Be sure the queue is processed:

    >>> processing = processQueue()

Set testmod on:

    >>> # os.environ["TESTMOD"] = "1"

NOTE: The TESTMOD environment variable can be used to conditionally set some
debug statements in the code, e.g.::

    import os
    if os.getenv("TESTMOD", False):
        print "ZCatalog.Catalog.catalogObject: catalog=%s object=%s" % (
            self.id, repr(object))

Create a new sample:

    >>> sample = new_sample([Cu])
    >>> api.get_workflow_status_of(sample)
    'sample_due'

The sample should be indexed in the `senaite_sample_catalog`:

   >>> is_indexed(sample, SAMPLE_CATALOG)
   senaite_catalog_sample: YES (found 1)

It should not be indexed in the other catalogs:

   >>> is_indexed(sample, *list(filter(lambda x: x != SAMPLE_CATALOG, ALL_SENAITE_CATALOGS)))
   senaite_catalog_analysis: NO (found 0)
   senaite_catalog_auditlog: NO (found 0)
   senaite_catalog_client: NO (found 0)
   senaite_catalog_contact: NO (found 0)
   senaite_catalog_label: NO (found 0)
   senaite_catalog_report: NO (found 0)
   senaite_catalog: NO (found 0)
   senaite_catalog_setup: NO (found 0)
   senaite_catalog_worksheet: NO (found 0)

It should be indexed in the `uid_catalog`:

   >>> is_indexed(sample, UID_CATALOG)
   uid_catalog: YES (found 1)

But not in the `portal_catalog`:

   >>> is_indexed(sample, PORTAL_CATALOG)
   portal_catalog: NO (found 0)


Test catalog indexing of Analyses
.................................

The analyses should be indexed in the `senaite_analysis_catalog`:

   >>> is_indexed(sample.Cu, ANALYSIS_CATALOG)
   senaite_catalog_analysis: YES (found 1)

It should not be indexed in the other catalogs:

   >>> is_indexed(sample.Cu, *list(filter(lambda x: x != ANALYSIS_CATALOG, ALL_SENAITE_CATALOGS)))
   senaite_catalog_auditlog: NO (found 0)
   senaite_catalog_client: NO (found 0)
   senaite_catalog_contact: NO (found 0)
   senaite_catalog_label: NO (found 0)
   senaite_catalog_report: NO (found 0)
   senaite_catalog_sample: NO (found 0)
   senaite_catalog: NO (found 0)
   senaite_catalog_setup: NO (found 0)
   senaite_catalog_worksheet: NO (found 0)
