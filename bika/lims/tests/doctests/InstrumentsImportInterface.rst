Abbott's m2000 Real Time import interface
=========================================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t InstrumentsImportInterface


Test Setup
----------
Needed imports::

    >>> import os
    >>> import transaction
    >>> import cStringIO
    >>> from Products.CMFCore.utils import getToolByName
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime

    >>> import codecs
    >>> from bika.lims.exportimport import instruments
    >>> from bika.lims.exportimport.instruments.abbott.m2000rt.m2000rt \
    ...      import Abbottm2000rtTSVParser, Abbottm2000rtImporter
    >>> from bika.lims.browser.resultsimport.resultsimport import ConvertToUploadFile
    >>> from zope.publisher.browser import FileUpload, TestRequest

Functional helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> class TestFile(object):
    ...     def __init__(self, file, filename='dummy.txt'):
    ...         self.file = file
    ...         self.headers = {}
    ...         self.filename = filename

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


Instruments files path
----------------------
Where testing files live::

    >>> files_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'files/instruments'))
    >>> instruments_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'exportimport/instruments'))
    >>> files = os.listdir(files_path)
    >>> interfaces = []
    >>> mylist = [] #TODO: rename mylist
    >>> for fl in files:
    ...     inst_interface = os.path.splitext(fl)[0] 
    ...     inst_path = '.'.join([inst_interface.replace('.', '/'), 'py'])
    ...     if os.path.isfile(os.path.join(instruments_path, inst_path)):
    ...         interfaces.append(inst_interface)
    ...         mylist.append((inst_interface, fl))
    ...     else:
    ...         inst_path = '.'.join([fl.replace('.', '/'), 'py'])
    ...         if os.path.isfile(os.path.join(instruments_path, inst_path)):
    ...             interfaces.append(inst_interface)
    ...             mylist.append((inst_interface, fl))
    ...         else:
    ...             self.fail('File {} found does match any import interface'.format(fl))

Availability of instrument interface
------------------------------------
Check that the instrument interface is available::

    >>> exims = []
    >>> for exim_id in instruments.__all__:
    ...     exims.append(exim_id)
    >>> [f for f in interfaces if f not in exims] 
    []

Assigning the Import Interface to an Instrument
-----------------------------------------------
TODO: Find a to test that the instruments have been created
Create an `Instrument` and assign to it the tested Import Interface::

    >>> for inter in interfaces:
    ...     title = inter.split('.')[0].title()
    ...     instrument = api.create(bika_instruments, "Instrument", title=title)
    ...     instrument.setImportDataInterface([inter])
    
    >>> for inter in mylist:
    ...     exec('from bika.lims.exportimport.instruments.{} import Import'.format(inter[0]))
    ...     filename = os.path.join(files_path, inter[1])
    ...     data = open(filename, 'r').read()
    ...     import_file = FileUpload(TestFile(cStringIO.StringIO(data)))
    ...     request = TestRequest(form=dict(
    ...                                submitted=True,
    ...                                artoapply='received',
    ...                                results_override='nooverride',
    ...                                instrument_results_file=import_file,
    ...                                override='nooverride',
    ...                                filename=import_file,
    ...                                format='tsv',
    ...                                sample='requestid',
    ...                                instrument=''))
    ...     context = self.portal
    ...     results = Import(context, request)
    ...     test_results = eval(results)
    ...     if 'Import finished successfully: 1 ARs and 1 results updated' not in test_results['log']:
    ...         self.fail("Results Update failed")

