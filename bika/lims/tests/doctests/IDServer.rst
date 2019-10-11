ID Server
=========

The ID Server in SENAITE LIMS provides IDs for content items base of the given
format specification. The format string is constructed in the same way as a
python format() method based predefined variables per content type. The only
variable available to all type is 'seq'. Currently, seq can be constructed
either using number generator or a counter of existing items. For generated IDs,
one can specifypoint at which the format string will be split to create the
generator key. For counter IDs, one must specify context and the type of counter
which is either the number of backreferences or the number of contained objects.

Configuration Settings:
* format:
  - a python format string constructed from predefined variables like client,
    sampleType.
  - special variable 'seq' must be positioned last in the format string
* sequence type: [generated|counter]
* context: if type counter, provides context the counting function
* counter type: [backreference|contained]
* counter reference: a parameter to the counting function
* prefix: default prefix if none provided in format string
* split length: the number of parts to be included in the prefix

ToDo:
* validation of format strings

Running this test from the buildout directory::

    bin/test -t IDServer


Test Setup
----------

Needed Imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from zope.component import getUtility

    >>> from bika.lims import alphanumber as alpha
    >>> from bika.lims import api
    >>> from bika.lims import idserver
    >>> from bika.lims.interfaces import INumberGenerator
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables:

    >>> date_now = timestamp()
    >>> year = date_now.split('-')[0][2:]
    >>> sample_date = DateTime(2017, 1, 31)
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> bika_sampletypes = setup.bika_sampletypes
    >>> bika_samplepoints = setup.bika_samplepoints
    >>> bika_analysiscategories = setup.bika_analysiscategories
    >>> bika_analysisservices = setup.bika_analysisservices
    >>> bika_labcontacts = setup.bika_labcontacts
    >>> bika_storagelocations = setup.bika_storagelocations
    >>> bika_samplingdeviations = setup.bika_samplingdeviations
    >>> bika_sampleconditions = setup.bika_sampleconditions
    >>> portal_url = portal.absolute_url()
    >>> setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()
    >>> current_user = ploneapi.user.get_current()

Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


Analysis Requests (AR)
----------------------

An `AnalysisRequest` can only be created inside a `Client`:

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client
    <...client-1>

To create a new AR, a `Contact` is needed:

    >>> contact = api.create(client, "Contact", Firstname="Ramon", Surname="Bartl")
    >>> contact
    <...contact-1>

A `SampleType` defines how long the sample can be retained, the minimum volume
needed, if it is hazardous or not, the point where the sample was taken etc.:

    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="water")
    >>> sampletype
    <...sampletype-1>

A `SamplePoint` defines the location, where a `Sample` was taken:

    >>> samplepoint = api.create(bika_samplepoints, "SamplePoint", title="Lake of Constance")
    >>> samplepoint
    <...samplepoint-1>

An `AnalysisCategory` categorizes different `AnalysisServices`:

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <...analysiscategory-1>

An `AnalysisService` defines a analysis service offered by the laboratory:

    >>> analysisservice = api.create(bika_analysisservices, "AnalysisService",
    ...     title="PH", Category=analysiscategory, Keyword="PH")
    >>> analysisservice
    <...analysisservice-1>


ID generation
-------------

IDs can contain *alphanumeric* or *numeric* numbers, depending on the provided
ID Server configuration.

Set up `ID Server` configuration:

    >>> values = [
    ...            {'form': '{sampleType}-{year}-{alpha:2a3d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1},
    ...            {'form': 'BA-{year}-{seq:04d}',
    ...             'portal_type': 'Batch',
    ...             'prefix': 'batch',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1,
    ...             'value': ''},
    ...          ]

    >>> setup.setIDFormatting(values)

An `AnalysisRequest` can be created:

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype.UID(),
    ...          }

    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Sampler', 'LabClerk'])
    >>> transaction.commit()
    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId() == "water-{}-AA001".format(year)
    True

Create a second `AnalysisRequest`:

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype.UID(),
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId() == "water-{}-AA002".format(year)
    True

Create a `Batch`:

    >>> batches = self.portal.batches
    >>> batch = api.create(batches, "Batch", ClientID="RB")
    >>> batch.getId() == "BA-{}-0001".format(year)
    True

