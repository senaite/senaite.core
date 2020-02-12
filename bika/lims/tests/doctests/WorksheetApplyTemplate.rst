====================================
Worksheet - Apply Worksheet Template
====================================

Worksheets are the main artifact for planning tests in the laboratory. They are
also used to add reference samples (controls and blancs), duplicates and
aggregate related tests from different Analysis Requests to be processed in a
single run.

Although worksheets can be created manually by the labmanager each time is
required, a better approach is to create them by using Worksheet Templates. In a
Worksheet Template, the labman defines the layout, the number of slots and the
type of analyses (reference or routine) to be placed in each slot, as well as
the Method and Instrument to be assigned. Thus, Worksheet Templates are used for
the semi-automated creation of Worksheets.

This doctest will validate the consistency between the Worksheet and the
Worksheet Template used for its creation. It will also test the correctness of
the worksheet when applying a Worksheet Template in a manually created
Worksheet.


Test Setup
==========

Running this test from the buildout directory:

    bin/test -t WorksheetApplyTemplate

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(bikasetup.bika_suppliers, "Supplier", Name="Naralabs")
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())

Create some Analysis Requests, so we can use them as sources for Worksheet cration:

    >>> values = {
    ...     'Client': client.UID(),
    ...     'Contact': contact.UID(),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype.UID()}
    >>> service_uids = [Cu.UID(), Fe.UID(), Au.UID()]
    >>> ar0 = create_analysisrequest(client, request, values, service_uids)
    >>> ar1 = create_analysisrequest(client, request, values, service_uids)
    >>> ar2 = create_analysisrequest(client, request, values, service_uids)
    >>> ar3 = create_analysisrequest(client, request, values, service_uids)
    >>> ar4 = create_analysisrequest(client, request, values, service_uids)
    >>> ar5 = create_analysisrequest(client, request, values, service_uids)
    >>> ar6 = create_analysisrequest(client, request, values, service_uids)
    >>> ar7 = create_analysisrequest(client, request, values, service_uids)
    >>> ar8 = create_analysisrequest(client, request, values, service_uids)
    >>> ar9 = create_analysisrequest(client, request, values, service_uids)


Worksheet Template creation
---------------------------

Create a Worksheet Template, but for `Cu` and `Fe` analyses, with the following
layout with 7 slots:

  * Routine analyses in slots 1, 2, 4
  * Duplicate analysis from slot 1 in slot 3
  * Duplicate analysis from slot 4 in slot 5
  * Control analysis in slot 6
  * Blank analysis in slot 7

    >>> service_uids = [Cu.UID(), Fe.UID()]
    >>> layout = [
    ...     {'pos': '1', 'type': 'a',
    ...      'blank_ref': '',
    ...      'control_ref': '',
    ...      'dup': ''},
    ...     {'pos': '2', 'type': 'a',
    ...      'blank_ref': '',
    ...      'control_ref': '',
    ...      'dup': ''},
    ...     {'pos': '3', 'type': 'd',
    ...      'blank_ref': '',
    ...      'control_ref': '',
    ...      'dup': '1'},
    ...     {'pos': '4', 'type': 'a',
    ...      'blank_ref': '',
    ...      'control_ref': '',
    ...      'dup': ''},
    ...     {'pos': '5', 'type': 'd',
    ...      'blank_ref': '',
    ...      'control_ref': '',
    ...      'dup': '4'},
    ...     {'pos': '6', 'type': 'c',
    ...      'blank_ref': '',
    ...      'control_ref': 'jajsjas',
    ...      'dup': ''},
    ...     {'pos': '7', 'type': 'b',
    ...      'blank_ref': 'asasasa',
    ...      'control_ref': '',
    ...      'dup': ''},
    ... ]
    >>> template = api.create(bikasetup.bika_worksheettemplates, "WorksheetTemplate", title="WS Template Test", Layout=layout, Service=service_uids)


Apply Worksheet Template to a Worksheet
=======================================

Create a new Worksheet by using this worksheet template:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.applyWorksheetTemplate(template)

Since we haven't received any analysis requests, this worksheet remains empty:

    >>> worksheet.getAnalyses()
    []
    >>> worksheet.getLayout()
    []

Receive the Analysis Requests and apply again the Worksheet Template:

    >>> performed = doActionFor(ar0, 'receive')
    >>> performed = doActionFor(ar1, 'receive')
    >>> performed = doActionFor(ar2, 'receive')
    >>> performed = doActionFor(ar3, 'receive')
    >>> performed = doActionFor(ar4, 'receive')
    >>> performed = doActionFor(ar5, 'receive')
    >>> performed = doActionFor(ar6, 'receive')
    >>> performed = doActionFor(ar7, 'receive')
    >>> performed = doActionFor(ar8, 'receive')
    >>> performed = doActionFor(ar9, 'receive')
    >>> worksheet.applyWorksheetTemplate(template)

