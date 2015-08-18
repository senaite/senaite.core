from Products.CMFPlone.utils import _createObjectByType
from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
import unittest

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestARImports(BikaFunctionalTestCase):
    layer = BIKA_SIMPLE_FIXTURE

    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(TestARImports, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.client = self.addthing(self.portal.clients, 'Client',
                                    title='Happy Hills', ClientID='HH')
        self.addthing(self.client, 'Contact', Firstname='Rita',
                      Lastname='Mohale')
        self.addthing(self.portal.bika_setup.bika_sampletypes, 'SampleType',
                      title='Agua del grifo')
        self.addthing(self.portal.bika_setup.bika_samplematrices,
                      'SampleMatrix', title='Agua')
        self.addthing(self.portal.bika_setup.bika_samplepoints, 'SamplePoint',
                      title='el grifo')
        self.addthing(self.portal.bika_setup.bika_containertypes,
                      'ContainerType', title='la taza')
        self.addthing(self.portal.bika_setup.bika_analysisservices,
                      'AnalysisService', title='A Service', Keyword="AKeyword")
        self.addthing(self.portal.bika_setup.bika_analysisprofiles,
                      'AnalysisProfile', title='A Profile')
        self.arimport = self.addthing(self.client, 'ARImport')

    def tearDown(self):
        super(TestARImports, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_complete_valid_batch_import(self):
        self.arimport.setOriginalFile("""Header,Import / Export,File name,Client name,Client ID,Contact,CC Names - Report,CC Emails - Report,CC Names - Invoices,CC Emails - Invoice,No of Samples,Client Order Number,Client Reference,,
        Header Data,Import,BikaARImportToBatchTemplate_02,Happy Hills,HH,Rita Mohale,,,,,10,HHPO-001,,,
        Batch Header,id,title,description,ClientBatchID,ClientBatchComment,BatchLabels,ReturnSampleToClient,,,
        Batch Data,B15-0123,New Batch,Optional descr,CC 201506,Routine monthly safety measure,,TRUE,,,
        Samples,ClientSampleID,SamplingDate,DateSampled,SamplePoint,SampleMatrix,SampleType,ContainerType,ReportDryMatter,Priority,Total number of Analyses or Profiles,Price excl Tax,AKeyword,"A Profile"
        Analysis price,,,,,,,,,,,,,,
        "Total Analyses or Profiles",,,,,,,,,,,,,3,,,
        Total price excl Tax,,,,,,,,,,,,,,
        "Sample 1",HHS14001,3/9/2014,3/9/2014,"el grifo",Agua,"Agua del grifo","la taza",0,,2,,1,1
        "Sample 2",HHS14002,3/9/2014,3/9/2014,"el grifo",Agua,"Agua del grifo","la taza",0,,1,,1,
        """)
        self.arimport.workflow_script_validate()
        errors = self.arimport.getErrors()
        self.assertEqual(errors, (), "Unexpected errors: " + str(errors))

    def test_missing_header_data(self):
        self.arimport.setOriginalFile("""
            Header,File name,Client name,Client ID,Contact,CC Names - Report,CC Emails - Report,CC Names - Invoices,CC Emails - Invoice,No of Samples,Client Order Number,Client Reference,,,,,,,,,,,,,
            """)
        self.arimport.validate_header()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestARImports))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
