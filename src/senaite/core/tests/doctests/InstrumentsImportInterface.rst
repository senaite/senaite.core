Instruments import interface
============================
We are going to test all instruments import interfaces on this one doctest
1. These files can only be added on `tests/files/instruments/`
2. The filenames(files to be imported) have to have the same name as their
   import data interface i.e
   `exportimport/instruments/generic/two_dimension.py` would match with
   `tests/files/instruments/generic.two_dimension.csv` and
   `exportimport/instruments/varian/vistapro/icp.py` would match with
   `tests/files/instruments/varian.vistapro.icp.csv`
   The reason for the above filenaming is so that we can do
   `interface = varian.vistapro.icp`
   `exec('from bika.lims.exportimport.instruments.{} import Import'.format(inteface))`
   LINE:225
3. All the files would have the same SampleID/AR-ID
   `H2O-0001`
4. Same analyses and same results because they will be testing against the same AR
   `Ca` = 0.0
   `Mg` = 2.0
5. To set DefaultResult to float `0.0` use `get_result`
   example can be found at `exportimport/instruments/varian/vistapro/icp.py`

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
    >>> bika_calculations = bika_setup.bika_calculations

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
    >>> analysisservice1 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HIV06ml",
    ...                              ShortTitle="hiv06",
    ...                              Category=analysiscategory,
    ...                              Keyword="HIV06ml")
    >>> analysisservice1
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

    >>> analysisservice2 = api.create(bika_analysisservices,
    ...                       'AnalysisService',
    ...                       title='Magnesium',
    ...                       ShortTitle='Mg',
    ...                       Category=analysiscategory,
    ...                       Keyword="Mg")
    >>> analysisservice2
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>
    >>> analysisservice3 = api.create(bika_analysisservices,
    ...                     'AnalysisService',
    ...                     title='Calcium',
    ...                     ShortTitle='Ca',
    ...                     Category=analysiscategory,
    ...                     Keyword="Ca")
    >>> analysisservice3
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-3>

    >>> total_calc = api.create(bika_calculations, 'Calculation', title='TotalMagCal')
    >>> total_calc.setFormula('[Mg] + [Ca]')
    >>> analysisservice4 = api.create(bika_analysisservices, 'AnalysisService', title='THCaCO3', Keyword="THCaCO3")
    >>> analysisservice4.setUseDefaultCalculation(False)
    >>> analysisservice4.setCalculation(total_calc)
    >>> analysisservice4
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-4>

    >>> interim_calc = api.create(bika_calculations, 'Calculation', title='Test-Total-Pest')
    >>> pest1 = {'keyword': 'pest1', 'title': 'Pesticide 1', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest2 = {'keyword': 'pest2', 'title': 'Pesticide 2', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest3 = {'keyword': 'pest3', 'title': 'Pesticide 3', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> interims = [pest1, pest2, pest3]
    >>> interim_calc.setInterimFields(interims)
    >>> self.assertEqual(interim_calc.getInterimFields(), interims)
    >>> interim_calc.setFormula('((([pest1] > 0.0) or ([pest2] > .05) or ([pest3] > 10.0) ) and "PASS" or "FAIL" )')
    >>> analysisservice5 = api.create(bika_analysisservices, 'AnalysisService', title='Total Terpenes', Keyword="TotalTerpenes")
    >>> analysisservice5.setUseDefaultCalculation(False)
    >>> analysisservice5.setCalculation(interim_calc)
    >>> analysisservice5.setInterimFields(interims)
    >>> analysisservice5
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-5>

Create an `AnalysisRequest` with this `AnalysisService` and receive it::

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()
    ...          }
    >>> service_uids = [analysisservice1.UID(),
    ...                 analysisservice2.UID(),
    ...                 analysisservice3.UID(),
    ...                 analysisservice4.UID(),
    ...                 analysisservice5.UID()
    ...                ]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/H2O-0001>
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
    >>> importer_filename = [] #List of tuples [(importer,filename),(importer, filename)]
    >>> for fl in files:
    ...     inst_interface = os.path.splitext(fl)[0] 
    ...     inst_path = '.'.join([inst_interface.replace('.', '/'), 'py'])
    ...     if os.path.isfile(os.path.join(instruments_path, inst_path)):
    ...         interfaces.append(inst_interface)
    ...         importer_filename.append((inst_interface, fl))
    ...     else:
    ...         inst_path = '.'.join([fl.replace('.', '/'), 'py'])
    ...         if os.path.isfile(os.path.join(instruments_path, inst_path)):
    ...             interfaces.append(fl)
    ...             importer_filename.append((fl, fl))
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
Create an `Instrument` and assign to it the tested Import Interface::

    >>> for inter in interfaces:
    ...     title = inter.split('.')[0].title()
    ...     instrument = api.create(bika_instruments, "Instrument", title=title)
    ...     instrument.setImportDataInterface([inter])
    ...     if instrument.getImportDataInterface() != [inter]:
    ...         self.fail('Instrument Import Data Interface did not get set')
    
    >>> for inter in importer_filename:
    ...     exec('from bika.lims.exportimport.instruments.{} import Import'.format(inter[0]))
    ...     filename = os.path.join(files_path, inter[1])
    ...     data = open(filename, 'r').read()
    ...     import_file = FileUpload(TestFile(cStringIO.StringIO(data), inter[1]))
    ...     request = TestRequest(form=dict(
    ...                                submitted=True,
    ...                                artoapply='received_tobeverified',
    ...                                results_override='override',
    ...                                instrument_results_file=import_file,
    ...                                sample='requestid',
    ...                                instrument=''))
    ...     context = self.portal
    ...     results = Import(context, request)
    ...     test_results = eval(results)
    ...     #TODO: Test for interim fields on other files aswell
    ...     analyses = ar.getAnalyses(full_objects=True)
    ...     if 'Parsing file generic.two_dimension.csv' in test_results['log']:
    ...         # Testing also for interim fields, only for `generic.two_dimension` interface
    ...         # TODO: Test for - H2O-0001: calculated result for 'THCaCO3': '2.0'
    ...         if 'Import finished successfully: 1 Samples and 3 results updated' not in test_results['log']:
    ...             self.fail("Results Update failed")
    ...         if "H2O-0001 result for 'TotalTerpenes:pest1': '1'" not in test_results['log']:
    ...             self.fail("pest1 did not get updated")
    ...         if "H2O-0001 result for 'TotalTerpenes:pest2': '1'" not in test_results['log']:
    ...             self.fail("pest2 did not get updated")
    ...         if "H2O-0001 result for 'TotalTerpenes:pest3': '1'" not in test_results['log']:
    ...             self.fail("pest3 did not get updated")
    ...         for an in analyses:
    ...             if an.getKeyword() == 'TotalTerpenes':
    ...                 if an.getResult() != 'PASS':
    ...                     msg = "{}:Result did not get updated".format(an.getKeyword())
    ...                     self.fail(msg)
    ...
    ...     elif 'Import finished successfully: 1 Samples and 2 results updated' not in test_results['log']:
    ...         self.fail("Results Update failed")
    ...
    ...     for an in analyses:
    ...         if an.getKeyword() ==  'Ca':
    ...             if an.getResult() != '0.0':
    ...                 msg = "{}:Result did not get updated".format(an.getKeyword())
    ...                 self.fail(msg)
    ...         if an.getKeyword() ==  'Mg':
    ...             if an.getResult() != '2.0':
    ...                 msg = "{}:Result did not get updated".format(an.getKeyword())
    ...                 self.fail(msg)
    ...         if an.getKeyword() ==  'THCaCO3':
    ...             if an.getResult() != '2.0':
    ...                 msg = "{}:Result did not get updated".format(an.getKeyword())
    ...                 self.fail(msg)
    ...
    ...     if 'Import' in globals():
    ...         del Import
