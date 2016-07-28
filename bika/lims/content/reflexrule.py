from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseContent
from Products.Archetypes import atapi
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import ReferenceField
from zope.interface import implements
from datetime import datetime
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReflexRule
from bika.lims.browser.fields import ReflexRuleField
from bika.lims.utils import isnumber
from bika.lims.utils import getUsers
from bika.lims.utils import tmpID
from bika.lims.utils.analysis import duplicateAnalysis
from bika.lims.utils import changeWorkflowState
from bika.lims.idserver import renameAfterCreation
from bika.lims import logger
from bika.lims.workflow import doActionFor
import sys

schema = BikaSchema.copy() + Schema((
    # Methods associated to the Reflex rule
    # In the first place the user has to choose from a drop-down list the
    # method which the rules for the analysis service will be bind to. After
    # selecting the method, the system will display another list in order to
    # choose the analysis service to add the rules when using the selected
    # method.
    ReferenceField(
        'Method',
        required=1,
        multiValued=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary='_getAvailableMethodsDisplayList',
        allowed_types=('Method',),
        relationship='ReflexRuleMethod',
        referenceClass=HoldingReference,
        widget=SelectionWidget(
            label=_("Methods"),
            format='select',
            description=_(
                "Select the method which the rules for the analysis "
                "service will be bound to."),
        )
    ),
    ReflexRuleField('ReflexRules',),
))
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")
schema['description'].widget.description = _("")


