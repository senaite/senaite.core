from Products.CMFPlone.utils import _createObjectByType
from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaSimpleTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName

import re
import transaction
import unittest

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestARImports(BikaSimpleTestCase):

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
        self.addthing(self.client, 'Contact', Firstname='Rita Mohale',
                      Lastname='Mohale')
        self.addthing(self.portal.bika_setup.bika_sampletypes, 'SampleType',
                      title='Water', Prefix='H2O')
        self.addthing(self.portal.bika_setup.bika_samplematrices,
                      'SampleMatrix', title='Liquids')
        self.addthing(self.portal.bika_setup.bika_samplepoints, 'SamplePoint',
                      title='Toilet')
        self.addthing(self.portal.bika_setup.bika_containertypes,
                      'ContainerType', title='Cup')
        self.addthing(self.portal.bika_setup.bika_arpriorities, 'ARPriority',
                      title='Normal', sortKey=1)
        a = self.addthing(self.portal.bika_setup.bika_analysisservices,
                          'AnalysisService', title='Ecoli', Keyword="ECO")
        b = self.addthing(self.portal.bika_setup.bika_analysisservices,
                          'AnalysisService', title='Salmonella', Keyword="SAL")
        c = self.addthing(self.portal.bika_setup.bika_analysisservices,
                          'AnalysisService', title='Color', Keyword="COL")
        d = self.addthing(self.portal.bika_setup.bika_analysisservices,
                          'AnalysisService', title='Taste', Keyword="TAS")
        self.addthing(self.portal.bika_setup.bika_analysisprofiles,
                      'AnalysisProfile', title='MicroBio',
                      Service=[a.UID(), b.UID()])
        self.addthing(self.portal.bika_setup.bika_analysisprofiles,
                      'AnalysisProfile', title='Properties',
                      Service=[c.UID(), d.UID()])

    def tearDown(self):
        super(TestARImports, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_complete_valid_batch_import(self):
        pc = getToolByName(self.portal, 'portal_catalog')
        workflow = getToolByName(self.portal, 'portal_workflow')
        arimport = self.addthing(self.client, 'ARImport')
        arimport.unmarkCreationFlag()
        arimport.setFilename("test1.csv")
        arimport.setOriginalFile("""
Header,      File name,  Client name,  Client ID, Contact,     CC Names - Report, CC Emails - Report, CC Names - Invoice, CC Emails - Invoice, No of Samples, Client Order Number, Client Reference,,
Header Data, test1.csv,  Happy Hills,  HH,        Rita Mohale,                  ,                   ,                    ,                    , 10,            HHPO-001,                            ,,
Batch Header, id,       title,     description,    ClientBatchID, ClientBatchComment, BatchLabels, ReturnSampleToClient,,,
Batch Data,   B15-0123, New Batch, Optional descr, CC 201506,     Just a batch,                  , TRUE                ,,,
Samples,    ClientSampleID,    SamplingDate,DateSampled,SamplePoint,SampleMatrix,SampleType,ContainerType,ReportDryMatter,Priority,Total number of Analyses or Profiles,Price excl Tax,ECO,SAL,COL,TAS,MicroBio,Properties
Analysis price,,,,,,,,,,,,,,
"Total Analyses or Profiles",,,,,,,,,,,,,9,,,
Total price excl Tax,,,,,,,,,,,,,,
"Sample 1", HHS14001,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          0,              Normal,  1,                                   0,             0,0,0,0,0,1
"Sample 2", HHS14002,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          0,              Normal,  2,                                   0,             0,0,0,0,1,1
"Sample 3", HHS14002,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          0,              Normal,  4,                                   0,             1,1,1,1,0,0
"Sample 4", HHS14002,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          0,              Normal,  2,                                   0,             1,0,0,0,1,0
        """)

        # check that values are saved without errors
        arimport.setErrors([])
        arimport.save_header_data()
        arimport.save_sample_data()
        arimport.create_or_reference_batch()
        errors = arimport.getErrors()
        if errors:
            self.fail("Unexpected errors while saving data: " + str(errors))
        # check that batch was created and linked to arimport without errors
        if not pc(portal_type='Batch'):
            self.fail("Batch was not created!")
        if not arimport.schema['Batch'].get(arimport):
            self.fail("Batch was created, but not linked to ARImport.")

        # the workflow scripts use response.write(); silence them
        arimport.REQUEST.response.write = lambda x: x

        # check that validation succeeds without any errors
        workflow.doActionFor(arimport, 'validate')
        state = workflow.getInfoFor(arimport, 'review_state')
        if state != 'valid':
            errors = arimport.getErrors()
            self.fail(
                'Validation failed!  %s.Errors: %s' % (arimport.id, errors))

        # Import objects and verify that they exist
        workflow.doActionFor(arimport, 'import')
        state = workflow.getInfoFor(arimport, 'review_state')
        if state != 'imported':
            errors = arimport.getErrors()
            self.fail(
                'Importation failed!  %s.Errors: %s' % (arimport.id, errors))

        bc = getToolByName(self.portal, 'bika_catalog')
        ars = bc(portal_type='AnalysisRequest')
        if not ars[0].getObject().getContact():
            self.fail('No Contact imported into ar.Contact field.')
        l = len(ars)
        if l != 4:
            self.fail('4 AnalysisRequests were not created!  We found %s' % l)
        l = len(bc(portal_type='Sample'))
        if l != 4:
            self.fail('4 Samples were not created!  We found %s' % l)
        bac = getToolByName(self.portal, 'bika_analysis_catalog')
        analyses = bac(portal_type='Analysis')
        l = len(analyses)
        if l != 12:
            self.fail('12 Analysis not found! We found %s' % l)
        states = [workflow.getInfoFor(a.getObject(), 'review_state')
                  for a in analyses]
        if states != ['sample_due'] * 12:
            self.fail('Analysis states should all be sample_due, but are not!')

    def test_LIMS_2080_correctly_interpret_false_and_blank_values(self):
        pc = getToolByName(self.portal, 'portal_catalog')
        workflow = getToolByName(self.portal, 'portal_workflow')
        arimport = self.addthing(self.client, 'ARImport')
        arimport.unmarkCreationFlag()
        arimport.setFilename("test1.csv")
        arimport.setOriginalFile("""
Header,      File name,  Client name,  Client ID, Contact,     CC Names - Report, CC Emails - Report, CC Names - Invoice, CC Emails - Invoice, No of Samples, Client Order Number, Client Reference,,
Header Data, test1.csv,  Happy Hills,  HH,        Rita Mohale,                  ,                   ,                    ,                    , 10,            HHPO-001,                            ,,
Samples,    ClientSampleID,    SamplingDate,DateSampled,SamplePoint,SampleMatrix,SampleType,ContainerType,ReportDryMatter,Priority,Total number of Analyses or Profiles,Price excl Tax,ECO,SAL,COL,TAS,MicroBio,Properties
Analysis price,,,,,,,,,,,,,,
"Total Analyses or Profiles",,,,,,,,,,,,,9,,,
Total price excl Tax,,,,,,,,,,,,,,
"Sample 1", HHS14001,          3/9/2014,    3/9/2014,   ,     ,     Water,     Cup,          0,              Normal,  1,                                   0,             0,0,0,0,0,1
"Sample 2", HHS14002,          3/9/2014,    3/9/2014,   ,     ,     Water,     Cup,          0,              Normal,  2,                                   0,             0,0,0,0,1,1
"Sample 3", HHS14002,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          1,              Normal,  4,                                   0,             1,1,1,1,0,0
"Sample 4", HHS14002,          3/9/2014,    3/9/2014,   Toilet,     Liquids,     Water,     Cup,          1,              Normal,  2,                                   0,             1,0,0,0,1,0
        """)

        # check that values are saved without errors
        arimport.setErrors([])
        arimport.save_header_data()
        arimport.save_sample_data()
        errors = arimport.getErrors()
        if errors:
            self.fail("Unexpected errors while saving data: " + str(errors))
        transaction.commit()
        browser = self.getBrowser(loggedIn=True)
        browser.open(arimport.absolute_url() + "/edit")
        content = browser.contents
        re.match('\<option selected\=\"selected\" value\=\"\d+\"\>Toilet\<\/option\>', content)
        #
        if len(re.findall('\<.*selected.*Toilet', content)) != 2:
            self.fail("Should be two empty SamplePoints, and two with values")
        #
        if len(re.findall('\<.*selected.*Liquids', content)) != 2:
            self.fail("Should be two empty Matrix fields, and two with values")
        #
        if len(re.findall('\<.*checked.*ReportDry', content)) != 2:
            self.fail("Should be two False DryMatters, and two True")


    def test_LIMS_2081_post_edit_fails_validation_gracefully(self):
        pc = getToolByName(self.portal, 'portal_catalog')
        workflow = getToolByName(self.portal, 'portal_workflow')
        arimport = self.addthing(self.client, 'ARImport')
        arimport.unmarkCreationFlag()
        arimport.setFilename("test1.csv")
        arimport.setOriginalFile("""
Header,      File name,  Client name,  Client ID, Contact,     CC Names - Report, CC Emails - Report, CC Names - Invoice, CC Emails - Invoice, No of Samples, Client Order Number, Client Reference,,
Header Data, test1.csv,  Happy Hills,  HH,        Rita Mohale,                  ,                   ,                    ,                    , 10,            HHPO-001,                            ,,
Samples,    ClientSampleID,    SamplingDate,DateSampled,SamplePoint,SampleMatrix,SampleType,ContainerType,ReportDryMatter,Priority,Total number of Analyses or Profiles,Price excl Tax,ECO,SAL,COL,TAS,MicroBio,Properties
Analysis price,,,,,,,,,,,,,,
"Total Analyses or Profiles",,,,,,,,,,,,,9,,,
Total price excl Tax,,,,,,,,,,,,,,
"Sample 1", HHS14001,          3/9/2014,    3/9/2014,   ,     ,     Water,     Cup,          0,              Normal,  1,                                   0,             0,0,0,0,0,1
        """)

        # check that values are saved without errors
        arimport.setErrors([])
        arimport.save_header_data()
        arimport.save_sample_data()
        arimport.create_or_reference_batch()
        errors = arimport.getErrors()
        if errors:
            self.fail("Unexpected errors while saving data: " + str(errors))
        transaction.commit()
        browser = self.getBrowser(loggedIn=True)
        browser.open(arimport.absolute_url() + "/edit")
        browser.getControl(name="ClientReference").value = 'test_reference'
        browser.getControl(name="form.button.save").click()
        if 'test_reference' not in browser.contents:
            self.fail('Failed to modify ARImport object (Client Reference)')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestARImports))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