Slots 1, 2 and 4 are filled with routine analyses:

    >>> worksheet.get_slot_positions(type='a')
    [1, 2, 4]

Each slot occupied by routine analyses is assigned to an Analysis Request, so
each time we add an analysis, it will be added into it's corresponding slot:

    >>> container = worksheet.get_container_at(1)
    >>> container.UID() == ar0.UID()
    True

    >>> slot1_analyses = worksheet.get_analyses_at(1)
    >>> an_ar = list(set([an.getRequestUID() for an in slot1_analyses]))

    >>> len(an_ar) == 1
    True

    >>> an_ar[0] == ar0.UID()
    True

    >>> [an.getKeyword() for an in slot1_analyses]
    ['Cu', 'Fe']

Slots 3 and 5 are filled with duplicate analyses:

    >>> worksheet.get_slot_positions(type='d')
    [3, 5]

    >>> dup1 = worksheet.get_analyses_at(3)
    >>> len(dup1) == 2
    True

    >>> list(set([dup.portal_type for dup in dup1]))
    ['DuplicateAnalysis']

The first duplicate analysis located at slot 3 is a duplicate of the first
analysis from slot 1:

    >>> dup_an = dup1[0].getAnalysis()
    >>> slot1_analyses[0].UID() == dup_an.UID()
    True

But since we haven't created any reference analysis (neither blank or control),
slots reserved for blank and controls are not occupied:

    >>> worksheet.get_slot_positions(type='c')
    []
    >>> worksheet.get_slot_positions(type='b')
    []


Remove analyses and Apply Worksheet Template again
==================================================

Remove analyses located at position 2:

    >>> to_del = worksheet.get_analyses_at(2)
    >>> worksheet.removeAnalysis(to_del[0])
    >>> worksheet.removeAnalysis(to_del[1])

Only slots 1, 4 are filled with routine analyses now:

    >>> worksheet.get_slot_positions(type='a')
    [1, 4]

Modify the Worksheet Template to allow `Au` analysis and apply the template to the
same Worksheet again:

    >>> service_uids = [Cu.UID(), Fe.UID(), Au.UID()]
    >>> template.setService(service_uids)
    >>> worksheet.applyWorksheetTemplate(template)

Now, slot 2 is filled again:

    >>> worksheet.get_slot_positions(type='a')
    [1, 2, 4]

And each slot contains the additional analysis `Au`:

    >>> slot1_analyses = worksheet.get_analyses_at(1)
    >>> len(slot1_analyses) == 3
    True

    >>> an_ar = list(set([an.getRequestUID() for an in slot1_analyses]))
    >>> an_ar[0] == ar0.UID()
    True

    >>> [an.getKeyword() for an in slot1_analyses]
    ['Cu', 'Fe', 'Au']

As well as in duplicate analyses:

    >>> dup1 = worksheet.get_analyses_at(3)
    >>> len(dup1) == 3
    True

    >>> slot3_analyses = worksheet.get_analyses_at(3)
    >>> [an.getKeyword() for an in slot3_analyses]
    ['Cu', 'Fe', 'Au']


Remove a duplicate and add it manually
======================================

Remove all duplicate analyses from slot 5:

    >>> dup5 = worksheet.get_analyses_at(5)
    >>> len(dup5) == 3
    True

    >>> worksheet.removeAnalysis(dup5[0])
    >>> worksheet.removeAnalysis(dup5[1])
    >>> worksheet.removeAnalysis(dup5[2])
    >>> dup5 = worksheet.get_analyses_at(5)
    >>> len(dup5) == 0
    True

Add duplicates using the same source routine analysis, located at slot 4, but
manually instead of applying the Worksheet Template:

    >>> dups = worksheet.addDuplicateAnalyses(4)

Three duplicate have been added to the worksheet:

    >>> [dup.getKeyword() for dup in dups]
    ['Cu', 'Fe', 'Au']

And these duplicates have been added in the slot number 5, cause this slot is
where this duplicate fits better in accordance with the layout defined in the
worksheet template associated to this worksheet:

    >>> dup5 = worksheet.get_analyses_at(5)
    >>> [dup.getKeyword() for dup in dup5]
    ['Cu', 'Fe', 'Au']

    >>> dups_uids = [dup.UID() for dup in dups]
    >>> dup5_uids = [dup.UID() for dup in dup5]
    >>> [dup for dup in dup5_uids if dup not in dups_uids]
    []

But if we remove only one duplicate analysis from slot number 5:

    >>> worksheet.removeAnalysis(dup5[0])
    >>> dup5 = worksheet.get_analyses_at(5)
    >>> [dup.getKeyword() for dup in dup5]
    ['Fe', 'Au']

