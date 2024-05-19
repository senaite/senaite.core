Instrument Results Import
-------------------------

NOTE: This test shall supersede existing instrument interface tests!

Test Setups:

- Basic Instrument Results Import
- Basic Instrument Results Import with Interims
- Instrument Results Import for multiple Samples with Interims
- Instrument Results Import with unbalanced CSV file
- Instrument Results Import with Worksheet assigned Analyses
- Instrument Results Import with Worksheet assigned Analyses and QCs


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

Helpers:

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_sample(client, request, values, service_uids)
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

    >>> bikasetup = api.get_bika_setup()
    >>> setup = api.get_senaite_setup()

    >>> analysiscategories = bikasetup.bika_analysiscategories
    >>> analysisservices = bikasetup.bika_analysisservices
    >>> calculations = bikasetup.bika_calculations
    >>> departments = setup.departments
    >>> instruments = bikasetup.bika_instruments
    >>> labcontacts = bikasetup.bika_labcontacts
    >>> sampletypes = bikasetup.bika_sampletypes
    >>> referencedefinitions = bikasetup.bika_referencedefinitions
    >>> suppliers = bikasetup.bika_suppliers

    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

    >>> auto_import = api.get_view("auto_import_results")
    >>> resultsfolder = make_tempfolder("results")

LIMS Setup:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager",])
    >>> bikasetup.setAutoreceiveSamples(True)

Content Setup:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(suppliers, "Supplier", Name="Reference Samples Inc.")

Standard Analysis Services:

    >>> Au = api.create(analysisservices, "AnalysisService", title="Gold", Keyword="Au", Category=category)
    >>> Cu = api.create(analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category)
    >>> Fe = api.create(analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category)

