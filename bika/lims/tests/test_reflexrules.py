from Products.CMFPlone.utils import _createObjectByType
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from bika.lims.idserver import renameAfterCreation
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

    def test_reflex_rule_creation_object(self):
        """
        Testing the object creation
        """
        # Creating a rule
        folder = self.portal.bika_setup.bika_reflexrulefolder
        _id = folder.invokeFactory('ReflexRule', id=tmpID())
        rule = folder[_id]
        rule.edit(title="Rule 1", description="A description")
        rule.unmarkCreationFlag()
        renameAfterCreation(rule)
        # Getting the rule from the system
        pc = getToolByName(self.portal, 'portal_catalog')
        brains = pc(portal_type="ReflexRule")
        self.assertEquals(len(brains), 1)
        # Getting the rule from the folder
        results = self.portal.bika_setup.bika_reflexrulefolder.items()
        self.assertEquals(len(results), 1)
        # Changeing state
        obj = brains[0].getObject()
        doActionFor(obj, 'deactivate')
        self.assertEquals(
            obj.portal_workflow.getInfoFor(obj, 'inactive_state'),
            'inactive')
        # Getting filtered rule
        brains = pc(portal_type="ReflexRule", inactive_state='active')
        self.assertEquals(len(brains), 0)

    def tearDown(self):
        logout()
        super(TestReflexRules, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReflexRules))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
