Secondary Analysis Request
==========================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SecondaryAnalysisRequest


Test Setup
----------

Needed Imports:

    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IAnalysisRequestSecondary
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup

Some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager",])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Create Secondary Analysis Request
---------------------------------

To create a Secondary Analysis Request we need first a primary (or source
Analysis Request) to which the secondary analysis request will refer to:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SamplingDate": DateTime(),
    ...     "DateSampled": DateTime(),
    ...     "SampleType": sampletype.UID() }
    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> primary = create_analysisrequest(client, request, values, service_uids)
    >>> primary
    <AnalysisRequest at /plone/clients/client-1/W-0001>

Receive the primary analysis request:

    >>> transitioned = do_action_for(primary, "receive")
    >>> api.get_workflow_status_of(primary)
    'sample_received'

Create the Secondary Analysis Request:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SampleType": sampletype.UID(),
    ...     "PrimaryAnalysisRequest": primary }

    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> secondary = create_analysisrequest(client, request, values, service_uids)
    >>> secondary
    <AnalysisRequest at /plone/clients/client-1/W-0001-S01>

    >>> secondary.getPrimaryAnalysisRequest()
    <AnalysisRequest at /plone/clients/client-1/W-0001>

The secondary AnalysisRequest also provides `IAnalysisRequestSecondary`:

    >>> IAnalysisRequestSecondary.providedBy(secondary)
    True

Dates match with those from the primary Analysis Request:

    >>> secondary.getDateSampled() == primary.getDateSampled()
    True

    >>> secondary.getSamplingDate() == primary.getSamplingDate()
    True

The secondary sample is automatically transitioned to `sample_received`:

    >>> api.get_workflow_status_of(secondary)
    'sample_received'

The SampleReceived date matches with the primary's:

    >>> secondary.getDateReceived() == primary.getDateReceived()
    True

Analyses have been also initialized automatically:

    >>> analyses = secondary.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

If I create another secondary sample using same AR as the primary:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SampleType": sampletype.UID(),
    ...     "PrimaryAnalysisRequest": primary }

    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> secondary = create_analysisrequest(client, request, values, service_uids)

The ID suffix of the new secondary sample increases in one unit:

    >>> secondary.getId()
    'W-0001-S02'

If I create a secondary sample from another secondary AR as the primary:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SampleType": sampletype.UID(),
    ...     "PrimaryAnalysisRequest": secondary }

    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> third = create_analysisrequest(client, request, values, service_uids)

The ID suffix is extended accordingly:

    >>> third.getId()
    'W-0001-S02-S01'

And the associated primary AR is the secondary sample we created earlier:

    >>> third.getPrimaryAnalysisRequest()
    <AnalysisRequest at /plone/clients/client-1/W-0001-S02>

And of course, keeps same date values:


    >>> third.getDateSampled() == secondary.getDateSampled()
    True

    >>> third.getSamplingDate() == secondary.getSamplingDate()
    True

    >>> third.getDateReceived() == secondary.getDateReceived()
    True

If we change the dates from the root Primary:

    >>> primary.setSamplingDate(DateTime() + 5)
    >>> primary.setDateSampled(DateTime() + 10)
    >>> primary.setDateReceived(DateTime() + 15)

Dates for secondaries are updated in accordance:

    >>> third.getSamplingDate() == secondary.getSamplingDate() == primary.getSamplingDate()
    True
    >>> third.getDateSampled() == secondary.getDateSampled() == primary.getDateSampled()
    True
    >>> third.getDateReceived() == secondary.getDateReceived() == primary.getDateReceived()
    True


Secondary Analysis Requests and partitions
------------------------------------------

When partitions are created from a secondary Analysis Request, the partitions
themselves are not considered secondaries from the primary AR, but partitions
of a Secondary Analysis Request.

Create a secondary Analysis Request:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SampleType": sampletype.UID(),
    ...     "PrimaryAnalysisRequest": primary }

    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> secondary = create_analysisrequest(client, request, values, service_uids)
    >>> secondary
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03>

Create a single partition from the secondary Analysis Request:

    >>> analyses = secondary.getAnalyses()
    >>> analyses_1 = analyses[0:1]
    >>> analyses_2 = analyses[1:]
    >>> partition = create_partition(secondary, request, analyses_1)
    >>> partition
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03-P01>

    >>> partition.isPartition()
    True

    >>> partition.getParentAnalysisRequest()
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03>

Partition does not provide `IAnalysisRequestSecondary`:

    >>> IAnalysisRequestSecondary.providedBy(partition)
    False

And does not keep the original Primary Analysis Request:

    >>> partition.getPrimaryAnalysisRequest() is None
    True

If we create another partition, the generated ID is increased in one unit:

    >>> partition = create_partition(secondary, request, analyses_2)
    >>> partition
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03-P02>

We can even create a secondary Analysis Request from a partition as the source:

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SampleType": sampletype.UID(),
    ...     "PrimaryAnalysisRequest": partition }

    >>> service_uids = map(api.get_uid, [Cu, Fe, Au])
    >>> secondary = create_analysisrequest(client, request, values, service_uids)
    >>> secondary
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03-P02-S01>

But note this new secondary is not considered a partition of a partition:

    >>> secondary.isPartition()
    False

But keeps the partition as the primary:

    >>> secondary.getPrimaryAnalysisRequest()
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03-P02>

We can also create new partitions from this weird secondary:

    >>> partition = create_partition(secondary, request, secondary.getAnalyses())
    >>> partition
    <AnalysisRequest at /plone/clients/client-1/W-0001-S03-P02-S01-P01>
