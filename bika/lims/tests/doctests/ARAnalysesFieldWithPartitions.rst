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
    >>> Mg = api.create(setup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="20", Category=category.UID())


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

    >>> fe = field.get_from_instance(sample, Fe)[0]
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True

But when asked for `Cu` when the primary is given, it returns empty, cause it
lives in the partition:

    >>> field.get_from_instance(sample, Cu)
    []

While it returns the analysis when the partition is used:

    >>> cu = field.get_from_instance(partition, Cu)[0]
    >>> cu.getServiceUID() == api.get_uid(Cu)
    True

But when asking the partition for `Fe` it returns empty, cause it lives in the
ancestor:

    >>> field.get_from_instance(partition, Fe)
    []

get_from_ancestor
.................

When asked for `Fe` to primary, it returns empty because there is no ancestor
containing `Fe`:

    >>> field.get_from_ancestor(sample, Fe)
    []

But when asked for `Fe` to the partition, it returns the analysis, cause it
it lives in an ancestor from the partition:

    >>> fe = field.get_from_ancestor(partition, Fe)[0]
    >>> fe.getServiceUID() == api.get_uid(Fe)
    True

If I ask for `Cu`, that lives in the partition, it will return empty for both:

    >>> field.get_from_ancestor(sample, Cu)
    []

    >>> field.get_from_ancestor(partition, Cu)
    []

get_from_descendant
...................

When asked for `Fe` to primary, it returns None because there is no descendant
containing `Fe`:

    >>> field.get_from_descendant(sample, Fe)
    []

And same with partition:

    >>> field.get_from_descendant(partition, Fe)
    []

When asked for `Cu` to primary, it returns the analysis, because it lives in a
descendant (partition):

    >>> field.get_from_descendant(sample, Cu)
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>]

But returns None if I ask to the partition:

    >>> field.get_from_descendant(partition, Cu)
    []

get_analyses_from_descendants
.............................

It returns the analyses contained by the descendants:

    >>> field.get_analyses_from_descendants(sample)
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>]

    >>> field.get_analyses_from_descendants(partition)
    []


Resolution of analyses from the Sample lineage
----------------------------------------------

resolve_analyses
................

Resolves the analysis from the sample lineage if exists:

    >>> field.resolve_analyses(sample, Fe)
    [<Analysis at /plone/clients/client-1/W-0001/Fe>]

    >>> field.resolve_analyses(sample, Cu)
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>]

    >>> field.resolve_analyses(sample, Au)
    []

But when we use the partition and the analysis is found in an ancestor, it
moves the analysis into the partition:

    >>> field.resolve_analyses(partition, Fe)
    [<Analysis at /plone/clients/client-1/W-0001-P01/Fe>]

    >>> sample.objectValues("Analysis")
    []

    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]


Addition of analyses
--------------------

add_analysis
............

If we try to add now an analysis that already exists, either in the partition or
in the primary, the analysis won't be added:

    >>> field.add_analysis(sample, Fe)
    >>> sample.objectValues("Analysis")
    []

    >>> field.add_analysis(partition, Fe)
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]

If we add a new analysis, this will be added in the sample we are working with:

    >>> field.add_analysis(sample, Au)
    >>> sample.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001/Au>]
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>]

Apply the changes:

    >>> transaction.commit()

If I try to add an analysis that exists in an ancestor, the analysis gets moved
while the function returns None:

    >>> field.add_analysis(partition, Au)
    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]


Set analyses
------------

If we try to set same analyses as before to the root sample, nothing happens
because the analyses are already there:

    >>> field.set(sample, [Cu, Fe, Au])

The analyses still belong to the partition though:

    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]

Same result if I set the analyses to the partition:

    >>> field.set(partition, [Cu, Fe, Au])
    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]

If I add a new analysis in the list, the analysis is successfully added:

    >>> field.set(sample, [Cu, Fe, Au, Mg])
    >>> sample.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001/Mg>]

And the partition keeps its own analyses:

    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]

Apply the changes:

    >>> transaction.commit()

If I set the same analyses to the partition, the `Mg` analysis is moved into
the partition:

    >>> field.set(partition, [Cu, Fe, Au, Mg])
    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>, <Analysis at /plone/clients/client-1/W-0001-P01/Mg>]

To remove `Mg` analysis, pass the list without `Mg`:

    >>> field.set(sample, [Cu, Fe, Au])

The analysis `Mg` has been removed, although it belonged to the partition:

    >>> sample.objectValues("Analysis")
    []
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]

But if I add a new analysis to the primary and I try to remove it from the
partition, nothing will happen:

    >>> field.set(sample, [Cu, Fe, Au, Mg])

    >>> field.set(partition, [Cu, Fe, Au])

    >>> sample.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001/Mg>]
    >>> partition.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/W-0001-P01/Cu>, <Analysis at /plone/clients/client-1/W-0001-P01/Fe>, <Analysis at /plone/clients/client-1/W-0001-P01/Au>]
