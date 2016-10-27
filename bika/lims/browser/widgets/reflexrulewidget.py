from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from bika.lims.utils import getUsers
from bika.lims.browser.widgets import RecordsWidget
import json

try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite

# Writting the description for the widget
description = """
<p>
When the results become available, some samples may need to be added to the next available worksheet in order to retest it and confirm the result or maybe the result of a previous analysis should be changed depending on the result of the reflexed analysis. These situations can be caused by the indetermination of the result or by a failed test.
</p>
<p>
The aim of this functionality is to create a logic capable of defining some determined actions after submitting or verifying specific results.
</p>
<p>
Basic usage:
</p>
<ul>
<li>Each reflex rule have to be bound to an analysis method using the drop-down list. So, the actions defined inside that reflex rule will be triggered only if the analysis is submitted/verified using this method.
 </li>

<li>Inside the reflex rule the user will be able to add actions for each analysis service belonging to the selected method. In order to improve the flexibility of the system, the user can set some conditions over the analysis service. For instance, the user can restrict the trigger of the actions to only those analyses which a reflex rule has been applied to them. We can expand the restriction introducing the number of times an analysis have been reflexed.
An example of the usage can be a lab that after submitting a result, if this is indeterminate, another test must be done (this is done using reflex rules). If the result is indeterminate two more time, the result of the first (original) analysis will be changed to negative instead of indeterminate.
 </li>

<li>For each analysis service the user can introduce a range of values or a discrete value depending on the result type of the selected analysis (Expected value/s). Then the user has to select from the drop-down list the action to be performed when the result for this analysis and the other conditions are met.
</li>

<li>"Do not apply the actions below if..." allows the system to set how many times this rule can be carried on over the same analysis.
</li>

<li>"Apply the actions below" specifies when the rule has to be checked and carried on.
</li>

<li>Using the 'add action' button, is possible to add more actions for the same result inside an analysis service or add new analysis services and results.
</li>

<li>If there is an analysis service with a defined range and rules but the user wants to add another range and new rules for it, he/she haves to create a new set of rules for the analysis service and define the actions to be done for the new results.
</li>

<li>The rules will be ran top-down, so the rule number one will be ran first, and the same happens withs its actions.
</li>

</ul>
<p>
Worksheet behaviour:
</p>
<ul>
<li>After defining the rule, the user can set the check-box in order to define
 whether the new analysis has to be added in a different worksheet.</li>
<li>If the user doesn't select that option the new analysis will be added to
 the current worksheet (or without worksheet if the analysis does not belong
 to anyone).</li>

<li>If the check-box is set and the user doesn't select an analyst the system
 will look for an open worksheet and it will add the analysis to that
 worksheet, without caring about the analyst. If there are no open worksheets,
 the system will create a new worksheet with an analyst (chosen by the system).

<li>If the check-box is set and the user defines an analyst, the system will
 look for the first worksheet assigned to the analyst. If there is no open
 worksheet for that analyst, the system will create a new worksheet assigned
 to the analyst.</li>
</ul>
<p>
So far there are only three reflex actions: duplicate, replace and set result.
</p>
<ul>
<li>Repeat an analysis means to cancel it and then create a new analysis with
 the same analysis service used for the canceled one (always working with the
 same sample). Attention! It is no possible to repeat a verified analysis, only
 a duplicate is allowed.</li>

<li>Duplicate an analysis consist on creating a new analysis with the same
 analysis service for the same sample. It is used in order to reduce the error
 procedure probability because both results must be similar.</li>

<li>If there are more than one 'repeat' actions for the same result, the system
 will do a 'duplicate' instead of another 'repeat'.</li>

<li>Set the result instruction gives to the analysis a final result depending
 on the result obtained in the last analysis. It can work in two different
 ways, for example you can set the result of the original analysis (the first
 one) and this will change the result on the original one. If you select to
 create a new analysis, it will repeat the analysis and will set the defined
 result.</li>
</ul>
"""