Intrim Analysis Service:

    >>> int1 = {'keyword': 'int1', 'title': 'Interim 1', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> int2 = {'keyword': 'int2', 'title': 'Interim 2', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> int3 = {'keyword': 'int3', 'title': 'Interim 3', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}

    >>> Int = api.create(analysisservices, "AnalysisService", title="Interim Service", Keyword="Int", Category=category)
    >>> Int.setInterimFields([int1, int2, int3])

Reference definition for a blank:

    >>> blankdef = api.create(referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [
    ...     {"uid": Au.UID(), "result": "0", "min": "0", "max": "0"},
    ...     {"uid": Cu.UID(), "result": "0", "min": "0", "max": "0"},
    ...     {"uid": Fe.UID(), "result": "0", "min": "0", "max": "0"},
    ... ]
    >>> blankdef.setReferenceResults(blank_refs)

Reference definition for a control:

    >>> controldef = api.create(referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [
    ...     {"uid": Au.UID(), "result": "10", "min": "9", "max": "11"},
    ...     {"uid": Cu.UID(), "result": "10", "min": "9", "max": "11"},
    ...     {"uid": Fe.UID(), "result": "10", "min": "9", "max": "11"},
    ... ]
    >>> controldef.setReferenceResults(control_refs)

Reference Samples:

    >>> blank = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blankdef,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)

    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=controldef,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)



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


Basic Instrument Results Import
...............................

Add a new sample:

    >>> sample = new_sample([Au, Cu, Fe], client, contact, sampletype)

New samples should be automatically received:

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

Run the auto import:

    >>> import_log = auto_import()

    >>> sample.Au.getResult()
    '3.0'
    >>> sample.Fe.getResult()
    '2.0'
    >>> sample.Cu.getResult()
    '1.0'


Basic Instrument Results Import with Interims
.............................................

Add a new sample:

    >>> sample = new_sample([Int], client, contact, sampletype)

Setup the import file:

    >>> data = """
    ... ID,Int,int1,int2,int3,end
    ... {},1,10,20,30,end
    ... """.strip().format(sample.getId())

    >>> with open(os.path.join(resultsfolder, "import2.csv"), "w") as f:
    ...     f.write(data)

Run the auto import:

    >>> import_log = auto_import()

    >>> sample.Int.getResult()
    '1.0'
    >>> sample.Int.getInterimValue("int1")
    '10'
    >>> sample.Int.getInterimValue("int2")
    '20'
    >>> sample.Int.getInterimValue("int3")
    '30'


Instrument Results Import for multiple Samples with Interims
............................................................

Create new samples:

    >>> sample1 = new_sample([Au,Cu,Fe,Int], client, contact, sampletype)
    >>> sample2 = new_sample([Au,Int], client, contact, sampletype)

Setup the import file:

    >>> data = """
    ... ID,Au,Cu,Fe,Int,int1,int2,int3,end
    ... {},1,1,1,1,10,10,10,end
    ... {},2,,,2,20,20,20,end
    ... """.strip().format(sample1.getId(), sample2.getId())

    >>> with open(os.path.join(resultsfolder, "import3.csv"), "w") as f:
    ...     f.write(data)

Run the auto import:

    >>> import_log = auto_import()

Test the results of the first sample:

    >>> sample1.Au.getResult()
    '1.0'
    >>> sample1.Cu.getResult()
    '1.0'
    >>> sample1.Fe.getResult()
    '1.0'
    >>> sample1.Int.getResult()
    '1.0'
    >>> sample1.Int.getInterimValue("int1")
    '10'
    >>> sample1.Int.getInterimValue("int2")
    '10'
    >>> sample1.Int.getInterimValue("int3")
    '10'

Test the results of the second sample:

    >>> sample2.Au.getResult()
    '2.0'
    >>> sample2.Int.getInterimValue("int1")
    '20'
    >>> sample2.Int.getInterimValue("int2")
    '20'
    >>> sample2.Int.getInterimValue("int3")
    '20'


Instrument Results Import with unbalanced CSV file
..................................................

Create new samples:

    >>> sample1 = new_sample([Au], client, contact, sampletype)
    >>> sample2 = new_sample([Au], client, contact, sampletype)

Setup the import file:

    >>> data = """
    ... ID, Au, end
    ... {}, 1, end
    ... {}, 2, 3, end
    ... """.strip().format(sample1.getId(), sample2.getId())

    >>> with open(os.path.join(resultsfolder, "import4.csv"), "w") as f:
    ...     f.write(data)

Run the auto import:

    >>> import_log = auto_import()

Test the results:

    >>> sample1.Au.getResult()
    '1.0'

    >>> sample2.Au.getResult()
    '2.0'


Instrument Results Import with Worksheet assigned Analyses
..........................................................

Create new samples:

    >>> sample1 = new_sample([Au], client, contact, sampletype)
    >>> sample2 = new_sample([Au], client, contact, sampletype)

Create a new Worksheet and add the analyses of the two samples:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

    >>> worksheet
    <Worksheet at .../worksheets/WS-001>

    >>> worksheet.addAnalyses(sample1.getAnalyses())
    >>> worksheet.addAnalyses(sample2.getAnalyses())

Setup the import file:

    >>> data = """
    ... ID,Au,end
    ... {},1,end
    ... {},2,end
    ... """.strip().format(sample1.getId(), sample2.getId())

    >>> with open(os.path.join(resultsfolder, "import5.csv"), "w") as f:
    ...     f.write(data)

Run the auto import:

    >>> import_log = auto_import()

Test the results:

    >>> sample1.Au.getResult()
    '1.0'

    >>> sample2.Au.getResult()
    '2.0'

The import CSV file should be attached to each analysis:

    >>> sample1.Au.getAttachment()[0].getFilename()
    'import5.csv'

    >>> print(sample1.Au.getAttachment()[0].getAttachmentFile().data)
    ID,Au,end
    W-0007,1,end
    W-0008,2,end


Instrument Results Import with Worksheet assigned Analyses and QCs
..................................................................

Create new samples:

    >>> sample1 = new_sample([Au], client, contact, sampletype)
    >>> sample2 = new_sample([Au], client, contact, sampletype)

Create a new Worksheet and add the analyses of the two samples:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

    >>> worksheet.addAnalyses(sample1.getAnalyses())
    >>> worksheet.addAnalyses(sample2.getAnalyses())

Add a blank and a control to the worksheet:

    >>> blank = worksheet.addReferenceAnalyses(blank, [Au.UID()])[0]
    >>> control = worksheet.addReferenceAnalyses(control, [Au.UID()])[0]

Chekc if the reference samples are added:

    >>> worksheet.getReferenceAnalyses()
    [<ReferenceAnalysis at .../supplier-1/QC-001/Au>, <ReferenceAnalysis at .../supplier-1/QC-002/Au>]

Setup the import file:

    >>> data = """
    ... ID,Au,end
    ... {},1,end
    ... {},2,end
    ... {},0,end
    ... {},10,end
    ... """.strip().format(sample1.getId(), sample2.getId(), blank.getReferenceAnalysesGroupID(), control.getReferenceAnalysesGroupID())

    >>> with open(os.path.join(resultsfolder, "import6.csv"), "w") as f:
    ...     f.write(data)

Run the auto import:

    >>> import_log = auto_import()

Test the results:

    >>> sample1.Au.getResult()
    '1.0'

    >>> sample2.Au.getResult()
    '2.0'

    >>> blank.getResult()
    '0.0'

    >>> control.getResult()
    '10.0'
