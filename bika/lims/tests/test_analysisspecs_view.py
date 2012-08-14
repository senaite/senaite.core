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
        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        sv = bsc(portal_type="AnalysisService", id="analysisservice-53")[0].getObject()
        self.browser.getControl(name=('min.%s:records' % sv.UID())).value = 11
        self.browser.getControl(name=('max.%s:records' % sv.UID())).value = 10
        self.browser.getControl(name='form.button.save').click()
        specsobj = bsc(portal_type="AnalysisSpec", id='analysisspec-2')[0].getObject()
        tool = getToolByName(specsobj, REFERENCE_CATALOG)
        for spec in specsobj.getResultsRange():
            service = tool.lookupObject(spec['service'])
            if service.UID() == uid:
                assertFalse(min > max & min!=max, "Min-Max inconsistence error")
                break

    def test_AnalysisSpecEditionForm(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisspecs/analysisspec-2"))
        primer = 3
        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        descriptioninit = self.browser.getControl(name='description').value
        serviceids = { '53' }#, '43', '44', '10' }
        for serviceid in serviceids:
            sv = bsc(portal_type="AnalysisService",
                     id=("analysisservice-%s" % serviceid))[0].getObject()
            uid = sv.UID()

            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid

            min = self.browser.getControl(name=minid)
            max = self.browser.getControl(name=maxid)
            error = self.browser.getControl(name=errorid)

            # Check initial values
            self.assertTrue(sv.getMin(), min.value, "Incorrect Min init value (%s <> %s) for %s" % (min, sv.getMin(), uid))
            self.assertTrue(sv.getMax(), max.value, "Incorrect Max init value (%s <> %s) for %s" % (max, sv.getMax(), uid))
            self.assertTrue(sv.getError(), error.value, "Incorrect Error init value (%s <> %s) for %s" % (error, sv.getError(), uid))

            min.value = primer * 1
            max.value = primer * 2
            error.value = primer / 3
            primer += 3

        description = 'Apple Pulp Analysis Specification description'
        self.browser.getControl(name='description').value = description
        self.browser.getControl(name='form.button.save').click()

        # Cecking after POST
        primer = 3
        for serviceid in serviceids:
            svid = "analysisservice-%s" % serviceid
            sv = bsc(portal_type="AnalysisService", id=svid)[0].getObject()
            uid = sv.UID()
            minid = 'min.%s:records' % uid
            maxid = 'max.%s:records' % uid
            errorid = 'error.%s:records' % uid
            min = self.browser.getControl(name=minid).value
            max = self.browser.getControl(name=maxid).value
            error = self.browser.getControl(name=error).value
            self.assertTrue(min, primer * 1, "Incorrect Min field value (%s) for %s" % (min, uid))
            self.assertTrue(max, primer * 2, "Incorrect Max field value (%s) for %s" % (min, uid))
            self.assertTrue(error, primer / 3, "Incorrect Error field value (%s) for %s" % (min, uid))
            primer += 3

        desc = self.browser.getControl(name='description').value
        self.assertEqual(desc, description, "Incorrect Description field value (%s <> %s)" % (desc, description))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite