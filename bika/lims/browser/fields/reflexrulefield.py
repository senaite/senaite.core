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
        [{
        'discreteresult': 'X',
        'trigger': 'xxx',
        'fromlevel': '2',
        'otherresultcondition': 'on',
        'resultcondition': 'repeat',
        'repetition_max': 'x'/integer,
        'analysisservice': '<as_uid>', 'value': '',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>'},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>'},
                ]
        },
        {
        'range1': 'X', 'range0': 'X',
        'trigger': 'xxx',
        'repetition_max': 'x'/integer,
        'analysisservice': '<as_uid>', 'value': '',
            'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>'},
                      {'action':'<action_name>', 'act_row_idx':'X',
                        'otherWS':Bool, 'analyst': '<analyst_id>'},
                ]
        ...]
        This list of dictionaries is how the system will store the reflexrule
        field info. This dictionaries must be in sync with the
        browser/widgets/reflexrulewidget.py/process_form() dictionaries format.
        """
        final_list = []
        for d in rules_list:
            # Checking if all dictionary items are correct
            if _check_set_values(instance, d):
                # checking actions
                action_idx = 0
                for action in d['actions']:
                    if type(action) not in (dict,):
                        logger.warn('Each action must be a dict.')
                        return False
                    if action.get('action', '') not in \
                            ('repeat', 'duplicate', 'setresult'):
                        logger.warn(
                            'Action %s does not exist' %
                            action.get('action', ''))
                        return False
                    if not action.get('act_row_idx', '') or\
                            not isnumber(action.get('act_row_idx')):
                            action['act_row_idx'] = action_idx
                    action['act_row_idx'] = str(action['act_row_idx'])
                    action_idx += 1
                final_list.append(d)
        RecordsField.set(self, instance, final_list, **kwargs)


def _check_set_values(instance, dic):
    """
    This function check if the dict values are correct. It doesn't look
    into the action list.
    :instance: the object instance. Used for querying
    :dic: is a dictionary with the following format:
    {
    'range1': 'X', 'range0': 'X', 'discreteresult': 'X',
    'trigger': 'xxx',
    'fromlevel': '2',
    'otherresultcondition': Bool,
    'resultcondition': 'repeat',
    'repetition_max': 'x'/integer,
    'analysisservice': '<as_uid>', 'value': '',
        'actions':[{'action':'<action_name>', 'act_row_idx':'X',
                    'otherWS':Bool, 'analyst': '<analyst_id>',
                    'setresultdiscrete': '1', 'setresulton': 'previous',
                    'setresultvalue': 'number'},
                  {'action':'<action_name>', 'act_row_idx':'X',
                    'otherWS':Bool, 'analyst': '<analyst_id>'},
            ]
    }
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
    range0 = dic.get('range0', None)
    range1 = dic.get('range1', None)
    discreteresult = dic.get('discreteresult', None)
    trigger = dic.get('trigger', 'submit')
    analysisservice = dic.get('analysisservice', None)
    fromlevel = dic.get('fromlevel', '0')
    otherresultcondition = dic.get('otherresultcondition', False)
    resultcondition = dic.get('resultcondition', '')
    actions = dic.get('actions', [])
    rep_max = dic.get('repetition_max', '0')
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
    if trigger not in ['submit', 'verify']:
        logger.warn('Only available triggers are "verify" or "submit". '
                    '%s has been introduced.' % (trigger))
        return False
    uc = getToolByName(instance, 'uid_catalog')
    as_brain = uc(UID=analysisservice)
    if not as_brain:
        logger.warn('Not correct analysis service UID.')
        return False
    if type(actions) not in (list,):
        logger.warn('actions must be a list.')
        return False
    if type(rep_max) not in (str, int):
        logger.warn(
            'repetition_max must be an integer or a string '
            'representing an integer.')
        return False
    if type(fromlevel) not in (str, int):
        logger.warn(
            'fromlevel must be an integer or a string '
            'representing an integer.')
        return False
    if type(otherresultcondition) not in (bool,):
        logger.warn(
            'otherresultcondition must be a boolean.')
        return False
    try:
        int(rep_max)
    except ValueError:
        logger.warn(
            'repetition_max must be an integer or a string '
            'representing an integer.')
        return False
    try:
        if fromlevel != '':
            int(fromlevel)
    except ValueError:
        logger.warn(
            'repetition_max must be an integer or a string '
            'representing an integer.')
        return False
    return True