And we manually add duplicates for analysis in position 4, a new slot will be
added at the end of the worksheet (slot number 8), cause the slot number 5 is
already occupied and slots 6 and 7, although empty, are reserved for blank and
control:

    >>> worksheet.get_analyses_at(8)
    []

    >>> dups = worksheet.addDuplicateAnalyses(4)
    >>> [dup.getKeyword() for dup in dups]
    ['Cu', 'Fe', 'Au']

    >>> dup8 = worksheet.get_analyses_at(8)
    >>> [dup.getKeyword() for dup in dup8]
    ['Cu', 'Fe', 'Au']

    >>> dups_uids = [dup.UID() for dup in dups]
    >>> dup8_uids = [dup.UID() for dup in dup8]
    >>> [dup for dup in dup8_uids if dup not in dups_uids]
    []


Control and blanks with Worksheet Template
==========================================

First, create a Reference Definition for blank:

    >>> blankdef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [{'uid': Cu.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},
    ...               {'uid': Fe.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},]
    >>> blankdef.setReferenceResults(blank_refs)

And for control:

    >>> controldef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': Cu.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'},
    ...                 {'uid': Fe.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'},]
    >>> controldef.setReferenceResults(control_refs)

Then, we create the associated Reference Samples:

    >>> blank = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blankdef,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)
    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=controldef,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)

Apply the blank and control to the Worksheet Template layout:

    >>> layout = template.getLayout()
    >>> layout[5] = {'pos': '6', 'type': 'c',
    ...              'blank_ref': '',
    ...              'control_ref': controldef.UID(),
    ...              'dup': ''}
    >>> layout[6] = {'pos': '7', 'type': 'b',
    ...              'blank_ref': blankdef.UID(),
    ...              'control_ref': '',
    ...              'dup': ''}
    >>> template.setLayout(layout)

Apply the worksheet template again:

    >>> worksheet.applyWorksheetTemplate(template)

Blank analyses at slot number 7, but note the reference definition is only for
analyses `Cu` and `Fe`:

    >>> ans = worksheet.get_analyses_at(7)
    >>> [an.getKeyword() for an in ans]
    ['Cu', 'Fe']
    >>> list(set([an.getReferenceType() for an in ans]))
    ['b']

Control analyses at slot number 6:

    >>> ans = worksheet.get_analyses_at(6)
    >>> [an.getKeyword() for an in ans]
    ['Cu', 'Fe']
    >>> list(set([an.getReferenceType() for an in ans]))
    ['c']


Remove Reference Analyses and add them manually
===============================================

Remove all controls from slot 6:

    >>> ans6 = worksheet.get_analyses_at(6)
    >>> len(ans6)
    2

    >>> worksheet.removeAnalysis(ans6[0])
    >>> worksheet.removeAnalysis(ans6[1])
    >>> worksheet.get_analyses_at(6)
    []

Add a reference analysis, but manually:

    >>> ref_ans = worksheet.addReferenceAnalyses(control, [Fe.UID(), Cu.UID()])
    >>> [ref.getKeyword() for ref in ref_ans]
    ['Cu', 'Fe']

These reference analyses have been added in the slot number 6, cause this slot
is where these reference analyses fit better in accordance with the layout
defined in the worksheet template associated to this worksheet:

    >>> ref6 = worksheet.get_analyses_at(6)
    >>> [ref.getKeyword() for ref in ref6]
    ['Cu', 'Fe']

    >>> refs_uids = [ref.UID() for ref in ref_ans]
    >>> ref6_uids = [ref.UID() for ref in ref6]
    >>> [ref for ref in ref6_uids if ref not in refs_uids]
    []

But if we remove only one reference analysis from slot number 6:

    >>> worksheet.removeAnalysis(ref6[0])
    >>> ref6 = worksheet.get_analyses_at(6)
    >>> [ref.getKeyword() for ref in ref6]
    ['Fe']

And we manually add references, a new slot will be added at the end of the
worksheet (slot number 8), cause the slot number 6 is already occupied, as well
as the rest of the slots:

    >>> worksheet.get_analyses_at(9)
    []

    >>> ref_ans = worksheet.addReferenceAnalyses(control, [Fe.UID(), Cu.UID()])
    >>> [ref.getKeyword() for ref in ref_ans]
    ['Cu', 'Fe']

    >>> ref9 = worksheet.get_analyses_at(9)
    >>> [ref.getKeyword() for ref in ref9]
    ['Cu', 'Fe']

    >>> refs_uids = [ref.UID() for ref in ref_ans]
    >>> ref9_uids = [ref.UID() for ref in ref9]
    >>> [ref for ref in ref9_uids if ref not in refs_uids]
    []
