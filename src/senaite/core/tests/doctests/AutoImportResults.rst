Auto Import Instrument Results
------------------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t AutoImportResults

Test Setup
..........

Needed Imports:

    >>> import os
    >>> import shutil
    >>> import tempfile
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from DateTime import DateTime
    >>> from plone.app.testing import login
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

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
    ...     transitioned = do_action_for(sample, "receive")
    ...     return sample

    >>> def try_transition(object, transition_id, target_state_id):
    ...     success = do_action_for(object, transition_id)[0]
    ...     state = api.get_workflow_status_of(object)
    ...     return success and state == target_state_id

    >>> def make_tempfolder(name):
    ...     tmpdir = tempfile.gettempdir()
    ...     folder = os.path.join(tmpdir, name)
    ...     if os.path.exists(folder):
    ...         shutil.rmtree(folder)
    ...     os.mkdir(folder)
    ...     return folder

    >>> def auto_import(user):
    ...     current_user = api.user.get_user()
    ...     login(portal, user)
    ...     view = api.get_view("auto_import_results")
    ...     out = view()
    ...     login(portal, current_user.getUserName())
    ...     return out

    >>> def auto_import_with_override(user, override_non_empty=0,
    ...                               override_with_empty=0):
    ...     current_user = api.user.get_user()
    ...     login(portal, user)
    ...     request.set("override_non_empty", str(override_non_empty))
    ...     request.set("override_with_empty", str(override_with_empty))
    ...     view = api.get_view("auto_import_results")
    ...     out = view()
    ...     request.set("override_non_empty", "0")
    ...     request.set("override_with_empty", "0")
    ...     login(portal, current_user.getUserName())
    ...     return out


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> resultsfolder = make_tempfolder("results")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", SortKey="1", Category=category.UID())
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", SortKey="2", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", SortKey="3", Category=category.UID())

Add an `analyst` test user:

    >>> pm = api.get_tool("portal_membership")
    >>> pm.addMember("analyst", "analyst", ["Analyst"], [])


Setup the LIMS for automatic result imports
...........................................

Setup an instrument with an import interface:

    >>> instrument = api.create(bikasetup.bika_instruments, "Instrument", title="Test Instrument")
    >>> instrument
    <Instrument at /plone/bika_setup/bika_instruments/instrument-1>
    >>> instrument.setImportDataInterface(["generic.two_dimension"])
    >>> instrument.setResultFilesFolder({"InterfaceName": "generic.two_dimension", "Folder": resultsfolder})
    >>> instrument.getImportDataInterface()
    ['generic.two_dimension']

Calling the 'auto_import_results' view should work as `Anlyst` user:

    >>> print(auto_import("analyst"))
    2... [INFO] [Instrument:Test Instrument] Auto import for Test Instrument started ...
    2... [INFO] Auto-Import finished


Create a sample for results import:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> sample
    <AnalysisRequest at /plone/clients/client-1/W-0001>

    >>> api.get_workflow_status_of(sample)
    'sample_received'

Now create an instrument results file:

    >>> with open(os.path.join(resultsfolder, "import1.csv"), "w") as f:
    ...     f.write("SampleID,Au,Cu,Fe,end\n")
    ...     f.write("%s,1,2,3,end\n" % sample.getId())

Run the import view again:

    >>> log = auto_import("analyst")

    >>> api.get_workflow_status_of(sample)
    'to_be_verified'

    >>> sample.Au.getResult()
    '1.0'
    >>> sample.Cu.getResult()
    '2.0'
    >>> sample.Fe.getResult()
    '3.0'

Autologs should be created:

    >>> autolog = instrument.objectValues("AutoImportLog")[0] 
    >>> print autolog.getResults()
    2... [INFO] Parsing file .../results/import1.csv
    2... [INFO] End of file reached successfully: 1 objects, 3 analyses, 3 results
    2... [INFO] Allowed sample states: sample_received, to_be_verified
    2... [INFO] Allowed analysis states: unassigned, assigned, to_be_verified
    2... [INFO] Don't override analysis results
    2... [INFO] W-0001 result for 'Au': '1.0'
    2... [INFO] W-0001 result for 'Cu': '2.0'
    2... [INFO] W-0001 result for 'Fe': '3.0'
    2... [INFO] W-0001: Analysis Au, Cu, Fe imported sucessfully
    2... [INFO] Import finished successfully: 1 Samples and 3 results updated

    >>> autolog.getInterface()
    'generic.two_dimension'

    >>> autolog.getImportFile()
    'import1.csv'


