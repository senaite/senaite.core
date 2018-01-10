Abbott's m2000 Real Time import interface
=========================================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AbbottM2000rtImportInterface


Test Setup
----------
Needed imports::

    >>> import os
    >>> import transaction
    >>> from Products.CMFCore.utils import getToolByName
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime

    >>> import codecs
    >>> from bika.lims.exportimport import instruments
    >>> from bika.lims.exportimport.instruments.abbott.m2000rt.m2000rt \
    ...      import Abbottm2000rtTSVParser, Abbottm2000rtImporter
    >>> from bika.lims.browser.resultsimport.resultsimport import ConvertToUploadFile

Functional helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_instruments = bika_setup.bika_instruments
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

Availability of instrument interface
------------------------------------
Check that the instrument interface is available::

    >>> exims = []
    >>> for exim_id in instruments.__all__:
    ...     exims.append(exim_id)
    >>> 'abbott.m2000rt.m2000rt' in exims
    True

Assigning the Import Interface to an Instrument
-----------------------------------------------
Create an `Instrument` and assign to it the tested Import Interface::

    >>> instrument = api.create(bika_instruments, "Instrument", title="Instrument-1")
    >>> instrument
    <Instrument at /plone/bika_setup/bika_instruments/instrument-1>
    >>> instrument.setImportDataInterface(['abbott.m2000rt.m2000rt'])
    >>> instrument.getImportDataInterface()
    ['abbott.m2000rt.m2000rt']

Import test
-----------

Required steps: Create and receive Analysis Request for import test
...................................................................

An `AnalysisRequest` can only be created inside a `Client`, and it also requires a `Contact` and
a `SampleType`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="NARALABS", ClientID="NLABS")
    >>> client
    <Client at /plone/clients/client-1>
    >>> contact = api.create(client, "Contact", Firstname="Juan", Surname="Gallostra")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>
    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="H2O", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

Create an `AnalysisCategory` (which categorizes different `AnalysisServices`), and add to it an `AnalysisService`.
This service matches the service specified in the file from which the import will be performed::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>
    >>> analysisservice = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HIV06ml",
    ...                              ShortTitle="hiv06",
    ...                              Category=analysiscategory,
    ...                              Keyword="HIV06ml")
    >>> analysisservice
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

Set some interim fields present in the results test file to the created `AnalysisService`::

    >>> service_interim_fields = [{'keyword': 'ASRExpDate',
    ...                            'title': 'ASRExpDate',
    ...                            'unit': '',
    ...                            'default': ''},
    ...                           {'keyword': 'ASRLotNumber',
    ...                            'title': 'ASRLotNumber',
    ...                            'unit': '',
    ...                            'default': ''},
    ...                           {'keyword': 'AssayCalibrationTime',
    ...                            'title': 'AssayCalibrationTime',
    ...                            'unit': '',
    ...                            'default': ''},
    ...                           {'keyword': 'FinalResult',
    ...                            'title': 'FinalResult',
    ...                            'unit': '',
    ...                            'default': ''},
    ...                           {'keyword': 'Location',
    ...                            'title': 'Location',
    ...                            'unit': '',
    ...                            'default': ''},
    ...                           ]
    >>> analysisservice.setInterimFields(service_interim_fields)
    >>> analysisservice.getInterimFields()
    [{'default': '', 'unit': '', 'keyword': 'ASRExpDate', 'title': 'ASRExpDate'},
     {'default': '', 'unit': '', 'keyword': 'ASRLotNumber', 'title': 'ASRLotNumber'},
     {'default': '', 'unit': '', 'keyword': 'AssayCalibrationTime', 'title': 'AssayCalibrationTime'},
     {'default': '', 'unit': '', 'keyword': 'FinalResult', 'title': 'FinalResult'},
     {'default': '', 'unit': '', 'keyword': 'Location', 'title': 'Location'}]

Create an `AnalysisRequest` with this `AnalysisService` and receive it::

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()
    ...          }
    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/H2O-0001-R01>
    >>> ar.getReceivedBy()
    ''
    >>> wf = getToolByName(ar, 'portal_workflow')
    >>> wf.doActionFor(ar, 'receive')
    >>> ar.getReceivedBy()
    'test_user_1_'

Import test
...........
Load results test file and import the results::

    >>> dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'files'))
    >>> temp_file = codecs.open(dir_path + '/Results.log.123',
    ...                         encoding='utf-8-sig')
    >>> test_file = ConvertToUploadFile(temp_file)
    >>> abbott_parser = Abbottm2000rtTSVParser(test_file)
    >>> importer = Abbottm2000rtImporter(parser=abbott_parser,
    ...                                  context=portal,
    ...                                  idsearchcriteria=['getId', 'getSampleID', 'getClientSampleID'],
    ...                                  allowed_ar_states=['sample_received', 'attachment_due', 'to_be_verified'],
    ...                                  allowed_analysis_states=None,
    ...                                  override=[True, True])
    >>> importer.process()

Check from the importer logs that the file from where the results have been imported is indeed
the specified file::

    >>> '/Results.log.123' in importer.logs[0]
    True

Check the rest of the importer logs to verify that the values were correctly imported::

    >>> importer.logs[1:]
    ['End of file reached successfully: 24 objects, 1 analyses, 24 results',
     'Allowed Analysis Request states: sample_received, attachment_due, to_be_verified',
     'Allowed analysis states: sampled, sample_received, attachment_due, to_be_verified',
     "H2O-0001 result for 'HIV06ml:ASRExpDate': '20141211'",
     "H2O-0001 result for 'HIV06ml:ASRLotNumber': '0123456'",
     "H2O-0001 result for 'HIV06ml:AssayCalibrationTime': '20150423 16:37:05'",
     "H2O-0001 result for 'HIV06ml:FinalResult': '18'",
     "H2O-0001 result for 'HIV06ml:Location': 'A12'",
     "H2O-0001-R01: [u'Analysis HIV06ml'] imported sucessfully",
     'Import finished successfully: 1 ARs and 1 results updated']

And finally check if indeed the analysis has the imported results::

    >>> analyses = ar.getAnalyses()
    >>> an = [analysis.getObject() for analysis in analyses if analysis.Title == 'HIV06ml'][0]
    >>> an.getInterimFields()
    [{'default': '', 'value': '20141211', 'unit': '', 'keyword': 'ASRExpDate', 'title': 'ASRExpDate'},
     {'default': '', 'value': '0123456', 'unit': '', 'keyword': 'ASRLotNumber', 'title': 'ASRLotNumber'},
     {'default': '', 'value': '20150423 16:37:05', 'unit': '', 'keyword': 'AssayCalibrationTime', 'title': 'AssayCalibrationTime'},
     {'default': '', 'value': '18', 'unit': '', 'keyword': 'FinalResult', 'title': 'FinalResult'},
     {'default': '', 'value': 'A12', 'unit': '', 'keyword': 'Location', 'title': 'Location'}]

