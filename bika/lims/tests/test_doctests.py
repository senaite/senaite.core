from Products.PloneTestCase import PloneTestCase
from Products.validation import validation
from Testing import ZopeTestCase as ztc
from bika.lims import content,browser
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from hashlib import sha1
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
import doctest
import hmac
import json
import plone.protect
import unittest

class TestCase(PloneTestCase.FunctionalTestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def _authenticator(self, user):
        manager = getUtility(IKeyManager)
        secret=manager.secret()
        auth=hmac.new(secret, user, sha1).hexdigest()
        return auth

    def getBrowser(self, loggedIn=False, admin=False):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            u = PloneTestCase.default_user
            p = PloneTestCase.default_password
            browser.open(self.portal.absolute_url() + "/login_form")
            browser.getControl(name='__ac_name').value = u
            browser.getControl(name='__ac_password').value = p
            browser.getControl(name='submit').click()
        return browser

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.browser.sample", test_class=TestCase))
##    suite.addTests(doctest.DocTestSuite(analysis))
##    suite.addTests(doctest.DocTestSuite(analysiscategory))
##    suite.addTests(doctest.DocTestSuite(analysisrequest))
##    suite.addTests(doctest.DocTestSuite(analysisrequestsfolder))
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.content.analysisservice", test_class=TestCase))
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.controlpanel.bika_analysisservices", test_class=TestCase))
##    suite.addTests(doctest.DocTestSuite(analysisservice))
##    suite.addTests(doctest.DocTestSuite(analysisspec))
##    suite.addTests(doctest.DocTestSuite(ar))
##    suite.addTests(doctest.DocTestSuite(ar))
##    suite.addTests(doctest.DocTestSuite(analysisprofile))
##    suite.addTests(doctest.DocTestSuite(artemplate))
##    suite.addTests(doctest.DocTestSuite(attachment))
##    suite.addTests(doctest.DocTestSuite(attachmenttype))
##    suite.addTests(doctest.DocTestSuite(bikaschema))
##    suite.addTests(doctest.DocTestSuite(bikasetup))
##    suite.addTests(doctest.DocTestSuite(calculation))
##    suite.addTests(doctest.DocTestSuite(client))
##    suite.addTests(doctest.DocTestSuite(clientfolder))
##    suite.addTests(doctest.DocTestSuite(contact))
##    suite.addTests(doctest.DocTestSuite(container))
##    suite.addTests(doctest.DocTestSuite(containertype))
##    suite.addTests(doctest.DocTestSuite(department))
##    suite.addTests(doctest.DocTestSuite(duplicateanalysis))
##    suite.addTests(doctest.DocTestSuite(instrument))
##    suite.addTests(doctest.DocTestSuite(invoice))
##    suite.addTests(doctest.DocTestSuite(invoicebatch))
##    suite.addTests(doctest.DocTestSuite(invoicefolder))
##    suite.addTests(doctest.DocTestSuite(invoicelineitem))
##    suite.addTests(doctest.DocTestSuite(labcontact))
##    suite.addTests(doctest.DocTestSuite(laboratory))
##    suite.addTests(doctest.DocTestSuite(labproduct))
##    suite.addTests(doctest.DocTestSuite(logentry))
##    suite.addTests(doctest.DocTestSuite(method))
##    suite.addTests(doctest.DocTestSuite(organisation))
##    suite.addTests(doctest.DocTestSuite(person))
##    suite.addTests(doctest.DocTestSuite(preservation))
##    suite.addTests(doctest.DocTestSuite(pricelist))
##    suite.addTests(doctest.DocTestSuite(pricelistfolder))
##    suite.addTests(doctest.DocTestSuite(pricelistlineitem))
##    suite.addTests(doctest.DocTestSuite(referenceanalysis))
##    suite.addTests(doctest.DocTestSuite(referencedefinition))
##    suite.addTests(doctest.DocTestSuite(referencemanufacturer))
##    suite.addTests(doctest.DocTestSuite(referencesample))
##    suite.addTests(doctest.DocTestSuite(referencesamplesfolder))
##    suite.addTests(doctest.DocTestSuite(referencesupplier))
##    suite.addTests(doctest.DocTestSuite(rejectanalysis))
##    suite.addTests(doctest.DocTestSuite(reports))
##    suite.addTests(doctest.DocTestSuite(sample))
##    suite.addTests(doctest.DocTestSuite(samplepartition))
##    suite.addTests(doctest.DocTestSuite(samplepoint))
##    suite.addTests(doctest.DocTestSuite(samplesfolder))
##    suite.addTests(doctest.DocTestSuite(sampletype))
##    suite.addTests(doctest.DocTestSuite(suppliercontact))
##    suite.addTests(doctest.DocTestSuite(supplyorder))
##    suite.addTests(doctest.DocTestSuite(supplyorderitem))
##    suite.addTests(doctest.DocTestSuite(worksheet))
##    suite.addTests(doctest.DocTestSuite(worksheetfolder))
##    suite.addTests(doctest.DocTestSuite(worksheettemplate))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
