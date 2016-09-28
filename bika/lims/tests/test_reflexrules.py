from Products.CMFPlone.utils import _createObjectByType
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from bika.lims.idserver import renameAfterCreation
from bika.lims.content.reflexrule import doReflexRuleAction
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
    # A list with the created analysis services
    ans_list = []

    def create_departments(self, department_data):
        """
        Creates a set of departments to be used in the tests
        :department_data: [{
                'title':'xxx',
                },
            ...]
        """
        departments_list = []
        folder = self.portal.bika_setup.bika_departments
        for department_d in department_data:
            _id = folder.invokeFactory('Department', id=tmpID())
            dep = folder[_id]
            dep.edit(
                title=department_d['title'],
                )
            dep.unmarkCreationFlag()
            renameAfterCreation(dep)
            departments_list.append(dep)
        return departments_list

    def create_category(self, category_data):
        """
        Creates a set of analaysis categories to be used in the tests
        :category_data: [{
                'title':'xxx',
                'Department': department object
                },
            ...]
        """
        folder = self.portal.bika_setup.bika_analysiscategories
        categories_list = []
        for category_d in category_data:
            _id = folder.invokeFactory('AnalysisCategory', id=tmpID())
            cat = folder[_id]
            cat.edit(
                title=category_d['title'],
                Department=category_d.get('Department', []),
                )
            cat.unmarkCreationFlag()
            renameAfterCreation(cat)
            categories_list.append(cat)
        return categories_list

    def create_analysisservices(self, as_data):
        """
        Creates a set of analaysis services to be used in the tests
        :as_data: [{
                'title':'xxx',
                'ShortTitle':'xxx',
                'Keyword': 'xxx',
                'PointOfCapture': 'Lab',
                'Category':category object,
                'Methods': [methods object,],
                },
            ...]
        """
        folder = self.portal.bika_setup.bika_analysisservices
        ans_list = []
        for as_d in as_data:
            _id = folder.invokeFactory('AnalysisService', id=tmpID())
            ans = folder[_id]
            ans.edit(
                title=as_d['title'],
                ShortTitle=as_d.get('ShortTitle', ''),
                Keyword=as_d.get('Keyword', ''),
                PointOfCapture=as_d.get('PointOfCapture', 'Lab'),
                Category=as_d.get('Category', ''),
                Methods=as_d.get('Methods', []),
                )
            ans.unmarkCreationFlag()
            renameAfterCreation(ans)
            ans_list.append(ans)
        return ans_list

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
        methods_list = []
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
            methods_list.append(meth)
        return methods_list

    def create_reflex_rules(self, rules_data):
        """
        Given a dict with raflex rules data, it creates the rules
        :rules_data: [{'title':'xxx','description':'xxx',
            'method':method-obj,
            'ReflexRules': [{'actions': [
                              {'act_row_idx': '1',
                               'action': 'repeat',
                               'analyst': 'analyst1',
                               'otherWS': True},
                              {'act_row_idx': '2',
                               'action': 'duplicate',
                               'analyst': 'analyst1',
                               'otherWS': False}],
                  'analysisservice': 'a9df45163f294b2288a369f43c6b0f95',
                  'discreteresult': '',
                  'range0': '5',
                  'range1': '10',
                  'trigger': 'submit',
                  'value': '8'}],...]}
        """
        # Creating a rule
        rules_list = []
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
            reflexrules = rule_d.get('ReflexRules', [])
            rule.edit(
                title=rule_d.get('title', ''),
                description=rule_d.get('description', ''),
                )
            rule.setMethod(method.UID())
            if reflexrules:
                rule.setReflexRules(reflexrules)
            rule.unmarkCreationFlag()
            renameAfterCreation(rule)
            rules_list.append(rule)
        return rules_list

    def setUp(self):
        super(TestReflexRules, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(TestReflexRules, self).tearDown()

    def test_reflex_rule_set_get(self):
        """
        Testing the simple set/get data from the field and the content type
        functions.
        """
        # Creating a department
        department_data = [
            {
                'title': 'dep1',
            }
        ]
        deps = self.create_departments(department_data)
        # Creating a category
        category_data = [{
            'title': 'cat1',
            'Department': deps[0]
            },
        ]
        cats = self.create_category(category_data)
        # Creating a method
        methods_data = [
            {
                'title': 'Method 1',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm1',
                'Accredited': 'True'
            },
        ]
        meths = self.create_methods(methods_data)
        # Creating an analysis service
        as_data = [{
                'title': 'analysis service1',
                'ShortTitle': 'as1',
                'Keyword': 'as1',
                'PointOfCapture': 'Lab',
                'Category': cats[0],
                'Methods': meths,
                },
        ]
        ans_list = self.create_analysisservices(as_data)
        # Creating a rule
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': 2,
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ]
        },]
        rules_data = [
            {
                'title': 'Rule MS',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        self.assertTrue(
            ans_list[-1].UID() == rule.getReflexRules()[0].get(
                'analysisservice', '')
            )
        # Create an analysis Request
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        ar = create_analysisrequest(client, request, values, [ans_list[-1]])
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')
        # Getting the analysis
        analysis = ar.getAnalyses(full_objects=True)[0]
        # Testing reflexrule content type public functions
        result = rule.getExpectedValuesAndRules(analysis, 'submit')
        self.assertEqual(
            result[0]['actions'], rules[0]['actions']
        )
        self.assertEqual(result[0]['expected_values'], ('5', '10'))
        # A result outside the range
        analysis.setResult('11.3')
        result = rule.getActionReflexRules(analysis, 'submit')
        self.assertEqual(
            result, []
        )
        # A result inside the range
        analysis.setResult('6.7')
        result = rule.getExpectedValuesAndRules(analysis, 'submit')
        self.assertEqual(
            result[0]['actions'], rules[0]['actions']
        )
        result = rule.getActionReflexRules(analysis, 'submit')
        expected_result = [{
            'act_row_idx': '1',
            'action': 'repeat',
            'analyst': 'analyst1',
            'otherWS': True,
            'rulename': 'Rule MS',
            'rulenumber': 0
            }, {
            'act_row_idx': '2',
            'action': 'duplicate',
            'analyst': 'analyst1',
            'otherWS': False,
            'rulename': 'Rule MS',
            'rulenumber': 0}]
        self.assertEqual(
            result, expected_result
        )
        # Using a float
        analysis.setResult(6.7)
        result = rule.getExpectedValuesAndRules(analysis, 'submit')
        self.assertEqual(
            result[0]['actions'], expected_result
        )
        result = rule.getActionReflexRules(analysis, 'submit')
        expected_result = [{
            'act_row_idx': '1',
            'action': 'repeat',
            'analyst': 'analyst1',
            'otherWS': True,
            'rulename': 'Rule MS',
            'rulenumber': 0
            }, {
            'act_row_idx': '2',
            'action': 'duplicate',
            'analyst': 'analyst1',
            'otherWS': False,
            'rulename': 'Rule MS',
            'rulenumber': 0}]
        self.assertEqual(
            result, expected_result
        )

    def test_reflex_rule_set_get_wrong_data(self):
        """
        Testing the set/get functions of reflex rules when worng data is
        introduced.
        """
        # Creating a department
        department_data = [
            {
                'title': 'dep2',
            }
        ]
        deps = self.create_departments(department_data)
        # Creating a category
        category_data = [{
            'title': 'cat2',
            'Department': deps[0]
            },
        ]
        cats = self.create_category(category_data)
        # Creating a method
        methods_data = [
            {
                'title': 'Method 2',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm2',
                'Accredited': 'True'
            },
        ]
        meths = self.create_methods(methods_data)
        # Creating an analysis service
        as_data = [{
                'title': 'analysis service2',
                'ShortTitle': 'as2',
                'Keyword': 'as2',
                'PointOfCapture': 'Lab',
                'Category': cats[0],
                'Methods': meths,
                },
        ]
        ans_list = self.create_analysisservices(as_data)
        # Creating a rule without ranges and discrete result
        rules = [{
            'repetition_max': 2,
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ]
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        # There must be a rule without reflex rules
        self.assertEqual(rule.getReflexRules(), [])
        # Creating a rule with wrong analysisservice
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': 2,
            'trigger': 'submit',
            'analysisservice': 'xxx', 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ]
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        # There must be a rule without reflex rules
        self.assertEqual(rule.getReflexRules(), [])
        # Creating a rule with wrong actions
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': 2,
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':{},
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        # There must be a rule without reflex rules
        self.assertEqual(rule.getReflexRules(), [])
        # Creating a rule with wrong repetition_max
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': 'haba',
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ],
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': -1,
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ],
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'repetition_max': 0,
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ],
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        # There must be a rule without reflex rules
        self.assertEqual(rule.getReflexRules(), [])
        # Creating a rule with wrong otherresultscondition
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'otherresultcondition': 'true',
            'repetition_max': 'haba',
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ],
        },]
        rules_data = [
            {
                'title': 'Rule MS 2',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        # There must be a rule without reflex rules
        self.assertEqual(rule.getReflexRules(), [])

    def test_reflex_rule_doReflexRuleAction(self):
        """
        Testing the doReflexRuleAction related functions over analysis.
        """
        # Creating a department
        department_data = [
            {
                'title': 'dep2',
            }
        ]
        deps = self.create_departments(department_data)
        # Creating a category
        category_data = [{
            'title': 'cat2',
            'Department': deps[0]
            },
        ]
        cats = self.create_category(category_data)
        # Creating a method
        methods_data = [
            {
                'title': 'Method 2',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm2',
                'Accredited': 'True'
            },
        ]
        meths = self.create_methods(methods_data)
        # Creating an analysis service
        as_data = [{
                'title': 'analysis service1',
                'ShortTitle': 'as1',
                'Keyword': 'as1',
                'PointOfCapture': 'Lab',
                'Category': cats[0],
                'Methods': meths,
                },
        ]
        ans_list = self.create_analysisservices(as_data)
        actions = [
                  {'action':'duplicate', 'act_row_idx':'1',
                    'otherWS':False, 'analyst': 'analyst1'},
            ]
        # Create an analysis Request
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        ar = create_analysisrequest(client, request, values, ans_list)
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')
        # Set result
        analysis = ar.getAnalyses(full_objects=True)[0]
        analysis.setResult('8')
        # Getting client analysis requests
        pc = getToolByName(ar, 'portal_catalog')
        contentFilter = {'portal_type': 'AnalysisRequest',
                         'cancellation_state': 'active'}
        analysisrequests = pc(contentFilter)
        self.assertEqual(
            len(analysisrequests[0].getObject().getAnalyses()), 1)
        self.assertEqual(
            analysisrequests[0].getObject().getAnalyses()[0].UID,
            analysis.UID())
        doReflexRuleAction(analysis, actions)
        analysisrequests = pc(contentFilter)
        self.assertEqual(
            len(analysisrequests[0].getObject().getAnalyses()), 2)
        self.assertEqual(
            analysisrequests[0].getObject().getAnalyses()[0].UID,
            analysis.UID()
        )
        self.assertNotEqual(
            analysisrequests[0].getObject().getAnalyses()[1].UID,
            analysis.UID()
        )
        # Checking the reflex rule fields in the created analysis
        reflex_analysis = analysisrequests[0].getObject()\
            .getAnalyses()[1].getObject()
        self.assertTrue(reflex_analysis.getIsReflexAnalysis())
        self.assertEqual(
            reflex_analysis.getOriginalReflexedAnalysis().UID(),
            analysis.UID())
        self.assertEqual(
            reflex_analysis.getReflexAnalysisOf().UID(),
            analysis.UID())
        self.assertEqual(
            reflex_analysis.getReflexRuleAction(), 'duplicate')
        self.assertEqual(
            reflex_analysis.getReflexRuleActionLevel(), 1)

    def test_reflex_rule_triggering_the_reflexion(self):
        """
        Testing the doReflexRuleAction using setresult on duplicate.
        """
        # Creating a department
        department_data = [
            {
                'title': 'dep2',
            }
        ]
        deps = self.create_departments(department_data)
        # Creating a category
        category_data = [{
            'title': 'cat2',
            'Department': deps[0]
            },
        ]
        cats = self.create_category(category_data)
        # Creating a method
        methods_data = [
            {
                'title': 'Method 2',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm2',
                'Accredited': 'True'
            },
        ]
        meths = self.create_methods(methods_data)
        # Creating an analysis service
        as_data = [{
                'title': 'analysis service1',
                'ShortTitle': 'as1',
                'Keyword': 'as1',
                'PointOfCapture': 'Lab',
                'Category': cats[0],
                'Methods': meths,
                },
        ]
        ans_list = self.create_analysisservices(as_data)
        actions1 = [
                  {'action':'duplicate', 'act_row_idx':'1',
                    'otherWS':False, 'analyst': 'analyst1'},
            ]
        actions2 = [
                  {'otherresultcondition': True,
                    'resultcondition': 'duplicate',
                    'fromlevel': '1',
                    'action':'setresult',
                    'setresulton': 'next',
                    'setresultvalue': '2',
                    'act_row_idx':'2',
                    'otherWS':False, 'analyst': 'analyst1'},
            ]
        # Create an analysis Request
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        ar = create_analysisrequest(client, request, values, ans_list)
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')
        # Set result
        analysis = ar.getAnalyses(full_objects=True)[0]
        analysis.setResult('8.1')
        # Getting client analysis requests
        pc = getToolByName(ar, 'portal_catalog')
        contentFilter = {'portal_type': 'AnalysisRequest',
                         'cancellation_state': 'active'}
        analysisrequests = pc(contentFilter)
        self.assertEqual(
            len(analysisrequests[0].getObject().getAnalyses()), 1)
        self.assertEqual(
            analysisrequests[0].getObject().getAnalyses()[0].UID,
            analysis.UID())
        # Apply reflex action 'repeat'
        doReflexRuleAction(analysis, actions1)
        analysisrequests = pc(contentFilter)
        self.assertEqual(
            len(analysisrequests[0].getObject().getAnalyses()), 2)
        reflexed_analysis = analysisrequests[0].getObject().getAnalyses()[1]
        reflexed_analysis.getObject().setResult('8.2')
        # Apply reflex action 'setresult'
        doReflexRuleAction(reflexed_analysis.getObject(), actions2)
        self.assertEqual(
            len(analysisrequests[0].getObject().getAnalyses()), 3)
        bac = getToolByName(self.portal, 'bika_analysis_catalog')
        contentFilter_analysis = {
            'portal_type': 'Analysis',
            'sort_on': 'created'}
        analyses = bac(contentFilter_analysis)
        reflexed_analysis_2 = analyses[-1].getObject()
        # Checking the reflex rule fields in the created analysis
        self.assertTrue(reflexed_analysis_2.getIsReflexAnalysis())
        self.assertEqual(
            reflexed_analysis_2.getOriginalReflexedAnalysis().UID(),
            analysis.UID())
        self.assertEqual(
            reflexed_analysis_2.getReflexAnalysisOf().UID(),
            analyses[-2].getObject().UID())
        self.assertTrue(
            reflexed_analysis_2.getReflexRuleActionLevel() == 2)
        self.assertEqual(
            reflexed_analysis_2.getResult(), '2'
            )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReflexRules))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