Test import with interims
.........................

Set interims to the analysis `Au`:

    >>> Au.setInterimFields([
    ...     {"keyword": "interim_1", "title": "Interim 1",},
    ...     {"keyword": "interim_2", "title": "Interim 2",}])

Create a new sample for results import:

    >>> sample2 = new_sample([Cu, Fe, Au])
    >>> sample2
    <AnalysisRequest at /plone/clients/client-1/W-0002>

    >>> api.get_workflow_status_of(sample2)
    'sample_received'

Create a new instrument results file:

    >>> with open(os.path.join(resultsfolder, "import2.csv"), "w") as f:
    ...     f.write("SampleID,Au,interim_1,interim_2\n")
    ...     f.write("%s,10,100,1000\n" % sample2.getId())

Run the import view again:

    >>> log = auto_import("analyst")

    >>> sample2.Au.getResult()
    '10.0'

Check if the interims were imported correctly:

    >>> sample2.Au.getInterimValue("interim_1")
    '100'
    >>> sample2.Au.getInterimValue("interim_2")
    '1000'

Autologs should be created:

    >>> autolog = instrument.objectValues("AutoImportLog")[1]
    >>> print autolog.getResults()
    2... [INFO] Parsing file .../results/import2.csv
    2... [INFO] End of file reached successfully: 1 objects, 1 analyses, 1 results
    2... [INFO] Allowed sample states: sample_received, to_be_verified
    2... [INFO] Allowed analysis states: unassigned, assigned, to_be_verified
    2... [INFO] Don't override analysis results
    2... [INFO] W-0002 result for 'Au:interim_1': '100'
    2... [INFO] W-0002 result for 'Au:interim_2': '1000'
    2... [INFO] W-0002 result for 'Au': '10.0'
    2... [INFO] W-0002: Analysis Au imported sucessfully
    2... [INFO] Import finished successfully: 1 Samples and 1 results updated


Test import of string restuls
.............................

Set analysis `Au` as string result:

    >>> Au.setStringResult(True)

Allow manual detection limit to enter "<" and ">" results:

    >>> Cu.setAllowManualDetectionLimit(True)
    >>> Fe.setAllowManualDetectionLimit(True)

Create a new sample for results import:

    >>> sample3 = new_sample([Cu, Fe, Au])
    >>> sample3
    <AnalysisRequest at /plone/clients/client-1/W-0003>

    >>> api.get_workflow_status_of(sample3)
    'sample_received'

Create a new instrument results file:

    >>> with open(os.path.join(resultsfolder, "import3.csv"), "w") as f:
    ...     f.write("SampleID,Au,Cu,Fe\n")
    ...     f.write('%s,"Found","<1",">2"\n' % sample3.getId())

Run the import view again:

    >>> log = auto_import("analyst")

    >>> sample3.Au.getFormattedResult()
    'Found'
    >>> sample3.Cu.getFormattedResult()
    '&lt; 1'
    >>> sample3.Fe.getFormattedResult()
    '&gt; 2'

Autologs should be created:

    >>> autolog = instrument.objectValues("AutoImportLog")[2]
    >>> print autolog.getResults()
    2... [INFO] Parsing file .../results/import3.csv
    2... [INFO] End of file reached successfully: 1 objects, 3 analyses, 3 results
    2... [INFO] Allowed sample states: sample_received, to_be_verified
    2... [INFO] Allowed analysis states: unassigned, assigned, to_be_verified
    2... [INFO] Don't override analysis results
    2... [INFO] W-0003 result for 'Au': 'Found'
    2... [INFO] W-0003 result for 'Cu': '<1'
    2... [INFO] W-0003 result for 'Fe': '>2'
    2... [INFO] W-0003: Analysis Au, Cu, Fe imported sucessfully
    2... [INFO] Import finished successfully: 1 Samples and 3 results updated


Test import of result options
.............................

Let's add some results options to service `Fe`:

    >>> results_options = [
    ...     {"ResultValue": "1", "ResultText": "Number 1"},
    ...     {"ResultValue": "2", "ResultText": "Number 2"},
    ...     {"ResultValue": "3", "ResultText": "Number 3"}]

    >>> Cu.setResultOptions(results_options)
    >>> Cu.setResultType("select")

    >>> Fe.setResultOptions(results_options)
    >>> Fe.setResultType("select")


Create a new sample for results import:

    >>> sample4 = new_sample([Cu, Fe, Au])
    >>> sample4
    <AnalysisRequest at /plone/clients/client-1/W-0004>

    >>> api.get_workflow_status_of(sample3)
    'sample_received'

Create a new instrument results file:

    >>> with open(os.path.join(resultsfolder, "import4.csv"), "w") as f:
    ...     f.write("SampleID,Au,Cu,Fe\n")
    ...     f.write('%s,"Found",1,2.0\n' % sample4.getId())

Run the import view again:

    >>> log = auto_import("analyst")

    >>> sample4.Au.getFormattedResult()
    'Found'
    >>> sample4.Cu.getFormattedResult()
    'Number 1'
    >>> sample4.Fe.getFormattedResult()
    'Number 2'

Autologs should be created:

    >>> autolog = instrument.objectValues("AutoImportLog")[3]
    >>> print autolog.getResults()
    2... Parsing file .../results/import4.csv
    2... End of file reached successfully: 1 objects, 3 analyses, 3 results
    2... Allowed sample states: sample_received, to_be_verified
    2... Allowed analysis states: unassigned, assigned, to_be_verified
    2... Don't override analysis results
    2... W-0004 result for 'Au': 'Found'
    2... W-0004 result for 'Cu': '1'
    2... W-0004 result for 'Fe': '2'
    2... W-0004: Analysis Au, Cu, Fe imported sucessfully
    2... Import finished successfully: 1 Samples and 3 results updated


Test override settings via request parameters
.............................................

Reset ``Au`` to numeric result type so the results are floatable:

    >>> Au.setStringResult(False)

Create a new sample and import results to give it existing values:

    >>> sample5 = new_sample([Au])
    >>> sample5
    <AnalysisRequest at /plone/clients/client-1/W-0005>

    >>> with open(os.path.join(resultsfolder, "import5.csv"), "w") as f:
    ...     f.write("SampleID,Au\n")
    ...     f.write("%s,99\n" % sample5.getId())

    >>> log = auto_import("analyst")
    >>> sample5.Au.getResult()
    '99.0'

By default the import does not override already set results. Create a new
results file for the same sample with a different value:

    >>> with open(os.path.join(resultsfolder, "import6.csv"), "w") as f:
    ...     f.write("SampleID,Au\n")
    ...     f.write("%s,88\n" % sample5.getId())

Default import (no override flags) keeps the existing result:

    >>> log = auto_import("analyst")
    >>> sample5.Au.getResult()
    '99.0'

The log reports that the existing result was kept:

    >>> "kept due to the selected override option" in log
    True

Now import with ``override_non_empty=1`` — the existing result should be
overwritten:

    >>> with open(os.path.join(resultsfolder, "import7.csv"), "w") as f:
    ...     f.write("SampleID,Au\n")
    ...     f.write("%s,77\n" % sample5.getId())

    >>> log = auto_import_with_override("analyst", override_non_empty=1)
    >>> sample5.Au.getResult()
    '77.0'

The log confirms the override setting was active:

    >>> autolog = instrument.objectValues("AutoImportLog")[-1]
    >>> print autolog.getResults()
    2... [INFO] Parsing file .../results/import7.csv
    2... [INFO] End of file reached successfully: 1 objects, 1 analyses, 1 results
    2... [INFO] Allowed sample states: sample_received, to_be_verified
    2... [INFO] Allowed analysis states: unassigned, assigned, to_be_verified
    2... [INFO] Override non-empty analysis results
    2... [INFO] W-0005 result for 'Au': '77.0'
    2... [INFO] W-0005: Analysis Au imported sucessfully
    2... [INFO] Import finished successfully: 1 Samples and 1 results updated
