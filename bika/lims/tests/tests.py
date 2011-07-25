"""
    This should use the same data source machine as load_setup_data.

"""

from Products.CMFCore.utils import getToolByName
from bika.lims.browser.load_setup_data import LoadSetupData
from bika.lims.tests.base import BikaTestCase
import unittest

class TestSetup(BikaTestCase):
    """Tests bika installation and setup.




    """

    def test_00(self):

        print self.portal.portal_catalog()
        pass


    def test_01_add_client(self):
        self.setRoles(['Manager',])
        new_id = self.portal.clients.invokeFactory('Client', 'test-client')
        self.assertEquals('test-client', new_id)

    def test_02_nr_of_clients(self):
        # this should fail
        self.setRoles(['Manager',])
        proxies = self.portal.clients.objectValues()
        self.assertEquals(len(proxies), 3)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
