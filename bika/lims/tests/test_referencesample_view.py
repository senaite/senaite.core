from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Products.validation import validation
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import *
from datetime import date
from datetime import datetime
import time
from plone.app.testing import *
from plone.testing import z2
import unittest

class Tests(BikaFunctionalTestCase):

    baseurl = None
    browser = None
    supurl  = "/bika_setup/bika_referencesuppliers/referencesupplier-1/"

    def setUp(self):
        BikaFunctionalTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        self.browser = self.browserLogin()
        self.baseurl = self.browser.url
        
    def newReferenceSample(self):        
        self.browser.open("%s%s%s" % (self.baseurl, self.supurl, "createObject?type_name=ReferenceSample"))
        input_title = self.browser.getControl(name='title')
        list_refdef = self.browser.getControl(name='ReferenceDefinition:list')
        check_blank = self.browser.getControl(name='Blank:boolean')
        check_hazard = self.browser.getControl(name='Hazardous:boolean')
        list_manufc = self.browser.getControl(name='ReferenceManufacturer:list')
        input_catnum = self.browser.getControl(name='CatalogueNumber')
        input_lotnum = self.browser.getControl(name='LotNumber')
        input_remark = self.browser.getControl(name='Remarks')
        input_datesampled = self.browser.getControl(name='DateSampled')
        input_datereceived = self.browser.getControl(name='DateReceived')
        input_dateopened = self.browser.getControl(name='DateOpened')
        input_expirydate = self.browser.getControl(name='ExpiryDate')
        
        title  = 'Blank reference'
        refdef = list_refdef.options[0]
        manufc = list_manufc.options[0]
        catnum = '7627:23-AB.2391222'
        lotnum = 'LHG-32_32.41:20#12'
        remark = 'Remark for Blank reference'       
        
        today = date.today()
        datesampled = today.replace(day=today.day - 2)
        datereceived = today.replace(day=today.day - 1)
        dateopened = today
        expirydate = datesampled.replace(year=datesampled.year + 1)
                
        input_title.value = title
        list_refdef.value = [refdef]
        list_manufc.value = [manufc]
        input_catnum.value= catnum
        input_lotnum.value= lotnum
        input_remark.value= remark
        check_blank.value = True
        check_hazard.value = True
        input_datesampled.value = datesampled.isoformat()
        input_datereceived.value = datereceived.isoformat()
        input_dateopened.value = dateopened.isoformat()
        input_expirydate.value = expirydate.isoformat()
        
        self.browser.getControl(name='form.button.save').click()        
        idref = self.browser.url.replace(("%s%s" % (self.baseurl, self.supurl)), "")
        idref = idref.replace("/base_view", "")
        self.assertTrue(len(idref.strip())>0, "Unable to create new Reference Sample")
        return idref;
    
    def test_AddNewReferenceSample(self):        
        
        idRefSample = self.newReferenceSample()
        editurl = "%s%s%s%s%s" % (self.baseurl, self.supurl, "/", idRefSample, "/base_edit");
        self.browser.open(editurl)
        
        # Check values
        outtitle = self.browser.getControl(name='title').value;
        outrefdef = self.browser.getControl(name='ReferenceDefinition:list').value[0]
        outblank = bool(self.browser.getControl(name='Blank:boolean').value)
        outhazard = bool(self.browser.getControl(name='Hazardous:boolean').value)
        outmanufc = self.browser.getControl(name='ReferenceManufacturer:list').value[0]
        outcatnum = self.browser.getControl(name='CatalogueNumber').value
        outlotnum = self.browser.getControl(name='LotNumber').value
        outremark = self.browser.getControl(name='Remarks').value
        outdatesampled = time.strftime(time.strptime(self.browser.getControl(name='DateSampled').value, '%d %b %Y'), '%Y-%m-%D')
        outdatereceived = time.strftime(time.strptime(self.browser.getControl(name='DateReceived').value, '%d %b %Y'), '%Y-%m-%D')
        outdateopened = time.strftime(time.strptime(self.browser.getControl(name='DateOpened').value, '%d %b %Y'), '%Y-%m-%D')
        outexpirydate = time.strftime(time.strptime(self.browser.getControl(name='ExpiryDate').value, '%d %b %Y'), '%Y-%m-%D')      
                        
        assertEqual(title, outtitle, "Title value doesn't match: %s <> %s" % title, outtitle)
        assertEqual(refdef, outrefdef, "Reference Definition doesn't match: %s <> %s" % refdef, outrefdef)
        assertEqual(manufc, outmanufc, "Reference Manufacturer doesn't match: %s <> %s" % manufc, outmanufc)
        assertEqual(catnum, outcatnum, "Catalogue Number doesn't match: %s <> %s" % catnum, outcatnum)
        assertEqual(lotnum, outlotnum, "Lot Nummber doesn't match: %s <> %s" % lotnum, outlotnum)
        assertEqual(remark, outremark, "Remarks doesn't match: %s <> %s" % remark, outremark)
        assertEqual(datesampled.isoformat(), outdatesampled, "Date Sampled doesn't match: %s <> %s" % datesampled.isoformat(), outdatesampled)
        assertEqual(datereceived.isoformat(), outdatereceived, "Date Received doesn't match: %s <> %s" % datereceived.isoformat(), outdatereceived)
        assertEqual(dateopened.isoformat(), outdateopened, "Date Opened doesn't match: %s <> %s" % dateopened.isoformat(), outdateopened)
        assertEqual(expirydate.isoformat(), outexpirydate, "Expiry Date doesn't match: %s <> %s" % expirydate.isoformat(), outexpirydate)
                
        
    def test_MinMaxValuesEditionIntegrity(self):
        
        idRefSample = self.newReferenceSample()
        editurl = "%s%s%s%s%s" % (self.baseurl, self.supurl, "/", idRefSample, "/base_edit");
        self.browser.open(editurl)        

        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('result.%s:records' % uid)).value = "5"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "0"       
        self.browser.getControl(name='form.button.save').click()
        self.browser.open(editurl)
        
        # Check min and max integrity
        bs = getToolByName(self.portal, 'bika_catalog')
        specsobj = bs(portal_type="ReferenceSample", id=idRefSample)[0].getObject()        
        for spec in specsobj.getReferenceResults():
            if (uid == spec['uid']):
                smin = spec['min']
                smax = spec['max']
                sres = spec['result']
                self.assertFalse(float(smin) > float(smax), "Min-Max inconsistence error (%s > %s)" % (smin, smax))
                self.assertFalse(sres < smin and sres > smax, "Reference sample result %s must be between min %s and max %s values for %s" % (sres, smin, smax, spec['uid']))
                break
            
        self.browser.getControl(name=('result.%s:records' % uid)).value = "15"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "10"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "20"       
        self.browser.getControl(name='form.button.save').click()
        self.browser.open(editurl)        
        
        # Check if result is between min and max values
        bs = getToolByName(self.portal, 'bika_catalog')
        specsobj = bs(portal_type="ReferenceSample", id=idRefSample)[0].getObject()         
        for spec in specsobj.getReferenceResults():
            if (uid == spec['uid']):
                smin = spec['min']
                smax = spec['max']
                sres = spec['result']
                self.assertTrue(sres > smin and sres < smax, "Reference result %s must be between min %s and max %s values for %s" % (sres, smin, smax, spec['uid']))
                break        
            
    
    
    def test_NumericValues(self):
        idRefSample = self.newReferenceSample()
        editurl = "%s%s%s%s%s" % (self.baseurl, self.supurl, "/", idRefSample, "/base_edit");
        self.browser.open(editurl)        
        
        sv = self.bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        uid = sv.UID()
        self.browser.getControl(name=('result.%s:records' % uid)).value = "x"
        self.browser.getControl(name=('min.%s:records' % uid)).value = "x"
        self.browser.getControl(name=('max.%s:records' % uid)).value = "x"    
        self.browser.getControl(name=('error.%s:records' % uid)).value = "x"
        self.browser.getControl(name='form.button.save').click()
        self.browser.open(editurl)  
        
        #Checking after POST
        bs = getToolByName(self.portal, 'bika_catalog')
        specsobj = bs(portal_type="ReferenceSample", id=idRefSample)[0].getObject()         
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
        idRefSample = self.newReferenceSample()
        editurl = "%s%s%s%s%s" % (self.baseurl, self.supurl, "/", idRefSample, "/base_edit");
        self.browser.open(editurl)
        
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
            
        self.browser.getControl(name='form.button.save').click()
        self.browser.open(editurl)  

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite