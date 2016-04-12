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
    # A list with the created rules
    rules_list = []
    # A list with the created methods
    methods_list = []

    def create_methods(self, methods_data):
        """
        Creates a set of methods to be used in the tests
        :methods_data: [{
                'title':'xxx',
                'description':'xxx',
                'Instructions':'xxx',
                'MethodID':'xxx',
                'Accredited':'False/True'},
            ...]
        """
        folder = self.portal.bika_setup.methods
        for meth_d in methods_data:
            _id = folder.invokeFactory('Method', id=tmpID())
            meth = folder[_id]
            meth.edit(
                title=meth_d['title'],
                description=meth_d.get('description', ''),
                Instructions=meth_d.get('Instructions', ''),
                MethodID=meth_d.get('MethodID', ''),
                Accredited=meth_d.get('Accredited', True),
                )
            meth.unmarkCreationFlag()
            renameAfterCreation(meth)
            self.methods_list.append(meth)

    def create_reflex_rules(self, rules_data):
        """
        Given a dict with raflex rules data, it creates the rules
        :rules_data: [{'title':'xxx','description':'xxx',
            'method':method-obj},...]
        """
        # Creating a rule
        folder = self.portal.bika_setup.bika_reflexrulefolder
        for rule_d in rules_data:
            _id = folder.invokeFactory('ReflexRule', id=tmpID())
            rule = folder[_id]
            if not rule_d.get('method', ''):
                # Rise an error
                self.fail(
                    'There is need a method in order to create'
                    ' a reflex rule')
            method = rule_d.get('method')
            rule.edit(
                title=rule_d.get('title', ''),
                description=rule_d.get('description', ''),
                )
            rule.setMethod(method.UID())
            rule.unmarkCreationFlag()
            renameAfterCreation(rule)
            self.rules_list.append(rule)

    def setUp(self):
        super(TestReflexRules, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.rules_list = []
        self.methods_list = []

    def tearDown(self):
        logout()
        super(TestReflexRules, self).tearDown()

    def test_reflex_rule_creation_object(self):
        """
        Testing the object creation and workflow changes
        """
        # Creating the rules
        methods_data = [
            {
                'title': 'Method C',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'mc',
                'Accredited': 'True'
            },
        ]
        self.create_methods(methods_data)
        rules_data = [
            {
                'title': 'Rule C',
                'description': 'A description',
                'method': self.methods_list[-1]
            },
        ]

        self.create_reflex_rules(rules_data)
        # Getting the rule from the system
        pc = getToolByName(self.portal, 'portal_catalog')
        brains = pc(portal_type="ReflexRule")
        self.assertEquals(len(brains), len(rules_data))
        # Getting the rule from the folder
        results = self.portal.bika_setup.bika_reflexrulefolder.items()
        self.assertEquals(len(results), len(rules_data))
        # Changeing state
        for brain in brains:
            obj = brain.getObject()
            doActionFor(obj, 'deactivate')
            self.assertEquals(
                obj.portal_workflow.getInfoFor(obj, 'inactive_state'),
                'inactive')
        # Getting filtered rule
        brains = pc(portal_type="ReflexRule", inactive_state='active')
        self.assertEquals(len(brains), 0)

    def test_reflex_rule_method_selection(self):
        """
        Testing the method bind
        """
        methods_data = [
            {
                'title': 'Method 1',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm1',
                'Accredited': 'True'
            },
        ]
        self.create_methods(methods_data)
        rules_data = [
            {
                'title': 'Rule MS',
                'description': 'A description',
                'method': self.methods_list[-1]
            },
        ]
        self.create_reflex_rules(rules_data)
        rule = self.rules_list[-1]
        self.assertEquals(rule.getMethod().UID(), self.methods_list[-1].UID())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReflexRules))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
