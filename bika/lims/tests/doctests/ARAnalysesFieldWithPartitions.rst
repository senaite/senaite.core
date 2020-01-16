AR Analyses Field when using Partitions
=======================================

The setter of the ARAnalysesField takes descendants (partitions) and ancestors
from the current instance into account to prevent inconsistencies: In a Sample
lineage analyses from a node are always masked by same analyses in leaves. This
can drive to inconsistencies and therefore, there is the need to keep the tree
without duplicates.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ARAnalysesFieldWithPartitions

Test Setup
----------

Needed imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from zope.interface import alsoProvides
    >>> from zope.interface import noLongerProvides

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def get_analysis_from(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Creation of a Sample with a Partition
-------------------------------------

Create a Sample and receive:

    >>> sample = new_sample([Cu, Fe])

Create a Partition containing of the Sample, containing the analysis `Cu`:

    >>> cu = get_analysis_from(sample, Cu)
    >>> partition = create_partition(sample, request, [cu])

The analysis 'Cu' lives in the partition:

    >>> cu = get_analysis_from(partition, Cu)
    >>> api.get_parent(cu) == partition
    True

Although is also returned by the primary:

    >>> cu = get_analysis_from(sample, Cu)
    >>> api.get_parent(cu) == partition
    True
    >>> api.get_parent(cu) == sample
    False


Analyses retrieval
------------------

Get the ARAnalysesField to play with:

    >>> field = sample.getField("Analyses")

get_from_instance
.................

When asked for `Fe` when the primary is given, it returns the analysis, cause
it lives in the primary:

    >>> fe = field.get_from_instance(sample, Fe)
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True

But when asked for `Cu` when the primary is given, it returns None, cause it
lives in the partition:

    >>> cu = field.get_from_instance(sample, Cu)
    >>> cu is None
    True

While it returns the analysis when the partition is used:

    >>> cu = field.get_from_instance(partition, Cu)
    >>> cu.getServiceUID() == api.get_uid(Cu)
    True

But when asking the partition for `Fe` it returns None, cause it lives in the
ancestor:

    >>> fe = field.get_from_instance(partition, Fe)
    >>> fe is None
    True

get_from_ancestor
.................

When asked for `Fe` to primary, it returns None because there is no ancestor
containing `Fe`:

    >>> fe = field.get_from_ancestor(sample, Fe)
    >>> fe is None
    True

But when asked for `Fe` to the partition, it returns the analysis, cause it
it lives in an ancestor from the partition:

    >>> fe = field.get_from_ancestor(partition, Fe)
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True

If I ask for `Cu`, that lives in the partition, it will return None for both:

    >>> cu = field.get_from_ancestor(sample, Cu)
    >>> cu is None
    True

    >>> cu = field.get_from_ancestor(partition, Cu)
    >>> cu is None
    True

get_from_descendant
...................

When asked for `Fe` to primary, it returns None because there is no descendant
containing `Fe`:

    >>> fe = field.get_from_descendant(sample, Fe)
    >>> fe is None
    True

And same with partition:

    >>> fe = field.get_from_descendant(partition, Fe)
    >>> fe is None
    True

When asked for `Cu` to primary, it returns the analysis, because it lives in a
descendant (partition):

    >>> cu = field.get_from_descendant(sample, Cu)
    >>> cu.getServiceUID() == api.get_uid(Cu)
    True

But returns None if I ask to the partition:

    >>> cu = field.get_from_descendant(partition, Cu)
    >>> cu is None
    True

get_analyses_from_descendants
.............................

It returns the analyses contained by the descendants:

    >>> field.get_analyses_from_descendants(sample)
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>]

    >>> field.get_analyses_from_descendants(partition)
    []


Resolution of analyses from the Sample lineage
----------------------------------------------

resolve_analysis
................

Resolves the analysis from the sample lineage if exists:

    >>> fe = field.resolve_analysis(sample, Fe)
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True
    >>> fe.aq_parent == sample
    True

    >>> cu = field.resolve_analysis(sample, Cu)
    >>> cu.getServiceUID() == api.get_uid(Cu)
    True
    >>> cu.aq_parent == partition
    True

    >>> au = field.resolve_analysis(sample, Au)
    >>> au is None
    True

But when we use the partition and the analysis is found in an ancestor, it
moves the analysis into the partition:

    >>> fe = field.resolve_analysis(partition, Fe)
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True
    >>> fe.aq_parent == partition
    True
    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]


Addition of analyses
--------------------

add_analysis
............

Setup required parameters:

    >>> prices = hidden = dict()

If we try to add now an analysis that already exists, either in the partition or
in the primary, the analysis won't be added:

    >>> added = field.add_analysis(sample, Fe, prices, hidden)
    >>> added is None
    True
    >>> sample.objectValues("Analysis")
    []

    >>> added = field.add_analysis(partition, Fe, prices, hidden)
    >>> added is None
    True
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]

If we add a new analysis, this will be added in the sample we are working with:

    >>> au = field.add_analysis(sample, Au, prices, hidden)
    >>> au.getServiceUID() == api.get_uid(Au)
    True
    >>> sample.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001/Au>]
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]

Apply the changes:

    >>> transaction.commit()

If I try to add an analysis that exists in an ancestor, the analysis gets moved
while the function returns None:

    >>> added = field.add_analysis(partition, Au, prices, hidden)
    >>> added is None
    True
    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]
