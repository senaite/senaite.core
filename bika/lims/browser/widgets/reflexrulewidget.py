from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from bika.lims.browser.widgets import RecordsWidget
import json

try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite


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
        'description':
            'Add actions for each analysis service belonging to the'
            ' selected method',
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
        'analysisservice': '<as_uid>', 'value': '',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X'},
                      {'action':'<action_name>', 'act_row_idx':'X'}
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
        # Building the actions list
        for action_set in raw_data[0]:
            value.append(self._format_actions_set(action_set))
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
        ...}

        and returns a formatted set with the actions sorted like this one:
        {
        'range1': '3', 'range0': '1',
        'analysisservice': '<as_uid>',
        'discreteresult': '1',
        'value': '',
            'actions':[
                {'action':'duplicate', 'act_row_idx':'0'},
                {'action':'repeat', 'act_row_idx':'1'}
            ]
        }
        """
        keys = action_set.keys()
        # 'formatted_action_row' is the dict which will be added in the
        # 'value' list
        formatted_action_set = {}
        # Filling the dict with the none action values
        for key in keys:
            if key.startswith('action-'):
                pass
            else:
                formatted_action_set[key] = action_set[key]
        # Adding the actions list to the final dictionary
        formatted_action_set['actions'] = self._get_sorted_actions_list(
            keys, action_set
        )
        return formatted_action_set

    def _get_sorted_actions_list(self, keys_list, action_set):
        """
        This function takes advantatge of the yet filtered 'keys_list'
        and returns a list of dictionaries with the actions from the action_set.
        :keys_list: is a list with the keys starting with 'action-' in the
            'action_set'.
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
            # Building the action dict
            action_dict = {
                'action': action_set[key], 'act_row_idx': a_count}
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
        {'<method_uid>': {'analysisservices': {'<as_uid>': {'as_id': '<as_id>',
                                                            'as_title':'<as_title>',
                                                            'resultoptions': [,,]}
                                               '<as_uid>': {'as_id': '<as_id>',
                                                            'as_title':'<as_title>',
                                                            'resultoptions': [
                                                                {'ResultText': 'Failed', 'ResultValue': '1', 'value': ''},
                                                                ...
                                                            ]}
                                            },
                          'as_keys': ['<as_uid>', '<as_uid>'],
                          'method_id': '<method_id>',
                          'method_tile': '<method_tile>'
                          },
        '<method_uid>': {'analysisservices': {'<as_uid>': {'as_id': '<as_id>',
                                                            'as_title':'<as_title>',
                                                            'resultoptions': [,,]}
                                               '<as_uid>': {'as_id': '<as_id>',
                                                            'as_title':'<as_title>',
                                                            'resultoptions': [,,]}
                                            },
                          'as_keys': ['<as_uid>', '<as_uid>'],
                          'method_id': '<method_id>',
                          'method_tile': '<method_tile>'
                          },
         'saved_actions': {'rules': [{'analysisservice': '<as_uid>',
                                        'range0': 'xx',
                                        'range1': 'xx',
                                        'value': '',
                                        'discreteresult': 'X'
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
        return DisplayList(
            [('repeat', 'Repeat'), ('duplicate', 'Duplicate')])

    def getReflexRuleElement(self, idx=0, element=''):
        """
        Returns the expected value saved in the object.
        :idx: it is an integer with the position of the reflex rules set in the
        widget's list.
        :element: a string with the elemen's name to obtain:
            'range0/1', 'actions', 'analysisservice',

        The widget is going to return a list like this:
        [
            {'discreteresult': 'X', 'analysisservice': '<as_uid>', 'value': '',
                'actions':[{'action':'<action_name>', 'act_row_idx':'X'},
                          {'action':'<action_name>', 'act_row_idx':'X'}
                    ]
            },
            {'range1': 'X', 'range0': 'X', 'analysisservice': '<as_uid>', 'value': '',
                'actions':[{'action':'<action_name>', 'act_row_idx':'X'},
                          {'action':'<action_name>', 'act_row_idx':'X'}
                    ]
            },
            {'range1': 'X', 'range0': 'X', 'analysisservice': '<as_uid>', 'value': '',
                'actions':[{'action':'<action_name>', 'act_row_idx':'X'},
                          {'action':'<action_name>', 'act_row_idx':'X'}
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
                return [{'action': '', 'act_row_idx': '0'}, ]
            else:
                return value
        return [
            {'action': '', 'act_row_idx': '0'}] if element == 'actions' else ''

registerWidget(
    ReflexRuleWidget,
    title="Reflex Rule Widget",
    description=(
        'Widget to define different actions for an analysis services result'),
    )
