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

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import ReflexRuleWidget
from bika.lims import logger
from bika.lims.utils import isnumber


class ReflexRuleField(RecordsField):

    """The field to manage reflex rule's data """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'fixedSize': 0,
        'minimalSize': 0,
        'maximalSize': 9999,
        'type': 'ReflexRule',
        'subfields': ('rulesset',),
        'subfield_labels': {'rulesset': _('Define the sets of actions'), },
        'widget': ReflexRuleWidget,
        'subfield_validators': {'rulesset': 'reflexrulevalidator', },
        })
    security = ClassSecurityInfo()

    def set(self, instance, rules_list, **kwargs):
        """
        Set the reflexrule field.
        :rules_list: is a list of dictionaries with the following format:
        [{'actions': [{'act_row_idx': 0,
                       'action': 'repeat',
                       'an_result_id': 'rep-1',
                       'analyst': '',
                       'otherWS': 'current',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': ''}],
          'conditions': [{'analysisservice': '52853cf7d5114b5aa8c159afad2f3da1',
                          'and_or': 'no',
                          'cond_row_idx': 0,
                          'discreteresult': '',
                          'range0': '11',
                          'range1': '12'}],
          'mother_service_uid': '52853cf7d5114b5aa8c159afad2f3da1',
          'rulenumber': '0',
          'trigger': 'submit'},
         {'actions': [{'act_row_idx': 0,
                       'action': 'repeat',
                       'an_result_id': 'rep-2',
                       'analyst': '',
                       'otherWS': 'current',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': ''},
                      {'act_row_idx': 1,
                       'action': 'repeat',
                       'an_result_id': 'rep-4',
                       'analyst': 'analyst1',
                       'otherWS': 'to_another',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': '70d48adfb34c4231a145f76a858e94cf'},
                      {'act_row_idx': 2,
                       'action': 'repeat',
                       'an_result_id': 'rep-5',
                       'analyst': '',
                       'otherWS': 'create_another',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': ''},
                      {'act_row_idx': 3,
                       'action': 'repeat',
                       'an_result_id': 'rep-6',
                       'analyst': '',
                       'otherWS': 'no_ws',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': ''}],
          'conditions': [{'analysisservice': 'rep-1',
                          'and_or': 'no',
                          'cond_row_idx': 0,
                          'discreteresult': '',
                          'range0': '12',
                          'range1': '12'}],
          'mother_service_uid': '52853cf7d5114b5aa8c159afad2f3da1',
          'rulenumber': '1',
          'trigger': 'submit'},
         {'actions': [{'act_row_idx': 0,
                       'action': 'repeat',
                       'an_result_id': 'rep-3',
                       'analyst': '',
                       'otherWS': 'current',
                       'setresultdiscrete': '',
                       'setresulton': 'original',
                       'setresultvalue': '',
                       'worksheettemplate': ''}],
          'conditions': [{'analysisservice': 'rep-1',
                          'and_or': 'and',
                          'cond_row_idx': 0,
                          'discreteresult': '',
                          'range0': '12',
                          'range1': '12'},
                         {'analysisservice': 'rep-2',
                          'and_or': 'or',
                          'cond_row_idx': 1,
                          'discreteresult': '',
                          'range0': '115',
                          'range1': '115'},
                         {'analysisservice': 'rep-1',
                          'and_or': 'no',
                          'cond_row_idx': 2,
                          'discreteresult': '',
                          'range0': '14',
                          'range1': '14'}],
          'mother_service_uid': '52853cf7d5114b5aa8c159afad2f3da1',
          'rulenumber': '2',
          'trigger': 'submit'}]
        This list of dictionaries is how the system will store the reflexrule
        field info. This dictionaries must be in sync with the
        browser/widgets/reflexrulewidget.py/process_form() dictionaries format.
        """
        for d in rules_list:
            # Checking if all dictionary items are correct
            if not _check_set_values(instance, d):
                RecordsField.set(self, instance, [], **kwargs)
        RecordsField.set(self, instance, rules_list, **kwargs)


def _check_set_values(instance, dic):
    """
    This function checks if the dict values are correct.
    :instance: the object instance. Used for querying
    :dic: is a dictionary with the following format:
    {'actions': [{'act_row_idx': 0,
                   'action': 'repeat',
                   'an_result_id': 'rep-1',
                   'analyst': '',
                   'otherWS': 'current',
                   'setresultdiscrete': '',
                   'setresulton': 'original',
                   'setresultvalue': '',
                   'worksheettemplate': ''}],
      'conditions': [{'analysisservice': '52853cf7d5114b5aa8c159afad2f3da1',
                      'and_or': 'no',
                      'cond_row_idx': 0,
                      'discreteresult': '',
                      'range0': '11',
                      'range1': '12'}],
      'mother_service_uid': '52853cf7d5114b5aa8c159afad2f3da1',
      'rulenumber': '0',
      'trigger': 'submit'},
    These are the checking rules:
        :range0/range1: string or number.
    They are the numeric range within the action will be
    carried on. It is needed to keep it as None or '' if the discreteresult
    is going to be used instead.
        :discreteresult: string
    If discreteresult is not Null, ranges have to be Null.
        :trigger: string.
    So far there are only two options: 'submit'/'verify'. They are defined
    in browser/widgets/reflexrulewidget.py/ReflexRuleWidget/getTriggerVoc.
        :analysisservice: it is the uid of an analysis service
        :actions: It is a list of dictionaries with the following format:
    [{'action':'<action_name>', 'act_row_idx':'X',
                'otherWS':Bool, 'analyst': '<analyst_id>'},
              {'action':'<action_name>', 'act_row_idx':'X',
                'otherWS':Bool, 'analyst': '<analyst_id>'},
        ]
        :'repetition_max': integer or string representing an integer.
    <action_name> options are found in
    browser/widgets/reflexrulewidget.py/ReflexRuleWidget/getActionVoc
    so far.
    """
    uc = getToolByName(instance, 'uid_catalog')
    rulenumber = dic.get('rulenumber', '0')
    if rulenumber and not(isnumber(rulenumber)):
        logger.warn('The range must be a number. Now its value is: '
                    '%s' % (rulenumber))
        return False
    trigger = dic.get('trigger', 'submit')
    if trigger not in ['submit', 'verify']:
        logger.warn('Only available triggers are "verify" or "submit". '
                    '%s has been introduced.' % (trigger))
        return False
    mother_service_uid = dic.get('mother_service_uid', '')
    as_brain = uc(UID=mother_service_uid)
    if not as_brain:
        logger.warn(
            'Not correct analysis service with UID. %s' % (mother_service_uid))
        return False
    # Checking the conditions
    conditions = dic.get('conditions', [])
    if not conditions or not _check_conditions(instance, conditions):
        return False
    # Checking the actions
    actions = dic.get('actions', [])
    if not actions or not _check_actions(instance, actions):
        return False
    return True


def _check_conditions(instance, conditions):
    uc = getToolByName(instance, 'uid_catalog')
    for condition in conditions:
        range0 = condition.get('range0', None)
        range1 = condition.get('range1', None)
        discreteresult = condition.get('discreteresult', None)
        analysisservice = condition.get('analysisservice', None)
        and_or = condition.get('and_or', 'no')
        cond_row_idx = condition.get('cond_row_idx', None)
        as_brain = uc(UID=analysisservice)
        if (not discreteresult and (not range0 or not range1)) or \
                (discreteresult and range0 and range1):
            logger.warn(_(
                'If range values are empty, discreteresult must contain a '
                'value, and if discreteresult has a value, ranges must be '
                'empty. But ranges or discreteresult must conatin a value.'
                'The given values are: '
                'discreteresult: %s, range0: %s, range1: %s'
                % (discreteresult, range0, range1)))
            return False
        if range1 and not(isnumber(range1)):
            logger.warn('The range must be a number. Now its value is: '
                        '%s' % (range1))
            return False
        if range0 and not(isnumber(range0)):
            logger.warn('The range must be a number. Now its value is: '
                        '%s' % (range0))
            return False
        if not as_brain:
            logger.warn(
                'Not correct analysis service with UID. %s' %
                (analysisservice))
            return False
        if and_or not in ['and', 'or', 'no']:
            logger.warn(
                'Not correct and_or value')
            return False
        if cond_row_idx and not(isnumber(cond_row_idx)):
            logger.warn('The cond_row_idx must be a number. Now its value is: '
                        '%s' % (cond_row_idx))
            return False
    return True


def _check_actions(instance, actions):
    uc = getToolByName(instance, 'uid_catalog')
    for action in actions:
        act_row_idx = action.get('act_row_idx', '0')
        action_name = action.get('action', '')
        an_result_id = action.get('an_result_id', '')
        analyst = action.get('analyst', '')
        otherWS = action.get('otherWS', 'current')
        setresultdiscrete = action.get('setresultdiscrete', '')
        setresulton = action.get('setresulton', '')
        setresultvalue = action.get('setresultvalue', '')
        worksheettemplate = action.get('worksheettemplate', '')
        wt_brain = uc(UID=worksheettemplate)
        if act_row_idx and not(isnumber(act_row_idx)):
            logger.warn('The act_row_idx must be a number. Now its value is: '
                        '%s' % (act_row_idx))
            return False
        if action_name not in ['repeat', 'duplicate', 'setresult','setvisibility']:
            logger.warn(
                'Not correct action_name value')
            return False
        if otherWS not in ['current', 'to_another', 'create_another', 'no_ws']:
            logger.warn(
                'Not correct otherWS value')
            return False
        if setresulton not in ['original', 'bew']:
            logger.warn(
                'Not correct setresulton value')
            return False
        if setresultvalue and not(isnumber(setresultvalue)):
            logger.warn(
                'The setresultvalue must be a number. Now its value is: '
                '%s' % (setresultvalue))
            return False
        if worksheettemplate and not wt_brain:
            logger.warn(
                'Not correct worksheet template with UID. %s' %
                (worksheettemplate))
            return False
    return True
