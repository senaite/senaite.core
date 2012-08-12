from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from hashlib import sha1
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
from zope.testbrowser.browser import Browser
import hmac
import json
import plone.protect
import unittest
import doctest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def _authenticator(self, user):
        manager = getUtility(IKeyManager)
        secret=manager.secret()
        auth=hmac.new(secret, user, sha1).hexdigest()
        return auth

    def test_analysisspecs_view(self):        
        ''' Tests for Analysis Specs View
        1. Test initial values loaded in the form for an Analysis Specification
        2. Test edited values integrity with those after posting the form
        3. Test Min-Max incoherent values in services
        4. Reset the Analysis Spec to its initial state        
        '''
        
        login(self.portal, TEST_USER_NAME)        
        setRoles(self.portal, TEST_USER_ID, ['Manager',])    
        from pdb import set_trace; set_trace();
        
        # url = self.portal.absolute_url()+"/Plone/bika_setup/bika_analysisspecs/analysisspec-2")        
        analysisspecid = "analysisspec-2"
        #url = "http://localhost:8080/Plone/bika_setup/bika_analysisspecs/%s" % analysisspecid    
        url = "http://localhost:8080/Plone/bika_setup/bika_analysisspecs/analysisspec-2";
        browser = Browser()
        browser.handleErrors = False        
        browser.open(url)
        from pdb import set_trace; set_trace();
        
        primer = 3
        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        descriptioninit = browser.getControl(name='description').value
        mininitvalues = {}
        maxinitvalues = {}
        errorinitvalues = {}
        serviceids = { '53', '43', '44', '10' }
        for serviceid in serviceids:
            sv = bsc(portal_type="AnalysisService", id=("analysisservice-%s" % serviceid))[0].getObject()
            uid = sv.UID()
            
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid            
            min = getControl(name=minid)
            max = getControl(name=maxid)
            error = getControl(name=errorid)
            
            # Check initial values
            self.assertTrue(sv.getMin(), min.value, "Incorrect Min init value (%s <> %s) for %s" % (min, sv.getMin(), uid))
            self.assertTrue(sv.getMax(), max.value, "Incorrect Max init value (%s <> %s) for %s" % (max, sv.getMax(), uid))
            self.assertTrue(sv.getError(), error.value, "Incorrect Error init value (%s <> %s) for %s" % (error, sv.getError(), uid))
            
            mininitvalues += min.value
            maxinitvalues += max.value
            errorinitvalues += error.value
            min.value = primer * 1
            max.value = primer * 2        
            error.value = primer / 3          
            primer += 3
        
        from pdb import set_trace; set_trace();
        description = 'Apple Pulp Analysis Specification description'
        browser.getControl(name='description').value = description
        
        # Cecking after POST
        primer = 3
        browser.getControl(name='form.button.save').click()
        for serviceid in serviceids:
            svid = "analysisservice-%s" % serviceid
            sv = bsc(portal_type="AnalysisService", id=svid)[0].getObject()
            uid = sv.UID()  
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid
            min = browser.getControl(name=minid).value
            max = browser.getControl(name=maxid).value
            error = browser.getControl(name=error).value        
            self.assertTrue(min, primer * 1, "Incorrect Min field value (%s) for %s" % (min, uid))
            self.assertTrue(max, primer * 2, "Incorrect Max field value (%s) for %s" % (min, uid))
            self.assertTrue(error, primer / 3, "Incorrect Error field value (%s) for %s" % (min, uid))      
            primer += 3
            
        desc = browser.getControl(name='description').value
        self.assertEqual(desc, description, "Incorrect Description field value (%s <> %s)" % (desc, description))
        
        # Min-Max Invalid values test
        browser.getControl(name=('min.%s:records' % uid)).value = 11
        browser.getControl(name=('max.%s:records' % uid)).value = 10
        browser.getControl(name='form.button.save').click()   
        specsobj = bsc(portal_type="AnalysisSpec", id=analysisspecid)[0].getObject()
        tool = getToolByName(specsobj, REFERENCE_CATALOG)
        for spec in specsobj.getResultsRange():
            service = tool.lookupObject(spec['service'])
            if service.UID() == uid:
                assertFalse(min > max & min!=max, "Min-Max inconsistence error")   
                break
                        
        # Reseting values      
        i=0
        for serviceid in serviceids:
            svid = "analysisservice-%s" % serviceid
            sv = bsc(portal_type="AnalysisService", id=svid)[0].getObject()
            uid = sv.UID()  
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid
            browser.getControl(name=minid).value = mininitvalues[i]
            browser.getControl(name=maxid).value = maxinitvalues[i]
            browser.getControl(name=error).value = errorinitvalues[i]
            i+=1
        browser.getControl(name='description').value=descriptioninit
        browser.getControl(name='form.button.save').click();
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite