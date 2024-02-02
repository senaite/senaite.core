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
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


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

Calling the 'auto_import_results' view should work:

    >>> view = api.get_view("auto_import_results")
    >>> print view()
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
    ...     f.write("SampleID,Cu,Fe,Au,end\n")
    ...     f.write("%s,1,2,3,end\n" % sample.getId())

Run the import view again:

    >>> view = api.get_view("auto_import_results")
    >>> log = view()

    >>> api.get_workflow_status_of(sample)
    'to_be_verified'

    >>> sample.Au.getResult()
    '3.0'
    >>> sample.Fe.getResult()
    '2.0'
    >>> sample.Cu.getResult()
    '1.0'

Autologs should be created:

    >>> autolog = instrument.objectValues("AutoImportLog")[0] 
    >>> print autolog.getResults()
    2... [INFO] Parsing file .../results/import1.csv
    2... [INFO] End of file reached successfully: 1 objects, 3 analyses, 3 results
    2... [INFO] Allowed Sample states: sample_received, to_be_verified
    2... [INFO] Allowed analysis states: unassigned, assigned, to_be_verified
    2... [INFO] W-0001 result for 'Cu': '1.0'
    2... [INFO] W-0001 result for 'Fe': '2.0'
    2... [INFO] W-0001 result for 'Au': '3.0'
    2... [INFO] W-0001: Analysis Cu, Fe, Au imported sucessfully
    2... [INFO] Import finished successfully: 1 Samples, 0 Instruments and 3 results updated

    >>> autolog.getInterface()
    'generic.two_dimension'

    >>> autolog.getImportFile()
    'import1.csv'
