from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Products.validation import validation
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import *
from plone.app.testing import *
from plone.testing import z2
import unittest

class Tests(BikaFunctionalTestCase):

    baseurl = None
    browser = None

    def setUp(self):
        BikaFunctionalTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        self.browser = self.browserLogin()
        self.baseurl = self.browser.url

    def test_MinMaxValuesEditionIntegrity(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisspecs/analysisspec-2"))
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('min.%s:records' % uid)).value = "11"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "10"       
        self.browser.getControl(name='form.button.save').click()
        
        #Checking after POST
        specsobj = self.bsc(portal_type="AnalysisSpec", id='analysisspec-2')[0].getObject()        
        for spec in specsobj.getResultsRange():
            if (sv.getKeyword() == spec['keyword']):
                smin = spec['min']
                smax = spec['max']
                self.assertFalse(float(smin) > float(smax), "Min-Max inconsistence error (%s > %s)" % (smin, smax))
                break
            
    def test_ErrorPercentage(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisspecs/analysisspec-2"))
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "20"    
        self.browser.getControl(name=('error.%s:records' % uid)).value = "-10"
        self.browser.getControl(name='form.button.save').click()
        
        #Checking after POST
        specsobj = self.bsc(portal_type="AnalysisSpec", id='analysisspec-2')[0].getObject()        
        for spec in specsobj.getResultsRange():
            if (sv.getKeyword() == spec['keyword']):
                error = spec['error']
                self.assertFalse(float(error) < 0, "Percentage error < 0 (%s for %s)" % (error, spec['keyword']))
                break
        
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "20"    
        self.browser.getControl(name=('error.%s:records' % uid)).value = "101"
        self.browser.getControl(name='form.button.save').click()
        
        #Checking after POST
        specsobj = self.bsc(portal_type="AnalysisSpec", id='analysisspec-2')[0].getObject()        
        for spec in specsobj.getResultsRange():
            if (sv.getKeyword() == spec['keyword']):
                error = spec['error']
                self.assertFalse(float(error) > 100, "Percentage error > 100 (%s for %s)" % (error, spec['keyword']))
                break
    
    def test_NumericValues(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisspecs/analysisspec-2"))
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('min.%s:records' % uid)).value = "x"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "x"    
        self.browser.getControl(name=('error.%s:records' % uid)).value = "x"
        self.browser.getControl(name='form.button.save').click()
        
        #Checking after POST
        specsobj = self.bsc(portal_type="AnalysisSpec", id='analysisspec-2')[0].getObject()        
        for spec in specsobj.getResultsRange():
            if (sv.getKeyword() == spec['keyword']):                
                try: float(spec['min'])
                except: self.assertIsNotNone(None, "Min value must be numeric")
                try: float(spec['max'])
                except: self.assertIsNotNone(None, "Max value must be numeric")
                try: float(spec['error'])
                except: self.assertIsNotNone(None, "Error value must be numeric")                
                break
    
    def test_AnalysisSpecEdition(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisspecs/analysisspec-2"))
        descriptioninit = self.browser.getControl(name='description').value
        tests = [ {'id':'53','min':'-20', 'max':'-10', 'error':'10'},
                  {'id':'43','min':'-10', 'max':  '0', 'error':'10'},
                  {'id':'44','min':  '0', 'max': '10', 'error':'10'},
                  {'id':'10','min': '10', 'max': '20', 'error':'10'},  
                  {'id':'12','min':'-20', 'max':'-10', 'error': '0'},
                  {'id':'25','min':  '0', 'max':  '0', 'error':'10'},
                  {'id':'23','min':'-10', 'max':  '0', 'error':'100'}
                ]
        
        for test in tests:
            sv = self.bsc(portal_type="AnalysisService",
                     id=("analysisservice-%s" % test['id']))[0].getObject()
            
            uid = sv.UID()
                                
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid            

            min = self.browser.getControl(name=minid)
            max = self.browser.getControl(name=maxid)
            error = self.browser.getControl(name=errorid)            

            min.value = "%s" % test['min']
            max.value = "%s" % test['max']
            error.value = "%s" % test['error']

        description = 'Apple Pulp Analysis Specification description'
        self.browser.getControl(name='description').value = description
        self.browser.getControl(name='form.button.save').click()

        # Cecking after POST
        for test in tests:
            svid = "analysisservice-%s" % test['id']
            sv = self.bsc(portal_type="AnalysisService", id=svid)[0].getObject()
            uid = sv.UID()
            
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid
            
            min = self.browser.getControl(name=minid).value
            max = self.browser.getControl(name=maxid).value
            err = self.browser.getControl(name=errorid).value
            
            minvalue = min == '' and '0' or min
            maxvalue = max == '' and '0' or max
            errvalue = err == '' and '0' or err    
            
            tminvalue = test['min'] == '' and '0' or test['min']
            tmaxvalue = test['max'] == '' and '0' or test['max']
            terrvalue = test['error'] == '' and '0' or test['error']            
                        
            self.assertTrue(minvalue == tminvalue, "Incorrect Min field value %s <> %s" % (min, test['min']))
            self.assertTrue(maxvalue == tmaxvalue, "Incorrect Max field value %s <> %s" % (max, test['max']))
            self.assertTrue(errvalue == terrvalue, "Incorrect Error field value %s <> %s" % (err, test['error']))
            
        desc = self.browser.getControl(name='description').value
        self.assertEqual(desc, description, "Incorrect Description field value (%s <> %s for %s)" % (desc, description, svid))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite