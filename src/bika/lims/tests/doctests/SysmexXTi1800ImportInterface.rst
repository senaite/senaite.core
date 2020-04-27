Sysmex xt i1800 import interface
================================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SysmexXTi1800ImportInterface


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
    >>> from bika.lims.exportimport.instruments.sysmex.xt import SysmexXTImporter
    >>> from bika.lims.exportimport.instruments.sysmex.xt.i1800 import TX1800iParser
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
    >>> 'sysmex.xt.i1800' in exims
    True

Assigning the Import Interface to an Instrument
-----------------------------------------------
Create an `Instrument` and assign to it the tested Import Interface::

    >>> instrument = api.create(bika_instruments, "Instrument", title="Instrument-1")
    >>> instrument
    <Instrument at /plone/bika_setup/bika_instruments/instrument-1>
    >>> instrument.setImportDataInterface(['sysmex.xt.i1800'])
    >>> instrument.getImportDataInterface()
    ['sysmex.xt.i1800']

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

Create an `AnalysisCategory` (which categorizes different `AnalysisServices`), and add to it some
of the `AnalysisServices` that are found in the results file::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>
    >>> analysisservice_1 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="WBC",
    ...                              ShortTitle="wbc",
    ...                              Category=analysiscategory,
    ...                              Keyword="WBC")
    >>> analysisservice_1
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>
    >>> analysisservice_2 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="RBC",
    ...                              ShortTitle="rbc",
    ...                              Category=analysiscategory,
    ...                              Keyword="RBC")
    >>> analysisservice_2
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>
    >>> analysisservice_3 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HGB",
    ...                              ShortTitle="hgb",
    ...                              Category=analysiscategory,
    ...                              Keyword="HGB")
    >>> analysisservice_3
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-3>
    >>> analysisservice_4 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HCT",
    ...                              ShortTitle="hct",
    ...                              Category=analysiscategory,
    ...                              Keyword="HCT")
    >>> analysisservice_4
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-4>
    >>> analysisservices = [analysisservice_1, analysisservice_2, analysisservice_3, analysisservice_4]

Create an `AnalysisRequest` with this `AnalysisService` and receive it::

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()
    ...          }
    >>> service_uids = [analysisservice.UID() for analysisservice in analysisservices]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/H2O-0001>
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
    >>> temp_file = codecs.open(dir_path + '/2012-05-09_11-06-14-425_CBDB6A.txt',
    ...                         encoding='utf-8-sig')
    >>> test_file = ConvertToUploadFile(temp_file)
    >>> tx1800i_parser = TX1800iParser(test_file)
    >>> importer = SysmexXTImporter(parser=tx1800i_parser,
    ...                             context=portal,
    ...                             allowed_ar_states=['sample_received', 'attachment_due', 'to_be_verified'],
    ...                             allowed_analysis_states=None,
    ...                             override=[True, True])
    >>> importer.process()

Check from the importer logs that the file from where the results have been imported is indeed
the specified file::

    >>> '2012-05-09_11-06-14-425_CBDB6A.txt' in importer.logs[0]
    True

Check the rest of the importer logs to verify that the values were correctly imported::

    >>> importer.logs[1:]
    ['End of file reached successfully: 1 objects, 21 analyses, 1 results',
     'Allowed Sample states: sample_received, attachment_due, to_be_verified',
     'Allowed analysis states: unassigned, assigned, to_be_verified',
     "H2O-0001: [u'Analysis HCT', u'Analysis RBC', u'Analysis WBC', u'Analysis HGB'] imported sucessfully",
     'Import finished successfully: 1 Samples and 4 results updated']

And finally check if indeed the analysis has the imported results::

    >>> analyses = ar.getAnalyses()
    >>> an = [analysis.getObject() for analysis in analyses if analysis.Title=='WBC'][0]
    >>> an.getResult()
    '6.01'
    >>> an = [analysis.getObject() for analysis in analyses if analysis.Title=='RBC'][0]
    >>> an.getResult()
    '5.02'
    >>> an = [analysis.getObject() for analysis in analyses if analysis.Title=='HGB'][0]
    >>> an.getResult()
    '13.2'
    >>> an = [analysis.getObject() for analysis in analyses if analysis.Title=='HCT'][0]
    >>> an.getResult()
    '40.0'