class ReflexRule(BaseContent):
    """
    When results become available, some samples may have to be added to the
    next available worksheet for reflex testing. These situations are caused by
    the indetermination of the result or by a failed test.
    """
    implements(IReflexRule)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getAvailableMethodsDisplayList(self):
        """ Returns a DisplayList with the available Methods
            registered in Bika-Setup. Only active Methods are fetched.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method', inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getExpectedValuesAndRules(self, analysis, wf_action):
        """
        This function returns the expected values (even if they are discrete or
        not) and the rules defined for the analysis service, the number of
        reflections and the 'other conditions' section.
        :analysis: the analysis full object which we want to obtain the
            rules for.
        :wf_action: it is the workflow action that the analysis is doing, we
            have to act in consideration of the action_set 'trigger' variable
        :return: a list of dictionaries:
            [{
            'expected_values':(X,Y),
            'repetition_max': '2',
            'wf_action': 'submit',
            'rulenumber': 'number',
            'actions': [{'action': 'duplicate', },
                        {,},
                        ...]
            }, ...]
        """
        # getting the analysis service uid for the query
        as_uid = analysis.getServiceUID()
        # The number of times the base analysis has been reflexed
        reflexed_times = analysis.getReflexRuleActionLevel()
        # Getting the action sets, those that contain action rows
        action_sets = self.getReflexRules()
        l = []
        for action_set in action_sets:
            try:
                rep_max = int(action_set.get('repetition_max', 0))
            except ValueError:
                logger.warn(
                    'repetition_max in %s should be an integer or a'
                    ' string representing an integer.' % (self.Title))
                rep_max = 0
            # Getting the 'other conditions' stuff from the rule
            otherresultcondition = action_set.get(
                'otherresultcondition', False)
            resultcondition = action_set.get('resultcondition', '')
            fromlevel = action_set.get('fromlevel', None)
            # Validate the analysis service
            if action_set.get('analysisservice', '') == as_uid and\
                    action_set.get('trigger', '') == wf_action:
                # Getting the 'other conditions' validity
                if (otherresultcondition and
                    resultcondition != analysis.getReflexRuleAction()) \
                    or \
                    (otherresultcondition and fromlevel and
                        int(fromlevel) != analysis.getReflexRuleActionLevel()):
                    continue
                # From level and reflected time conditions
                cond = int(fromlevel) == analysis.getReflexRuleActionLevel() \
                    if otherresultcondition else rep_max > reflexed_times
                # Defining the result deppending on the analysis' result type
                import pdb; pdb.set_trace()
                if action_set.get('range0', '') and cond:
                    l.append({
                        'expected_values': (
                            action_set.get('range0', ''),
                            action_set.get('range1', '')
                            ),
                        'actions': action_set.get('actions', []),
                        'rulenumber': action_set.get('rulenumber', 0)
                        })
                elif not(action_set.get('range0', '')) and cond:
                    l.append({
                        'expected_values': action_set.get(
                            'discreteresult', ''),
                        'actions': action_set.get('actions', []),
                        'rulenumber': action_set.get('rulenumber', 0)
                        })
                else:
                    pass
        return l

    def getActionReflexRules(self, analysis, wf_action):
        """
        This function returns a list of dictionaries with the rules to be done
        for the analysis service.
        :analysis: the analysis full object which we want to obtain the
            rules for.
        :wf_action: it is the workflow action that the analysis is doing, we
            have to act in consideration of the action_set 'trigger' variable
        :return: [{'action': 'duplicate', ...}, {,}, ...]
        """
        # the value of the analysis' result as string
        result = analysis.getResult()
        # Getting a list with the rules and expected values related to the
        # analysis service
        action_sets = self.getExpectedValuesAndRules(analysis, wf_action)
        r = []
        # Checking if the there are rules for this result and analysis
        # state change
        for action_set in action_sets:
            # It is a discrete value in string shape or
            # it is a range of values
            exp_val = action_set.get('expected_values', '')
            if (isnumber(result) and isinstance(exp_val, str) and
                exp_val == result)\
                or\
                (isnumber(result) and len(exp_val) == 2 and
                    float(exp_val[0]) <= float(result) and
                    float(result) <= float(exp_val[1])):
                acts = action_set.get('actions', {})
                # Adding the rule number inside each action row because we will
                # need to get the rule number from a row action later.
                for act in acts:
                    act['rulenumber'] = action_set.get('rulenumber', '0')
                    act['rulename'] = self.Title()
                r += acts
        return r

atapi.registerType(ReflexRule, PROJECTNAME)


def doActionToAnalysis(base, action):
    """
    This functions executes the action against the analysis.
    :base: a full analysis object. The new analyses will be cloned from it.
    :action: a dictionary representing an action row.
        [{'action': 'duplicate', ...}, {,}, ...]
    :returns: the new analysis
    """
    # If the analysis has been retracted yet, just duplicate it
    workflow = getToolByName(base, "portal_workflow")
    state = workflow.getInfoFor(base, 'review_state')
    action_rule_name = ''
    if action.get('action', '') == 'repeat' and state != 'retracted':
        # Repeat an analysis consist on cancel it and then create a new
        # analysis with the same analysis service used for the canceled
        # one (always working with the same sample). It'll do a retract
        # action
        doActionFor(base, 'retract')
        analysis = base.aq_parent.getAnalyses(
            sort_on='created')[-1].getObject()
        action_rule_name = 'Repited'
        analysis.setResult('')
    elif action.get('action', '') == 'duplicate' or state == 'retracted':
        analysis = duplicateAnalysis(base)
        action_rule_name = 'Duplicated'
        analysis.setResult('')
    elif action.get('action', '') == 'setresult':
        target_analysis = action.get('setresulton', '')
        result_value = action['setresultdiscrete'] if \
            action.get('setresultdiscrete', '') else action['setresultvalue']
        if target_analysis == 'original':
            original = base.getOriginalReflexedAnalysis()
            analysis = original
            original.setResult(result_value)
        else:
            # target_analysis == 'next'
            # Create a new analysis
            analysis = duplicateAnalysis(base)
            analysis.setResult(result_value)
            changeWorkflowState(analysis,
                                "bika_analysis_workflow", "to_be_verified")
        action_rule_name = 'Result set'
    else:
        logger.error(
            "Not known Reflex Rule action %s." % (action.get('action', '')))
        return 0
    # Get the recreated time number
    created_number = base.getReflexRuleActionLevel()
    # Incrementing the creation time number
    analysis.setReflexRuleActionLevel(created_number + 1)
    analysis.setReflexRuleAction(action.get('action', ''))
    analysis.setIsReflexAnalysis(True)
    analysis.setReflexAnalysisOf(base)
    # Setting the original reflected analysis
    if base.getOriginalReflexedAnalysis():
        analysis.setOriginalReflexedAnalysis(
            base.getOriginalReflexedAnalysis())
    else:
        analysis.setOriginalReflexedAnalysis(base)
    # Setting the remarks to base analysis
    time = datetime.now().strftime('%Y-%m-%d %H:%M')
    rule_num = action.get('rulenumber', 0)
    rule_name = action.get('rulename', '')
    base_remark = "Reflex rule number %s of '%s' applied at %s." % \
        (rule_num, rule_name, time)
    base_remark = base.getRemarks() + base_remark + '\n '
    base.setRemarks(base_remark)
    # Setting the remarks to base analysis
    analysis_remark = "%s due to reflex rule number %s of '%s' at %s" % \
        (action_rule_name, rule_num, rule_name, time)
    analysis_remark = analysis.getRemarks() + analysis_remark + '\n '
    analysis.setRemarks(analysis_remark)
    return analysis


def createWorksheet(base, analyst):
    """
    This function creates a new worksheet takeing advantatge of the analyst
    variable. If there isn't an analyst definet, the system will puck up the
    the first one obtained in a query.
    """
    if not(analyst):
        # Get any analyst
        analyst = getUsers(base, ['Manager', 'LabManager', 'Analyst'])[1]
    folder = base.bika_setup.worksheets
    _id = folder.invokeFactory('Worksheet', id=tmpID())
    ws = folder[_id]
    ws.unmarkCreationFlag()
    new_ws_id = renameAfterCreation(ws)
    ws.edit(
        Number=new_ws_id,
        Analyst=analyst,
        )
    return ws


def doWorksheetLogic(base, action, analysis):
    """
    This function checks if the actions contains worksheet actions.
    If the action demands to add the new analysis to another worksheet, this
    function will do it following the next rules:
    - If an analyst is defined in the action, the system will try to add the
    new analysis to the first worksheet of this analyst.
    If no active worksheet is found for this analyst, the system will create a
    new worksheet assigned to the defined analyst.
    - If no analyst is defined the system will try to add the new analysis to
    the last worksheet created, but if there are no active worksheets, a new
    worksheet with any analyst will be created.

    If the actions doesn't requires to add the new analysis to another
    worksheet, the function will try to add the analysis to the same worksheet
    as the base analysis.
    """
    if action.get('otherWS', False):
        # Adds the new analysis inside another worksheet.
        # Checking if the actions defines an analyst
        new_analyst = action.get('analyst', '')
        pc = getToolByName(base, 'portal_catalog')
        # If a new analyst is defined, add the analysis to the first
        # analyst's worksheet
        if new_analyst:
            # Getting the last worksheet created for the analyst
            wss = pc(
                portal_type='Worksheet',
                inactive_state='active',
                sort_on='created',
                sort_order='reverse',
                Analyst=new_analyst)
        else:
            # Getting the last worksheet created
            wss = pc(portal_type='Worksheet', inactive_state='active')
        if len(wss) > 0:
            # Add the new analysis to the worksheet
            wss[0].getObject().addAnalysis(analysis)
        else:
            # Create a new worksheet and add the analysis to it
            ws = createWorksheet(base, new_analyst)
            ws.addAnalysis(analysis)
    else:
        # Getting the base's worksheet
        wss = base.getBackReferences('WorksheetAnalysis')
        if len(wss) > 0:
            # If the old analysis belongs to a worksheet, add the new
            # one to it
            wss[0].addAnalysis(analysis)


def doReflexRuleAction(base, action_row):
    """
    This function executes all the reflex rule actions inside action_row using
    the object in the variable 'base' as the starting point
    :base: a full analysis object
    :action_row: a list of dictionaries containing the actions to do
        [{'action': 'duplicate', ...}, {,}, ...]
    """
    for action in action_row:
        # Do the action
        analysis = doActionToAnalysis(base, action)
        # Working with the worksheetlogic
        doWorksheetLogic(base, action, analysis)
    return True
