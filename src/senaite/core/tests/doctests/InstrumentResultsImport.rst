Instrument Results Import
-------------------------

NOTE: This test shall supersede existing instrument interface tests!

What is tested:

- Basic results import
- Basic results import with interim fields
- Instrument calibration imports

Running this test from the buildout directory:

    bin/test test_textual_doctests -t InstrumentResultsImport


Test Setup
..........

Imports:

    >>> import os
    >>> import shutil
    >>> import tempfile

    >>> from bika.lims import api
    >>> from DateTime import DateTime
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest as create_sample

    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD


Helper Functions

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_sample(client, request, values, service_uids)
    ...     transitioned = api.do_transition_for(sample, "receive")
    ...     return sample

    >>> def get_analysis_from(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None


    >>> def make_tempfolder(name):
    ...     tmpdir = tempfile.gettempdir()
    ...     folder = os.path.join(tmpdir, name)
    ...     if os.path.exists(folder):
    ...         shutil.rmtree(folder)
    ...     os.mkdir(folder)
    ...     return folder

Variables:

    >>> portal = api.get_portal()
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bikasetup = api.get_bika_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> resultsfolder = make_tempfolder("results")
    >>> sampletypes = bikasetup.bika_sampletypes
    >>> labcontacts = bikasetup.bika_labcontacts
    >>> departments = setup.departments
    >>> analysiscategories = bikasetup.bika_analysiscategories
    >>> analysisservices = bikasetup.bika_analysisservices
    >>> instruments = bikasetup.bika_instruments

LIMS Setup:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager",])

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(analysiscategories, "AnalysisCategory", title="Metals", Department=department)

    >>> Cu = api.create(analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category)
    >>> Fe = api.create(analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category)
    >>> Au = api.create(analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category)

    >>> auto_import = api.get_view("auto_import_results")


Instrument Setup
................

Prepare a new basic instrument:

    >>> instrument = api.create(instruments, "Instrument", title="Basic Instrument")
    >>> instrument
    <Instrument at .../instrument-1>

Configure the 2D-CSV import interface:

    >>> instrument.setImportDataInterface(["generic.two_dimension"])
    >>> instrument.getImportDataInterface()
    ['generic.two_dimension']

Allow automatic imports from the import folder:

    >>> instrument.setResultFilesFolder({"InterfaceName": "generic.two_dimension", "Folder": resultsfolder})


Basic Instrument 2D-CSV Results Import
......................................

Setup a basic instrument:


Add a new sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)

    >>> sample
    <AnalysisRequest at /plone/clients/client-1/W-0001>

    >>> api.get_workflow_status_of(sample)
    'sample_received'


Setup the import file:

    >>> data = """
    ... ID,Cu,Fe,Au,end
    ... {},1,2,3,end
    ... """.strip().format(sample.getId())

    >>> with open(os.path.join(resultsfolder, "import1.csv"), "w") as f:
    ...     f.write(data)

Run the auto import view:

    >>> import_log = auto_import()

    >>> sample.Au.getResult()
    '3.0'
    >>> sample.Fe.getResult()
    '2.0'
    >>> sample.Cu.getResult()
    '1.0'
