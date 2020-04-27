# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets.reflexrulewidget_description import description
from bika.lims.utils import getUsers

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

        [...,{
            'conditions':[{
                'range1': 'X', 'range0': 'X',
                'cond_row_idx':'X'
                'and_or': 'and',
                'analysisservice': '<as_uid>',
                }, {...}],
            'trigger': 'xxx',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                            'otherWS':'to_another', 'analyst': '<analyst_id>',
                            'an_result_id':'rep-1',...},
                    ]
        },
        {
            'conditions':[{
                'range1': 'X', 'range0': 'X',
                'trigger': 'xxx',
                'cond_row_idx':'X'
                'and_or': 'and',
                'analysisservice': '<as_uid>',
                },
                {
                'discreteresult': 'X',
                'trigger': 'xxx',
                'cond_row_idx':'X'
                'and_or': 'and',
                'analysisservice': '<as_uid>',
                }, {...}],
            'trigger': 'xxx',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':to_another, 'analyst': '<analyst_id>',
                        'an_result_id':'rep-1',...},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':to_another, 'analyst': '<analyst_id>',
                        'an_result_id':'rep-2'...},
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
        rulenum = 0
        # Building the actions and conditions list
        for raw_set in raw_data[0]:
            d = self._format_conditions_and_actions(raw_set)
            # Adding the rule number
            d['rulenumber'] = str(rulenum)
            # Filling the dict with the mother service UID
            d['mother_service_uid'] = raw_data[0][0].get(
                'analysisservice-0', '')
            value.append(d)
            rulenum += 1

        return value, {}

    def _format_conditions_and_actions(self, raw_data):
        """
        This function gets a set of actions and conditionswith the following
        format:

         {'action-0': 'repeat',
          'action-1': 'repeat',
          'analysisservice-0': '30cd952b0bb04a05ac27b70ada7feab2',
          'analysisservice-1': '30cd952b0bb04a05ac27b70ada7feab2',
          'and_or-0': 'and',
          'and_or-1': 'no',
          'range0-0': '12',
          'range0-1': '31',
          'range1-0': '12',
          'range1-1': '33',
          'worksheettemplate-0': '70d48adfb34c4231a145f76a858e94cf',
          'setresulton-0': 'original',
          'setresulton-1': 'original',
          'trigger': 'submit',
          'value': '',
          'an_result_id-0':'rep-1',
          'an_result_id-1':'rep-2'}

        and returns a formatted set with the conditions and actions sorted
        like this one:
        {
        'conditions':[{
            'range1': 'X', 'range0': 'X',
            'cond_row_idx':'X'
            'and_or': 'and',
            'analysisservice': '<as_uid>',
            },
            {
            'range1': 'X', 'range0': 'X',
            'cond_row_idx':'X'
            'and_or': 'and',
            'analysisservice': '<as_uid>',
            }, {...}],
        'trigger': 'xxx',
        'actions':[
            {'action':'duplicate', 'act_row_idx':'0',
                'otherWS': to_another, 'analyst': 'sussan1',
                'setresultdiscrete': '1', 'setresultvalue': '2',
                'worksheettemplate-0': '70d48adfb34c4231a145f76a858e94cf',
                'setresulton': 'original','an_result_id-0':'rep-1'},
            {'action':'repeat', 'act_row_idx':'1',
                'otherWS': current, 'analyst': '', ...},
        ]
        }
        """
        keys = raw_data.keys()
        # 'formatted_action_row' is the dict which will be added in the
        # 'value' list
        formatted_set = {}
        # Filling the dict with the values that aren't actions or conditions
        formatted_set['trigger'] = raw_data.get('trigger', '')
        # Adding the conditions list to the final dictionary
        formatted_set['conditions'] = self._get_sorted_conditions_list(
            raw_data)
        # Adding the actions list to the final dictionary
        formatted_set['actions'] = self._get_sorted_actions_list(raw_data)
        return formatted_set

    def _get_sorted_conditions_list(self, raw_set):
        """
        This returns a list of dictionaries with the conditions got in the
        raw_set.
        :raw_set: is the dict representing a set of rules and conditions.
        """
        keys_list = raw_set.keys()
        # cond_dicts_l is the final list which will contain the the
        # dictionaries with the conditions.
        # The dictionaries will be sorted by the index obtained in the
        # template.
        cond_dicts_l = []
        # c_count is a counter which is incremented every time a new cond is
        # added to the list, so we can give it a index.
        c_count = 0
        # cond_list will contain the keys starting with 'analysisservice-'
        # but sorted by their index
        cond_list = self._get_sorted_cond_keys(keys_list)
        for key in cond_list:
            range0_key = 'range0-'+str(c_count)
            range0 = raw_set.get(range0_key, '')
            range1_key = 'range1-'+str(c_count)
            range1 = raw_set.get(range1_key, '')
            discreteresult_key = 'discreteresult-'+str(c_count)
            discreteresult = raw_set.get(discreteresult_key, '')
            and_or_key = 'and_or-'+str(c_count)
            and_or = raw_set.get(and_or_key, '')
            # Building the conditions dict
            cond_dict = {
                'analysisservice': raw_set[key],
                'cond_row_idx': c_count,
                'range0': range0,
                'range1': range1,
                'discreteresult': discreteresult,
                'and_or': and_or,
                }
            # Saves the conditions as a new dict inside the actions list
            cond_dicts_l.append(cond_dict)
            c_count += 1
        return cond_dicts_l

    def _get_sorted_cond_keys(self, keys_list):
        """
        This function returns only the elements starting with
        'analysisservice-' in 'keys_list'. The returned list is sorted by the
        index appended to the end of each element
        """
        # The names can be found in reflexrulewidget.pt inside the
        # conditionscontainer div.
        cond_list = []
        for key in keys_list:
            if key.startswith('analysisservice-'):
                cond_list.append(key)
        cond_list.sort()
        return cond_list

    def _get_sorted_actions_list(self, raw_set):
        """
        This returns a list of dictionaries with the actions got in the
        raw_set.
        :raw_set: is the dict representing a set of rules and conditions.
        """
        keys_list = raw_set.keys()
        # actions_dicts_l is the final list which will contain the the
        # dictionaries with the actions.
        # The dictionaries will be sorted by the index obtained in the
        # template.
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
            # Getting the value for otherWS selector
            otherWS = raw_set.get(otherWS_key, '')
            # Getting the key for analyst element
            analyst_key = 'analyst-'+str(a_count)
            # Getting the value for analyst
            analyst = raw_set.get(analyst_key, '')
            # Getting which analysis should has its result set
            setresulton_key = 'setresulton-'+str(a_count)
            setresulton = raw_set.get(setresulton_key, '')
            # Getting the discrete result to set
            setresultdiscrete_key = 'setresultdiscrete-'+str(a_count)
            setresultdiscrete = raw_set.get(setresultdiscrete_key, '')
            # Getting the numeric result to set
            setresultvalue_key = 'setresultvalue-'+str(a_count)
            setresultvalue = raw_set.get(setresultvalue_key, '')
            # Getting the local analysis id
            local_id_key = 'an_result_id-'+str(a_count)
            local_id = raw_set.get(local_id_key, '')
            # Getting the local analysis id
            worksheettemplate_key = 'worksheettemplate-'+str(a_count)
            worksheettemplate = raw_set.get(worksheettemplate_key, '')
            # Getting the visibility in report
            showinreport_key = 'showinreport-'+str(a_count)
            showinreport = raw_set.get(showinreport_key, '')
            # Getting the analysis to show or hide in report
            setvisibilityof_key = 'setvisibilityof-'+str(a_count)
            setvisibilityof = raw_set.get(setvisibilityof_key, '')
            # Building the action dict
            action_dict = {
                'action': raw_set[key],
                'act_row_idx': a_count,
                'otherWS': otherWS,
                'worksheettemplate': worksheettemplate,
                'analyst': analyst,
                'setresulton': setresulton,
                'setresultdiscrete': setresultdiscrete,
                'setresultvalue': setresultvalue,
                'an_result_id': local_id,
                'showinreport': showinreport,
                'setvisibilityof': setvisibilityof,
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
        # The names can be found in reflexrulewidget.pt inside the
        # Reflex action rules list section.
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
          'as_keys': ['<as_uid>', '<as_uid>'],
          'method_id': '<method_id>',
          'method_tile': '<method_tile>'
          },
         'saved_actions': {'rules': [
                    {'actions': [{'act_row_idx': 0,
                                   'action': 'repeat',
                                   'an_result_id': '',
                                   'analyst': '',
                                   'otherWS': current,
                                   'setresultdiscrete': '',
                                   'setresulton': 'original',
                                   'setresultvalue': '',
                                   'worksheettemplate': '70d48adfb34c4231a145f76a858e94cf',}],
                      'conditions': [{'analysisservice': 'd802cdbf1f4742c094d45997b1038f9c',
                                      'and_or': 'no',
                                      'cond_row_idx': 0,
                                      'discreteresult': '',
                                      'range0': '12',
                                      'range1': '12'}],
                      'rulenumber': '1',
                      'trigger': 'submit'},...],
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
                    is_active=True)]
        bsc = getToolByName(self, 'bika_setup_catalog')
        for method in methods:
            # Get the analysis services related to each method
            an_servs_brains = bsc(
                portal_type='AnalysisService',
                getMethodUIDs={
                    "query": method.UID(),
                    "operator": "or"
                })
            analysiservices = {}
            for analysiservice in an_servs_brains:
                analysiservice = analysiservice.getObject()
                # Getting the worksheet templates that could be used with the
                # analysis, those worksheet templates are the ones without
                # method and the ones with a method shared with the
                # analysis service.
                service_methods_uid = analysiservice.getAvailableMethodUIDs()
                query_dict = {
                    'portal_type': 'WorksheetTemplate',
                    'is_active': True,
                    'sort_on': 'sortable_title',
                    'getMethodUID': {
                        "query": service_methods_uid + [''],
                        "operator": "or"
                    }
                }
                wst_brains = bsc(query_dict)
                analysiservices[analysiservice.UID()] = {
                    'as_id': analysiservice.getId(),
                    'as_title': analysiservice.Title(),
                    'resultoptions':
                        analysiservice.getResultOptions()
                        if analysiservice.getResultOptions()
                        else [],
                    'wstoptions': [
                        (brain.UID, brain.Title) for brain in wst_brains]
                }
            # Make the json dict
            relations[method.UID()] = {
                'method_id': method.getId(),
                'method_tile': method.Title(),
                'analysisservices': analysiservices,
                'as_keys': analysiservices.keys(),
            }
        # Get the data saved in the object
        reflex_rule = self.aq_parent.aq_inner
        saved_method = reflex_rule.getMethod()
        relations['saved_actions'] = {
            'method_uid': saved_method.UID() if
            saved_method else '',
            'method_id': saved_method.getId() if
            saved_method else '',
            'method_tile': saved_method.Title() if
            saved_method else '',
            'rules': reflex_rule.getReflexRules(),
            }
        return json.dumps(relations)

    def getActionVoc(self):
        """
        Return the different action available
        """
        return DisplayList([
            ('repeat', _('Repeat')),
            ('duplicate', _('Duplicate')),
            ('setresult', _('Set result')),
            ('setvisibility', _('Set Visibility'))])

    def getShowInRepVoc(self):
        """
        Return the different Visibility in Report values.
        """
        return DisplayList([
            ('default', _('Visibility (default)')),
            ('visible', _('Show in Report')),
            ('invisible', _('Hide In Report'))])

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
            ('original', 'Original analysis'),
            ('new', 'New analysis')])

    def getTriggerVoc(self):
        """
        Return the triggeroptions for the rule
        """
        return DisplayList([
            ('submit', 'on analysis submission'),
            ('verify', 'on analysis verification')])

    def getWorksheetOptionsVoc(self):
        """
        Return the the available options to carry on realted with a worksheet
        """
        return DisplayList([
            ('current', "To the current worksheet"),
            ('to_another', "To another worksheet"),
            ('create_another', "Create another worksheet"),
            ('no_ws', "No worksheet")])

    def getReflexRuleElement(self, idx=0, element=''):
        """
        Returns the expected value saved in the object.
        :idx: it is an integer with the position of the reflex rules set in the
        widget's list.
        :element: a string with the name of the element to obtain:
            'actions', 'trigger', 'conditions',

        The widget is going to return a list like this:
        [
            {'conditions': [{'analysisservice': '<as-id>',
                            'and_or': 'no',
                            'cond_row_idx': 0,
                            'discreteresult': '',
                            'range0': '12',
                            'range1': '12'}}]
            'trigger': 'xxx',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': 'to_another', 'analyst': '<analyst_id>',...},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS': 'to_another', 'analyst': '<analyst_id>'}
                ]
            }, ...]
        - The list is the abstraction of the rules section in a Reflex
        Rule obj.
        - Each dictionary inside the list is an abstraction of a set of
        conditions and actions to be done if the conditions are met.
        - The 'action' element from the dictionary is a list (its order is
        important) with dictionaries where each dict represents a simple
        action.
        - The 'conditions' element from the dictionary is a list (its order is
        important) with dictionaries where each dict represents a condition.
        - act_row_idx: it is used to know the position numeber of the action
        inside the list.
        - cond_row_idx: it is used to know the position numeber of the
        condition inside the list.
        """
        rules_list = self.aq_parent.aq_inner.getReflexRules()
        if len(rules_list) > idx:
            value = rules_list[idx].get(element, '')
            if element == 'actions' and value == '':
                return [{'action': '', 'act_row_idx': '0',
                        'otherWS': 'current', 'analyst': '',
                        'setresulton': '', 'setresultdiscrete': '',
                        'worksheettemplate': '',
                        'setresultvalue': '', 'an_result_id': ''}, ]
            elif element == 'conditions' and value == '':
                return [{'analysisservice': '', 'cond_row_idx': '0',
                        'range0': '', 'range1': '',
                        'discreteresult': '', 'and_or': 'no'}, ]
            else:
                return value
        if element == 'actions':
            return [{'action': '', 'act_row_idx': '0',
                    'otherWS': 'current', 'analyst': '',
                    'worksheettemplate': '',
                    'setresulton': '', 'setresultdiscrete': '',
                    'setresultvalue': '', 'an_result_id': ''}, ]
        elif element == 'conditions':
            return [{'analysisservice': '', 'cond_row_idx': '0',
                    'range0': '', 'range1': '',
                    'discreteresult': '', 'and_or': 'no'}, ]
        else:
            return ''

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

    def getReflexRuleConditionElement(self, set_idx=0, row_idx=0, element=''):
        """
        Returns the expected value saved in the action list object.
        :set_idx: it is an integer with the position of the reflex rules set
        in the widget's list.
        :row_idx: is an integer with the numer of the row from the set
        :element: a string with the name of the element of the action to
            obtain: 'analysisservice', 'cond_row_idx', 'range0', 'range1',
                    'discreteresult', and_or
        """
        if isinstance(set_idx, str):
            set_idx = int(set_idx)
        if isinstance(row_idx, str):
            row_idx = int(row_idx)
        cond = self.getReflexRuleElement(idx=set_idx, element='conditions')
        return cond[row_idx].get(element, '')

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