class ReflexRuleWidget(RecordsWidget):
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/reflexrulewidget",
        'helper_js': (
            "bika_widgets/recordswidget.js",
            "bika_widgets/reflexrulewidget.js",),
        'helper_css': (
            "bika_widgets/recordswidget.css",
            "bika_widgets/reflexrulewidget.css",),
        'label': '',
        'description': description,
        'allowDelete': True,
    })

    security = ClassSecurityInfo()

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Gets the values from the ReflexRule section and returns them in the
        correct way to be saved.
        So the function will return a list of dictionaries:
        [{
        'range1': 'X', 'range0': 'X',
        'discreteresult': 'X',
        'trigger': 'xxx',
        'rulenumber': 'number',
        'analysisservice': '<as_uid>', 'value': '',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>', ...},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>', ...},
                ]
        }, ...]
        """
        if field.getName() != 'ReflexRules':
            return RecordsWidget.process_form(
                self, instance, field, form, empty_marker, emptyReturnsMarker)
        raw_data = RecordsWidget.process_form(
            self, instance, field, form, empty_marker, emptyReturnsMarker)
        # 'value' is a list which will be saved
        value = []
        rulenum = 1
        # Building the actions list
        #import pdb; pdb.set_trace()
        for action_set in raw_data[0]:
            d = self._format_actions_set(action_set)
            # Adding the rule number
            d['rulenumber'] = str(rulenum)
            value.append(d)
            rulenum += 1
        return value, {}

    def _format_actions_set(self, action_set):
        """
        This function gets a set of actions with the following format:
        {'analysisservice': '<as_uid>',
        'value': '',
        'range1': '3',
        'range0': '1',
        'discreteresult': '1',
        'action-1': 'repeat',
        'action-0': 'duplicate',
        'otherWS-1': 'on',
        'fromlevel': '2',
        'setresultdiscrete-0': '1',
        'setresulton-0': 'original',
        'setresultvalue': '2'
        'otherresultcondition': Bool,
        'resultcondition': 'repeat',
        'analyst-0': 'sussan1',
        'repetition_max': 2,
        'trigger': 'submit',
        ...}

        and returns a formatted set with the actions sorted like this one:
        {
        'range1': '3', 'range0': '1',
        'analysisservice': '<as_uid>',
        'discreteresult': '1',
        'repetition_max': 2,
        'trigger': 'submit',
        'fromlevel': '2',
        'otherresultcondition': True,
        'resultcondition': 'repeat',
        'value': '',
        'actions':[
            {'action':'duplicate', 'act_row_idx':'0',
                'otherWS': True, 'analyst': 'sussan1',
                'setresultdiscrete': '1', 'setresultvalue': '2',
                'setresulton': 'original'},
            {'action':'repeat', 'act_row_idx':'1',
                'otherWS': False, 'analyst': '', ...},
        ]
        }
        """
        keys = action_set.keys()
        # 'formatted_action_row' is the dict which will be added in the
        # 'value' list
        formatted_action_set = {}
        # Getting the action field names in order to filter the keys later.
        # The names can be found in reflexrulewidget.pt inside the
        # Reflex action rules list section.
        exclude = [
            'action-', 'otherWS-', 'analyst-', 'setresulton-',
            'setresultdiscrete-', 'setresultvalue-']
        action_keys = [k for k in keys if filter(k.startswith, exclude)]
        # Filling the dict with the values that aren't actions
        for key in keys:
            if key in action_keys:
                pass
            elif key == 'otherresultcondition':
                formatted_action_set[key] = True if action_set[key] == 'on'\
                    else False
            else:
                formatted_action_set[key] = action_set[key]
        # Adding the actions list to the final dictionary
        formatted_action_set['actions'] = self._get_sorted_actions_list(
            action_keys, action_set
        )
        return formatted_action_set

    def _get_sorted_actions_list(self, keys_list, action_set):
        """
        This function takes advantatge of the yet filtered 'keys_list'
        and returns a list of dictionaries with the actions from the
        action_set.
        :keys_list: is a list with the keys belonging to the action
            field names'.
        :action_set: is the dict representing a set of actions.
        """
        # actions_dicts_l is the final list which will contain the the
        # dictionaries from raw_index that start with 'action-'.
        # The dictionaries will be sorted by its index
        actions_dicts_l = []
        # a_count is a counter which is incremented every time a new action is
        # added to the list, so we can give it a index.
        a_count = 0
        # actions_list will contain the keys starting with 'action-' but sorted
        # by their index
        actions_list = self._get_sorted_action_keys(keys_list)
        for key in actions_list:
            # Getting the key for otherWS element
            otherWS_key = 'otherWS-'+str(a_count)
            # Getting the value for otherWS checkbox
            otherWS = True if otherWS_key in keys_list \
                and action_set[otherWS_key] == 'on' else False
            # Getting the key for analyst element
            analyst_key = 'analyst-'+str(a_count)
            # Getting the value for analyst
            analyst = action_set.get(analyst_key, '')
            # Getting in which analysis should has its result set
            setresulton_key = 'setresulton-'+str(a_count)
            setresulton = action_set.get(setresulton_key, '')
            # Getting the discrete result to set
            setresultdiscrete_key = 'setresultdiscrete-'+str(a_count)
            setresultdiscrete = action_set.get(setresultdiscrete_key, '')
            # Getting the numeric result to set
            setresultvalue_key = 'setresultvalue-'+str(a_count)
            setresultvalue = action_set.get(setresultvalue_key, '')
            # Building the action dict
            action_dict = {
                'action': action_set[key],
                'act_row_idx': a_count,
                'otherWS': otherWS,
                'analyst': analyst,
                'setresulton': setresulton,
                'setresultdiscrete': setresultdiscrete,
                'setresultvalue': setresultvalue,
                }
            # Saves the action as a new dict inside the actions list
            actions_dicts_l.append(action_dict)
            a_count += 1
        return actions_dicts_l

    def _get_sorted_action_keys(self, keys_list):
        """
        This function returns only the elements starting with 'action-' in
        'keys_list'. The returned list is sorted by the index appended to
        the end of each element
        """
        action_list = []
        for key in keys_list:
            if key.startswith('action-'):
                action_list.append(key)
        action_list.sort()
        return action_list

    def getReflexRuleSetup(self):
        """
        Return a json dict with all the setup data necessary to build the
        relations:
        - Relations between methods and analysis services options.
        - The current saved data
        the functions returns:
        {'<method_uid>': {
            'analysisservices': {
                '<as_uid>': {'as_id': '<as_id>',
                            'as_title':'<as_title>',
                            'resultoptions': [,,]}
                '<as_uid>': {'as_id': '<as_id>',
                            'as_title':'<as_title>',
                            'resultoptions': [{
                                'ResultText': 'Failed',
                                'ResultValue': '1', 'value': ''},
                                ...
                            ]}
            },
          'repetition_max': integer
          'as_keys': ['<as_uid>', '<as_uid>'],
          'method_id': '<method_id>',
          'method_tile': '<method_tile>'
          },
        '<method_uid>': {
            'analysisservices': {
                '<as_uid>': {'as_id': '<as_id>',
                            'as_title':'<as_title>',
                            'resultoptions': [,,]}
               '<as_uid>': {'as_id': '<as_id>',
                            'as_title':'<as_title>',
                            'resultoptions': [,,]}
            },
          'repetition_max': integer
          'as_keys': ['<as_uid>', '<as_uid>'],
          'method_id': '<method_id>',
          'method_tile': '<method_tile>'
          },
         'saved_actions': {'rules': [{'analysisservice': '<as_uid>',
                                        'range0': 'xx',
                                        'range1': 'xx',
                                        'value': '',
                                        'discreteresult': 'X',
                                        'otherWS': Bool,
                                        'analyst': '<analyst_id>'
                                        'repetition_max': integer,
                                        'trigger': 'xxx',
                                    }],
                           'method_id': '<method_uid>',
                           'method_tile': '<method_tile>',
                           'method_uid': '<method_uid>'
                           }
        }
        """
        relations = {}
        # Getting all the methods from the system
        pc = getToolByName(self, 'portal_catalog')
        methods = [obj.getObject() for obj in pc(
                    portal_type='Method',
                    inactive_state='active')]
        for method in methods:
            # Get the analysis services related to each method
            br = method.getBackReferences('AnalysisServiceMethods')
            analysiservices = {}
            for analysiservice in br:
                analysiservices[analysiservice.UID()] = {
                    'as_id': analysiservice.id,
                    'as_title': analysiservice.Title(),
                    'resultoptions':
                        analysiservice.getResultOptions()
                        if analysiservice.getResultOptions()
                        else [],
                }
            # Make the json dict
            relations[method.UID()] = {
                'method_id': method.id,
                'method_tile': method.Title(),
                'analysisservices': analysiservices,
                'as_keys': analysiservices.keys(),
            }
        # Get the data saved in the object
        relations['saved_actions'] = {
            'method_uid': self.aq_parent.getMethod().UID() if
            self.aq_parent.getMethod() else '',
            'method_id': self.aq_parent.getMethod().id if
            self.aq_parent.getMethod() else '',
            'method_tile': self.aq_parent.getMethod().Title() if
            self.aq_parent.getMethod() else '',
            'rules': self.aq_parent.getReflexRules(),
            }
        return json.dumps(relations)

    def getActionVoc(self):
        """
        Return the different action available
        """
        return DisplayList([
            ('repeat', 'Repeat'),
            ('duplicate', 'Duplicate'),
            ('setresult', 'Set result')])

    def getAndOrVoc(self):
        """
        Return the different concatenation options
        """
        return DisplayList([
            ('no', ''),
            ('and', 'AND'),
            ('or', 'OR')])

    def getDefiningResultTo(self):
        """
        Returns where we can define a result.
        """
        return DisplayList([
            ('original', 'Original analysis'), ])
            # ('new', 'New analysis')])

    def getTriggerVoc(self):
        """
        Return the triggeroptions for the rule
        """
        return DisplayList(
            [('submit', 'on analysis submission'),
            ('verify', 'on analysis verification')])

    def getReflexRuleElement(self, idx=0, element=''):
        """
        Returns the expected value saved in the object.
        :idx: it is an integer with the position of the reflex rules set in the
        widget's list.
        :element: a string with the name of the element to obtain:
            'range0/1', 'actions', 'analysisservice',

        The widget is going to return a list like this:
        [
            {'discreteresult': 'X',
            'repetition_max': integer,
            'analysisservice': '<as_uid>', 'value': '',
            'trigger': 'xxx',
            'rulenumber': 'number',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'}
                ]
            },
            {'range1': 'X', 'range0': 'X',
            'analysisservice': '<as_uid>', 'value': '',
            'repetition_max': integer,
            'trigger': 'xxx',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'}
                ]
            },
            {'range1': 'X', 'range0': 'X',
            'analysisservice': '<as_uid>', 'value': '',
            'repetition_max': integer,
            'fromlevel': '2',
            'otherresultcondition': True,
            'resultcondition': 'repeat',
            'trigger': 'xxx',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': Bool, 'analyst': '<analyst_id>'}
                ]
            },
        ]
        - The list is the abstraction of the rules section in a Reflex
        Rule obj.
        - Each dictionary inside the list is an abstraction of a set of rules
        binded to an analysis service.
        - The 'action' element from the dictionary is a list (its order is
        important) with dictionaries where each dict represents a simple
        action.
        - act_row_idx: it is used to know the position numeber of the action
        inside the list.
        """
        rules_list = self.aq_parent.getReflexRules()
        if len(rules_list) > idx:
            value = rules_list[idx].get(element, '')
            if element == 'actions' and value == '':
                return [{'action': '', 'act_row_idx': '0',
                        'otherWS': False, 'analyst': ''}, ]
            elif element == 'repetition_max' and value == '':
                return 2
            else:
                return value
        return [{
                'action': '', 'act_row_idx': '0',
                'otherWS': False, 'analyst': ''
                }] if element == 'actions' else ''

    def getReflexRuleActionElement(self, set_idx=0, row_idx=0, element=''):
        """
        Returns the expected value saved in the action list object.
        :set_idx: it is an integer with the position of the reflex rules set
        in the widget's list.
        :row_idx: is an integer with the numer of the row from the set
        :element: a string with the name of the element of the action to
            obtain: 'action', 'act_row_idx', 'otherWS', 'analyst'
        """
        if isinstance(set_idx, str):
            set_idx = int(set_idx)
        if isinstance(row_idx, str):
            row_idx = int(row_idx)
        actions = self.getReflexRuleElement(idx=set_idx, element='actions')
        return actions[row_idx].get(element, '')

    def getAnalysts(self):
        """
        This function returns a displaylist with the available analysts
        """
        analysts = getUsers(self, ['Manager', 'LabManager', 'Analyst'])
        return analysts.sortedByKey()

registerWidget(
    ReflexRuleWidget,
    title="Reflex Rule Widget",
    description=(
        'Widget to define different actions for an analysis services result'),
    )
