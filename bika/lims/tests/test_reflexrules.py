from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
import unittest

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest

# Tests related with reflex testing
class TestReflexRules(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestReflexRules, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_reflex_rule_creation(self):
        """
        Testing the object creation
        """
        import pdb;pdb.set_trace()
        folder = self.portal.bika_setup.bika_reflexrulefolder
        rule = [_createObjectByType("ReflexRule", folder, tmpID()),
                ]
        rule[0].processForm()
        rule[0].edit(title="Rule 1")

    def tearDown(self):
        logout()
        super(TestReflexRules, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReflexRules))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
