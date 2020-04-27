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
from bika.lims.interfaces import IReflexRule, IDeactivable
from bika.lims.browser.fields import ReflexRuleField
from bika.lims.utils import isnumber
from bika.lims.utils import getUsers
from bika.lims.utils import tmpID
from bika.lims.utils.analysis import duplicateAnalysis
from bika.lims.idserver import renameAfterCreation
from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
import sys
from Products.CMFCore.interfaces import ISiteRoot

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
    implements(IReflexRule, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    @security.private
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.private
    def _getAvailableMethodsDisplayList(self):
        """ Returns a DisplayList with the available Methods
            registered in Bika-Setup. Only active Methods are fetched.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method', is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    @security.private
    def _areConditionsMet(self, action_set, analysis, forceuid=False):
        """
        This function returns a boolean as True if the conditions in the
        action_set are met, and returns False otherwise.
        :analysis: the analysis full object which we want to obtain the
            rules for.
        :action_set: a set of rules and actions as a dictionary.
            {'actions': [{'act_row_idx': 0,
                'action': 'setresult',
                'an_result_id': 'set-4',
                'analyst': 'analyst1',
                'otherWS': 'current',
                'setresultdiscrete': '3',
                'setresulton': 'new',
                'setresultvalue': '',
                'worksheettemplate': ''}],
            'conditions': [{'analysisservice': 'dup-2',
                'and_or': 'and',
                'cond_row_idx': 0,
                'discreteresult': '2',
                'range0': '',
                'range1': ''},
                {'analysisservice': 'dup-7',
                'and_or': 'no',
                'cond_row_idx': 1,
                'discreteresult': '2',
                'range0': '',
                'range1': ''}],
            'mother_service_uid': 'ddaa2a7538bb4d188798498d6e675abd',
            'rulenumber': '1',
            'trigger': 'submit'}
        :forceuid: a boolean used to get the analysis service's UID from the
        analysis even if the analysis has been reflected and has a local_id.
        :returns: a Boolean.
        """
        conditions = action_set.get('conditions', [])
        eval_str = ''
        # Getting the analysis local id or its uid instead
        alocalid = analysis.getReflexRuleLocalID() if \
            analysis.getIsReflexAnalysis() and not forceuid else analysis.getServiceUID()
        # Getting the local ids (or analysis service uid) from the condition
        # with the same local id (or analysis service uid) as the analysis
        # attribute
        localids = [cond.get('analysisservice') for cond in conditions
                    if cond.get('analysisservice', '') == alocalid]
        # Now the alocalid could be the UID of the analysis service (if
        # this analysis has not been crated by a previous reflex rule) or it
        # could be a local_id if the analysis has been created by a reflex
        # rule.
        # So, if the analysis was reflexed, and no localid has been found
        # inside the action_set matching the analysis localid, lets look for
        # the analysis service UID.
        # forceuid is True when this second query has been done.
        if not localids and not forceuid and analysis.getIsReflexAnalysis():
            return self._areConditionsMet(action_set, analysis, forceuid=True)
        # action_set will not have any action for this analysis
        elif not localids:
            return False
        # Getting the action_set.rulenumber in order to check the
        # analysis.ReflexRuleActionsTriggered
        rulenumber = action_set.get('rulenumber', '')
        # Getting the reflex rules uid in order to fill the
        # analysis.ReflexRuleActionsTriggered attribute later
        rr_uid = self.UID()
        # Building the possible analysis.ReflexRuleActionsTriggered
        rr_actions_triggered = '.'.join([rr_uid, rulenumber])
        # If the follow condition is met, it means that the action_set for this
        # analysis has already been done by any other analysis from the
        # action_set. (e.g analsys.local_id =='dup-2', but this action has been
        # ran by the analysis with local_id=='dup-1', so we do not have to
        # run it again)
        if rr_actions_triggered in\
                analysis.getReflexRuleActionsTriggered().split('|'):
            return False
        # Check that rules are not repited: lets supose that some conditions
        # are met and an analysis with id analysis-1 is reflexed using a
        # duplicate action. Now we have analysis-1 and analysis1-dup. If the
        # same conditions are met while submitting/verifying analysis1-dup, the
        # duplicated shouldn't trigger the reflex action again.
        if forceuid and analysis.IsReflexAnalysis and rr_actions_triggered in\
                analysis.getReflexRuleActionsTriggered().split('|'):
            return False
        # To save the analysis related in the same action_set
        ans_related_to_set = []
        for condition in conditions:
            # analysisservice can be either a service uid (if it is the first
            # condition in the reflex rule) or it could be a local id such
            # as 'dup-2' if the analysis_set belongs to a derivate rule.
            ans_cond = condition.get('analysisservice', '')
            ans_uid_cond = action_set.get('mother_service_uid', '')
            # Be aware that we already know that the local_id for 'analysis'
            # has been found inside the conditions for this action_set
            if ans_cond != alocalid:
                # If the 'analysisservice' item from the condition is not the
                # same as the local_id from the analysis, the system
                # should look for the possible analysis with this localid
                # (e.g dup-2) and get its analysis object in order to compare
                # the results of the 'analysis variable' with the analysis
                # object obtained here
                curranalysis = _fetch_analysis_for_local_id(
                    analysis, ans_cond)
            else:
                # if the local_id of the 'analysis' is the same as the
                # local_id in the condition, we will use it as the current
                # analysis
                curranalysis = analysis
            if not curranalysis:
                continue
            ans_related_to_set.append(curranalysis)
            # the value of the analysis' result as string
            result = curranalysis.getResult()
            if len(analysis.getResultOptions()) > 0:
                # Discrete result as expacted value
                exp_val = condition.get('discreteresult', '')
            else:
                exp_val = (
                    condition.get('range0', ''),
                    condition.get('range1', '')
                    )
            and_or = condition.get('and_or', '')
            service_uid = curranalysis.getServiceUID()

            # Resolve the conditions
            resolution = \
                ans_uid_cond == service_uid and\
                ((isnumber(result) and isinstance(exp_val, str) and
                    exp_val == result) or
                    (isnumber(result) and len(exp_val) == 2 and
                        isnumber(exp_val[0]) and isnumber(exp_val[1]) and
                        float(exp_val[0]) <= float(result) and
                        float(result) <= float(exp_val[1])))
            # Build a string and then use eval()
            if and_or == 'no':
                eval_str += str(resolution)
            else:
                eval_str += str(resolution) + ' ' + and_or + ' '
        if eval_str and eval(eval_str):
            for an in ans_related_to_set:
                an.addReflexRuleActionsTriggered(rr_actions_triggered)
            return True
        else:
            return False

    @security.public
    def getActionReflexRules(self, analysis, wf_action):
        """
        This function returns a list of dictionaries with the rules to be done
        for the analysis service.
        :analysis: the analysis full object which we want to obtain the
            rules for.
        :wf_action: it is the workflow action that the analysis is doing, we
            have to act in consideration of the action_set 'trigger' variable
        :returns: [{'action': 'duplicate', ...}, {,}, ...]
        """
        # Setting up the analyses catalog
        self.analyses_catalog = getToolByName(self, CATALOG_ANALYSIS_LISTING)
        # Getting the action sets, those that contain action rows
        action_sets = self.getReflexRules()
        rules_list = []
        condition = False
        for action_set in action_sets:
            # Validate the trigger
            if action_set.get('trigger', '') == wf_action:
                # Getting the conditions resolution
                condition = self._areConditionsMet(action_set, analysis)
                if condition:
                    actions = action_set.get('actions', [])
                    for act in actions:
                        # Adding the rule number inside each action row because
                        # need to get the rule number from a row action later.
                        # we will need to get the rule number from a row
                        # action later.
                        act['rulenumber'] = action_set.get('rulenumber', '0')
                        act['rulename'] = self.Title()
                        rules_list.append(act)
        return rules_list

atapi.registerType(ReflexRule, PROJECTNAME)


def _fetch_analysis_for_local_id(analysis, ans_cond):
    """
    This function returns an analysis when the derivative IDs conditions
    are met.
    :analysis: the analysis full object which we want to obtain the
        rules for.
    :ans_cond: the local id with the target derivative reflex rule id.
    """
    # Getting the first reflexed analysis from the chain
    first_reflexed = analysis.getOriginalReflexedAnalysis()
    # Getting all reflexed analysis created due to this first analysis
    analyses_catalog = getToolByName(analysis, CATALOG_ANALYSIS_LISTING)
    derivatives_brains = analyses_catalog(
        getOriginalReflexedAnalysisUID=first_reflexed.UID()
    )
    # From all the related reflexed analysis, return the one that matches
    # with the local id 'ans_cond'
    for derivative in derivatives_brains:
        derivative = derivative.getObject()
        if derivative.getReflexRuleLocalID() == ans_cond:
            return derivative
    return None

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
    if action.get('action', '') == 'setvisibility':
        action_rule_name = 'Visibility set'
        target_analysis = action.get('setvisibilityof', '')
        if target_analysis == "original":
            analysis = base
        else:
            analysis = _fetch_analysis_for_local_id(base, target_analysis)
    elif action.get('action', '') == 'repeat' and state != 'retracted':
        # Repeat an analysis consist on cancel it and then create a new
        # analysis with the same analysis service used for the canceled
        # one (always working with the same sample). It'll do a retract
        # action
        doActionFor(base, 'retract')
        analysis = base.aq_parent.getAnalyses(
            sort_on='created')[-1].getObject()
        action_rule_name = 'Repeated'
        analysis.setResult('')
    elif action.get('action', '') == 'duplicate' or state == 'retracted':
        analysis = duplicateAnalysis(base)
        action_rule_name = 'Duplicated'
        analysis.setResult('')
    elif action.get('action', '') == 'setresult':
        target_analysis = action.get('setresulton', '')
        action_rule_name = 'Result set'
        result_value = action['setresultdiscrete'] if \
            action.get('setresultdiscrete', '') else action['setresultvalue']
        if target_analysis == 'original':
            original = base.getOriginalReflexedAnalysis()
            analysis = original
            original.setResult(result_value)
        elif target_analysis == 'new':
            # Create a new analysis
            analysis = duplicateAnalysis(base)
            analysis.setResult(result_value)
            doActionFor(analysis, 'submit')
    else:
        logger.error(
            "Not known Reflex Rule action %s." % (action.get('action', '')))
        return 0
    analysis.setReflexRuleAction(action.get('action', ''))
    analysis.setIsReflexAnalysis(True)
    analysis.setReflexAnalysisOf(base)
    analysis.setReflexRuleActionsTriggered(
        base.getReflexRuleActionsTriggered()
    )
    if action.get('showinreport', '') == "invisible":
        analysis.setHidden(True)
    elif action.get('showinreport', '') == "visible":
        analysis.setHidden(False)
    # Setting the original reflected analysis
    if base.getOriginalReflexedAnalysis():
        analysis.setOriginalReflexedAnalysis(
            base.getOriginalReflexedAnalysis())
    else:
        analysis.setOriginalReflexedAnalysis(base)
    analysis.setReflexRuleLocalID(action.get('an_result_id', ''))
    # Setting the remarks to base analysis
    time = datetime.now().strftime('%Y-%m-%d %H:%M')
    rule_num = action.get('rulenumber', 0)
    rule_name = action.get('rulename', '')
    base_remark = "Reflex rule number %s of '%s' applied at %s." % \
        (rule_num, rule_name, time)
    base_remark = base.getRemarks() + base_remark + '||'
    base.setRemarks(base_remark)
    # Setting the remarks to new analysis
    analysis_remark = "%s due to reflex rule number %s of '%s' at %s" % \
        (action_rule_name, rule_num, rule_name, time)
    analysis_remark = analysis.getRemarks() + analysis_remark + '||'
    analysis.setRemarks(analysis_remark)
    return analysis


def _createWorksheet(base, worksheettemplate, analyst):
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
    if worksheettemplate:
        ws.applyWorksheetTemplate(worksheettemplate)
    return ws


def doWorksheetLogic(base, action, analysis):
    """
    This function checks if the actions contains worksheet actions.

    There is a selection list in each action section. This select has the
    following options and consequence.

    1) "To the current worksheet" (selected by default)
    2) "To another worksheet"
    3) "Create another worksheet"
    4) "No worksheet"

    - If option 1) is selected, the Analyst selection list will not be
    displayed. Since the action doesn't require to add the new analysis to
    another worksheet, the function will try to add the analysis to the same
    worksheet as the base analysis. If the base analysis is not assigned in a
    worksheet, no worksheet will be assigned to the new analysis.

    - If option 2) is selected, the Analyst selection list will be displayed.

    - If option 2) is selected and an analyst has also been selected, then the
    system will search for the latest worksheet in status "open" for the
    selected analyst and will add the analysis in that worksheet (the system
    also searches for the worksheet template if defined).
    If the system doesn't find any match, another worksheet assigned to the
    selected analyst and with the analysis must be automatically created.

    - If option 2) is selected but no analyst selected, then the system will
    search for the latest worksheet in the status "open" regardless of the
    analyst assigned and will add the analysis in that worksheet. If there
    isn't any open worksheet available, then go to option 3)

    - If option 3) is selected, a new worksheet with the defined analyst will
    be created.
    If no analyst is defined for the original analysis, the system
    will create a new worksheet and assign the same analyst as the original
    analysis to which the rule applies.
    If the original analysis doesn't have assigned any analyst, the system will
    assign the same analyst that was assigned to the latest worksheet available
    in the system. If there isn't any worksheet created yet, use the first
    active user with role "analyst" available.

    - if option 4) the Analyst selection list will not be displayed. The
    analysis (duplicate, repeat, whatever) will be created, but not assigned
    to any worksheet, so it will stay "on queue", assigned to the same
    Analysis Request as the original analysis for which the rule has been
    triggered.
    """
    otherWS = action.get('otherWS', False)
    worksheet_catalog = getToolByName(base, CATALOG_WORKSHEET_LISTING)
    if otherWS in ['to_another', 'create_another']:
        # Adds the new analysis inside same worksheet as the previous analysis.
        # Checking if the actions defines an analyst
        new_analyst = action.get('analyst', '')
        # Checking if the action defines a worksheet template
        worksheettemplate = action.get('worksheettemplate', '')
        # Creating the query
        contentFilter = {
            'review_state': 'open',
            'sort_on': 'created',
            'sort_order': 'reverse'}
        # If a new analyst is defined, add the analysis to the first
        # analyst's worksheet
        if new_analyst:
            # Getting the last worksheet created for the analyst
            contentFilter['Analyst'] = new_analyst
        if worksheettemplate:
            # Adding the worksheettemplate filter
            contentFilter['getWorksheetTemplateUID'] = worksheettemplate
        # Run the filter
        wss = worksheet_catalog(contentFilter)
        # 'repeat' actions takes advantatge of the 'retract' workflow action.
        # the retract process assigns the new analysis to the same worksheet
        # as the base analysis, so we need to desassign it now.
        ws = analysis.getWorksheet()
        if ws:
            ws.removeAnalysis(analysis)
        # If worksheet found and option 2
        if len(wss) > 0 and otherWS == 'to_another':
            # Add the new analysis to the worksheet
            wss[0].getObject().addAnalysis(analysis)
        # No worksheet found, but option 2 or 3 selected:
        elif new_analyst:
            # Create a new worksheet and add the analysis to it
            ws = _createWorksheet(base, worksheettemplate, new_analyst)
            ws.addAnalysis(analysis)
        elif not new_analyst:
            # Getting the original analysis to which the rule applies
            previous_analysis = analysis.getReflexAnalysisOf()
            # Getting the worksheet of the analysis
            prev_ws = previous_analysis.getWorksheet()
            # Getting the analyst from the worksheet
            prev_analyst = prev_ws.getAnalyst() if prev_ws else ''
            # If the previous analysis belongs to a worksheet:
            if prev_analyst:
                ws = _createWorksheet(base, worksheettemplate, prev_analyst)
                ws.addAnalysis(analysis)
            # If the original analysis doesn't have assigned any analyst
            else:
                # assign the same analyst that was assigned to the latest
                # worksheet available
                prev_analyst = wss[0].getObject().getAnalyst() if wss else ''
                if prev_analyst:
                    ws = _createWorksheet(base, worksheettemplate, prev_analyst)
                    ws.addAnalysis(analysis)

    elif otherWS == 'current':
        # Getting the base's worksheet
        ws = base.getWorksheet()
        if ws:
            # If the old analysis belongs to a worksheet, add the new
            # one to it
            ws.addAnalysis(analysis)
    # If option 1 selected and no ws found, no worksheet will be assigned to
    # the analysis.
    # If option 4 selected, no worksheet will be assigned to the analysis
    elif otherWS == 'no_ws':
        ws = analysis.getWorksheet()
        if ws:
            ws.removeAnalysis(analysis)


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
        # Reindexing both objects in order to fill its metacolumns with
        # the changes.
        # TODO: Sometimes, objects are reindexed. Could it be that they
        # are reindexed in some workflow step that some of them don't do?
        base.reindexObject()
        analysis.reindexObject()
    return True