Change ID formats and create new `AnalysisRequest`:

    >>> values = [
    ...            {'form': '{clientId}-{dateSampled:%Y%m%d}-{sampleType}-{seq:04d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1},
    ...            {'form': 'BA-{year}-{seq:04d}',
    ...             'portal_type': 'Batch',
    ...             'prefix': 'batch',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1,
    ...             'value': ''},
    ...          ]

    >>> setup.setIDFormatting(values)

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype.UID(),
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'RB-20170131-water-0001'

Re-seed and create a new `Batch`:

    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Manager'])
    >>> transaction.commit()
    >>> browser.open(portal_url + '/ng_seed?prefix=batch-BA&seed=10')
    >>> batch = api.create(batches, "Batch", ClientID="RB")
    >>> batch.getId() == "BA-{}-0011".format(year)
    True

Change ID formats and use alphanumeric ids:

    >>> sampletype2 = api.create(bika_sampletypes, "SampleType", Prefix="WB")
    >>> sampletype2
    <...sampletype-2>

    >>> values = [
    ...            {'form': '{sampleType}-{alpha:3a1d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1},
    ...          ]

    >>> setup.setIDFormatting(values)
    >>> values = {'SampleType': sampletype2.UID(),}
    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'WB-AAA1'

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'WB-AAA2'

Now generate 8 more ARs to force the alpha segment to change:

    >>> for num in range(8):
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'WB-AAB1'

And try now without separators:

    >>> values = [
    ...            {'form': '{sampleType}{alpha:3a1d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 1},
    ...          ]

    >>> setup.setIDFormatting(values)
    >>> values = {'SampleType': sampletype2.UID(),}
    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)

The system continues after the previous ID, even if no separator is used:

    >>> ar.getId()
    'WBAAB2'

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'WBAAB3'

Now generate 8 more ARs to force the alpha segment to change
    >>> for num in range(8):
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'WBAAC2'

TODO: Test the case when numbers are exhausted in a sequence!


IDs with Suffix
---------------

In SENAITE < 1.3.0 it was differentiated between an *Analysis Request* and a
*Sample*. The *Analysis Request* acted as a "holder" of a *Sample* and the ID
used to be the same as the holding *Sample* but with the suffix `-R01`.

This suffix was incremented, e.g. `-R01` to `-R02`, when a retest was requested,
while keeping the ID of the previous part constant.

With SENAITE 1.3.0 there is no differentiation anymore between Analysis Request
and Sample. However, some labs might still want to follow the old ID scheme with
the suffix and incrementation of retests to keep their analysis reports in a
sane state.

Therefore, the ID Server also supports Suffixes and the logic to generated the
next suffix number for retests:


    >>> values = [
    ...            {'form': '{sampleType}-{year}-{seq:04d}-R01',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 2},
    ...            {'form': '{parent_base_id}-R{test_count:02d}',
    ...             'portal_type': 'AnalysisRequestRetest',
    ...             'prefix': 'analysisrequestretest',
    ...             'sequence_type': '',
    ...             'split_length': 1},
    ...          ]

    >>> setup.setIDFormatting(values)

Allow self-verification of results:

    >>> setup.setSelfVerificationEnabled(True)

Create a new `AnalysisRequest`:

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype.UID(),
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId() == "water-{}-0001-R01".format(year)
    True

Receive the Sample:

    >>> do_action_for(ar, "receive")[0]
    True

Submit and verify results:

    >>> an = ar.getAnalyses(full_objects=True)[0]
    >>> an.setResult(5)

    >>> do_action_for(an, "submit")[0]
    True

    >>> do_action_for(an, "verify")[0]
    True

The AR should benow in the state `verified`:

     >>> api.get_workflow_status_of(ar)
     'verified'

We can invalidate it now:

    >>> do_action_for(ar, "invalidate")[0]
    True


Now a retest was created with the same ID as the invalidated AR, but an
incremented suffix:

    >>> retest = ar.getRetest()
    >>> retest.getId() == "water-{}-0001-R02".format(year)
    True

Submit and verify results of the retest:

    >>> an = retest.getAnalyses(full_objects=True)[0]
    >>> an.setResult(5)

    >>> do_action_for(an, "submit")[0]
    True

    >>> do_action_for(an, "verify")[0]
    True

The Retest should benow in the state `verified`:

     >>> api.get_workflow_status_of(retest)
     'verified'

We can invalidate it now:

    >>> do_action_for(retest, "invalidate")[0]
    True

Now a retest of the retest was created with the same ID as the invalidated AR,
but an incremented suffix:

    >>> retest = retest.getRetest()
    >>> retest.getId() == "water-{}-0001-R03".format(year)
    True


ID Slicing
----------

The ID slicing machinery that comes with ID Server takes into consideration both
wildcards (e.g "{SampleType}") and separators (by default "-"):

    >>> id_format = "AR-{sampleType}-{parentId}{alpha:3a2d}"

If default separator "-" is used, the segments generated are:
`["AR", "{sampleType}", "{parentId}", "{alpha:3a2d}"]`

    >>> idserver.slice(id_format, separator="-", start=0, end=3)
    'AR-{sampleType}-{parentId}'

    >>> idserver.slice(id_format, separator="-", start=1, end=2)
    '{sampleType}-{parentId}'

If no separator is used, note the segments generated are like follows:
`["AR-", "{sampleType}", "-", "{parentId}", "{alpha:3a2d}"]`

    >>> idserver.slice(id_format, separator="", start=0, end=3)
    'AR-{sampleType}-'

    >>> idserver.slice(id_format, separator="", start=1, end=2)
    '{sampleType}-'

And if we use a separator other than "-", we have the same result as before:

    >>> idserver.slice(id_format, separator=".", start=0, end=3)
    'AR-{sampleType}-'

    >>> idserver.slice(id_format, separator=".", start=1, end=2)
    '{sampleType}-'

Unless we define an ID format in accordance:

    >>> id_format = "AR.{sampleType}.{parentId}{alpha:3a2d}"

So we get the same results as the beginning:

    >>> idserver.slice(id_format, separator=".", start=0, end=3)
    'AR.{sampleType}.{parentId}'

    >>> idserver.slice(id_format, separator=".", start=1, end=2)
    '{sampleType}.{parentId}'

If we define an ID format without separator, the result will always be the same
regardless of setting a separator as a parm or not:

    >>> id_format = "AR{sampleType}{parentId}{alpha:3a2d}"
    >>> idserver.slice(id_format, separator="-", start=0, end=3)
    'AR{sampleType}{parentId}'

    >>> idserver.slice(id_format, separator="", start=0, end=3)
    'AR{sampleType}{parentId}'

    >>> idserver.slice(id_format, separator="-", start=1, end=2)
    '{sampleType}{parentId}'

Try now with a simpler and quite common ID:

    >>> id_format = "WS-{seq:04d}"
    >>> idserver.slice(id_format, separator="-", start=0, end=1)
    'WS'

    >>> id_format = "WS{seq:04d}"
    >>> idserver.slice(id_format, separator="-", start=0, end=1)
    'WS'

    >>> idserver.slice(id_format, separator="", start=0, end=1)
    'WS'

Number generator storage behavior for IDs with/without separators
-----------------------------------------------------------------

Number generator machinery keeps track of the last IDs generated to:

1. Make the creation of new IDs faster. The system does not need to find out the
   last ID number generated for a given portal type by walking through all
   objects each time an object is created.

2. Allow to manually reseed the numbering through ng interface. Sometimes, the
   lab wants an ID to start from a specific number, set manually.

These last-generated IDs are stored in annotation storage.

Set up `ID Server` configuration with an hyphen separated format and create an
Analysis Request:

    >>> id_formatting = [
    ...            {'form': 'NG-{sampleType}-{alpha:2a3d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 2},
    ...          ]

    >>> setup.setIDFormatting(id_formatting)
    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': sample_date,
    ...           'DateSampled': sample_date,
    ...           'SampleType': sampletype.UID(),
    ...          }
    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'NG-water-AA001'

Check the ID was correctly seeded in storage:

    >>> number_generator = getUtility(INumberGenerator)
    >>> last_number = number_generator.get("analysisrequest-NG-water")
    >>> alpha.to_decimal('AA001') == last_number
    True

Create a new Analysis Request with same format and check again:

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'NG-water-AA002'
    >>> number_generator = getUtility(INumberGenerator)
    >>> last_number = number_generator.get("analysisrequest-NG-water")
    >>> alpha.to_decimal('AA002') == last_number
    True

Do the same, but with an ID formatting without separators:

    >>> id_formatting = [
    ...            {'form': 'NG{sampleType}{alpha:2a3d}',
    ...             'portal_type': 'AnalysisRequest',
    ...             'prefix': 'analysisrequest',
    ...             'sequence_type': 'generated',
    ...             'split_length': 2},
    ...          ]

    >>> setup.setIDFormatting(id_formatting)
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'NGwaterAA001'

Check if the ID was correctly seeded in storage:

    >>> number_generator = getUtility(INumberGenerator)
    >>> last_number = number_generator.get("analysisrequest-NGwater")
    >>> alpha.to_decimal('AA001') == last_number
    True

Create a new Analysis Request with same format and check again:

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar.getId()
    'NGwaterAA002'
    >>> number_generator = getUtility(INumberGenerator)
    >>> last_number = number_generator.get("analysisrequest-NGwater")
    >>> alpha.to_decimal('AA002') == last_number
    True
