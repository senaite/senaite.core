from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Products.validation import validation
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from Products.Archetypes.config import REFERENCE_CATALOG
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
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_referencedefinitions/referencedefinition-1"))
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('result.%s:records' % uid)).value = "5"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "0"       
        self.browser.getControl(name='form.button.save').click()
        
        # Check min and max integrity
        specsobj = self.bsc(portal_type="ReferenceDefinition", id='referencedefinition-1')[0].getObject()        
        for spec in specsobj.getReferenceResults():
            if (uid == spec['uid']):
                smin = spec['min']
                smax = spec['max']
                sres = spec['result']
                self.assertFalse(float(smin) > float(smax), "Min-Max inconsistence error (%s > %s)" % (smin, smax))
                self.assertFalse(sres < smin and sres > smax, "Reference result %s must be between min %s and max %s values for %s" % (sres, smin, smax, spec['uid']))
                break
            
        self.browser.getControl(name=('result.%s:records' % uid)).value = "15"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "20"       
        self.browser.getControl(name='form.button.save').click()
        
        # Check if result is between min and max values
        specsobj = self.bsc(portal_type="ReferenceDefinition", id='referencedefinition-1')[0].getObject()        
        for spec in specsobj.getReferenceResults():
            if (uid == spec['uid']):
                smin = spec['min']
                smax = spec['max']
                sres = spec['result']
                self.assertTrue(sres > smin and sres < smax, "Reference result %s must be between min %s and max %s values for %s" % (sres, smin, smax, spec['uid']))
                break        
            
    
    
    def test_NumericValues(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_referencedefinitions/referencedefinition-1"))
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('result.%s:records' % uid)).value = "x"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "x"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "x"    
        self.browser.getControl(name=('error.%s:records' % uid)).value = "x"
        self.browser.getControl(name='form.button.save').click()
        
        #Checking after POST
        specsobj = self.bsc(portal_type="ReferenceDefinition", id='referencedefinition-1')[0].getObject()        
        for spec in specsobj.getReferenceResults():
            if (uid == spec['uid']):
                try: float(spec['result'])
                except: self.assertIsNotNone(None, "Result value must be numeric")
                try: float(spec['min'])
                except: self.assertIsNotNone(None, "Min value must be numeric")
                try: float(spec['max'])
                except: self.assertIsNotNone(None, "Max value must be numeric")
                break
    
    def test_ReferenceDefinitionValues(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_referencedefinitions/referencedefinition-1"))
        descriptioninit = self.browser.getControl(name='description').value
        tests = [ {'id':'53','result':'-15','min':'-20', 'max':'-10', 'error':'10'},
                  {'id':'43','result':'-5','min':'-10', 'max':  '0', 'error':'10'},
                  {'id':'44','result':'5','min':  '0', 'max': '10', 'error':'10'},
                  {'id':'10','result':'15','min': '10', 'max': '20', 'error':'10'},  
                  {'id':'12','result':'-15','min':'-20', 'max':'-10', 'error': '0'},
                  {'id':'25','result':'0','min': '0', 'max':  '0', 'error':'10'},
                  {'id':'23','result':'-5','min':'-10', 'max':  '0', 'error':'100'}
                ]
        
        for test in tests:
            sv = self.bsc(portal_type="AnalysisService",
                     id=("analysisservice-%s" % test['id']))[0].getObject()
            
            uid = sv.UID()
                               
            resid = 'result.%s:records' % uid
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid            

            res = self.browser.getControl(name=resid)
            min = self.browser.getControl(name=minid)
            max = self.browser.getControl(name=maxid)
            error = self.browser.getControl(name=errorid)            
            
            res.value = "%s" % test['result']
            min.value = "%s" % test['min']
            max.value = "%s" % test['max']
            error.value = "%s" % test['error']

        description = 'Blank Reference description'
        self.browser.getControl(name='description').value = description
        self.browser.getControl(name='form.button.save').click()

        # Cecking after POST
        for test in tests:
            svid = "analysisservice-%s" % test['id']
            sv = self.bsc(portal_type="AnalysisService", id=svid)[0].getObject()
            uid = sv.UID()
            
            resid = 'result.%s:records' % uid
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            
            res = self.browser.getControl(name=resid).value
            min = self.browser.getControl(name=minid).value
            max = self.browser.getControl(name=maxid).value
            
            resvalue = res == '' and '0' or res
            minvalue = min == '' and '0' or min
            maxvalue = max == '' and '0' or max  
            
            tresvalue = test['result'] == '' and '0' or test['result']
            tminvalue = test['min'] == '' and '0' or test['min']
            tmaxvalue = test['max'] == '' and '0' or test['max']         
            
            self.assertTrue(resvalue == tresvalue, "Incorrect Result field value %s <> %s" % (res, test['result']))        
            self.assertTrue(minvalue == tminvalue, "Incorrect Min field value %s <> %s" % (min, test['min']))
            self.assertTrue(maxvalue == tmaxvalue, "Incorrect Max field value %s <> %s" % (max, test['max']))
            
        desc = self.browser.getControl(name='description').value
        self.assertEqual(desc, description, "Incorrect Description field value (%s <> %s for %s)" % (desc, description, svid))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite