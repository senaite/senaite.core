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
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReflexRule
from bika.lims.browser.fields import ReflexRuleField
from bika.lims.utils import isnumber
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import getUsers
from bika.lims.utils import tmpID
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

    def getExpectedValuesAndRules(self, as_uid, reflexed_times, wf_action):
        """
        This function returns the expected values (even if they are discrete or
        not) and the rules defined for the analysis service.
        :as_uid: is the analysis service uid to obtain the rules and expected
            values from.
        :reflexed_times: The number of times the base analysis
            has been reflexed
        :wf_action: it is the workflow action that the analysis is doing, we
            have to act in consideration of the action_set 'trigger' variable
        :return: a list of dictionaries:
            [{
            'expected_values':(X,Y),
            'repetition_max': '2',
            'wf_action': 'submit',
            'actions': [{'action': 'duplicate', },
                        {,},
                        ...]
            }, ...]
        """
        action_sets = self.getReflexRules()
        l = []
        for action_set in action_sets:
            rep_max = 0
            try:
                rep_max = int(action_set.get('repetition_max', 0))
            except:
                pass
            if action_set.get('analysisservice', '') == as_uid and\
                    action_set.get('range0', '') and\
                    action_set.get('trigger', '') == wf_action and\
                    rep_max > reflexed_times:
                l.append({
                    'expected_values': (
                        action_set.get('range0', ''),
                        action_set.get('range1', '')
                        ),
                    'actions': action_set.get('actions', [])
                    })
            elif action_set.get('analysisservice', '') == as_uid and\
                    action_set.get('trigger', '') == wf_action and\
                    not(action_set.get('range0', '')) and\
                    rep_max > reflexed_times:
                l.append({
                    'expected_values': action_set.get('resultoption', ''),
                    'actions': action_set.get('actions', [])
                    })
            else:
                pass
        return l

    def getRules(self, as_uid, result, reflexed_times, wf_action):
        """
        This function returns a list of dictionaries with the rules to be done
        for the analysis service.
        :as_uid: is the analysis service uid for the query.
        :result: the value of the result as string.
        :reflexed_times: The number of times the base analysis
            has been reflexed
        :wf_action: it is the workflow action that the analysis is doing, we
            have to act in consideration of the action_set 'trigger' variable
        :return: [{'action': 'duplicate', ...}, {,}, ...]
        """
        # Getting a list with the rules and expected values related to the
        # analysis service
        action_sets = self.getExpectedValuesAndRules(
            as_uid, reflexed_times, wf_action)
        r = []
        # Checking if the there are rules for this result and analysis
        # state change
        for action_set in action_sets:
            # It is a discrete value in string shape
            exp_val = action_set.get('expected_values', '')
            if isnumber(result) and isinstance(exp_val, str) and \
                    exp_val == result:
                r += action_set.get('actions', {})
            # It is a range of values
            elif isnumber(result) and len(exp_val) == 2 and \
                    float(exp_val[0]) <= float(result) and \
                    float(result) <= float(exp_val[1]):
                r += action_set.get('actions', {})
            else:
                pass
        return r

atapi.registerType(ReflexRule, PROJECTNAME)


def doActionToAnalysis(base, action):
    """
    This functions executes the action against the analysis.
    :base: a full analysis object. The new analyses will be cloned from it.
    :action: a dictionary representing an action row.
    :returns: the new analysis
    """
    # If the analysis has been retracted yet, just duplicate it
    workflow = getToolByName(base, "portal_workflow")
    state = workflow.getInfoFor(base, 'review_state')
    if action.get('action', '') == 'repeat' and state != 'retracted':
        # Repeat an analysis consist on cancel it and then create a new
        # analysis with the same analysis service used for the canceled
        # one (always working with the same sample). It'll do a retract
        # action
        doActionFor(base, 'retract')
        analysis = base.aq_parent.getAnalyses(
            sort_on='created')[-1].getObject()
    elif action.get('action', '') == 'duplicate' or state == 'retracted':
        # Duplicate an analysis consist on creating a new analysis with
        # the same analysis service for the same sample. It is used in
        # order to reduce the error procedure probability because both
        # results must be similar.
        ar = base.aq_parent
        kw = base.getKeyword()
        # Rename the analysis to make way for it's successor.
        # Support multiple duplicates by renaming to *-0, *-1, etc
        # Getting the analysis service
        analyses = [x for x in ar.objectValues("Analysis")
                    if x.getId().startswith(kw)]
        a_id = "{0}-{1}".format(kw, len(analyses))
        # Create new analysis and copy values from current analysis
        _id = ar.invokeFactory('Analysis', id=a_id)
        analysis = ar[_id]
        analysis.edit(
            Service=base.getService(),
            Calculation=base.getCalculation(),
            InterimFields=base.getInterimFields(),
            ResultDM=base.getResultDM(),
            Retested=True,  # True
            MaxTimeAllowed=base.getMaxTimeAllowed(),
            DueDate=base.getDueDate(),
            Duration=base.getDuration(),
            ReportDryMatter=base.getReportDryMatter(),
            Analyst=base.getAnalyst(),
            Instrument=base.getInstrument(),
            SamplePartition=base.getSamplePartition())
        analysis.setDetectionLimitOperand(base.getDetectionLimitOperand())
        analysis.setResult(base.getResult())
        analysis.unmarkCreationFlag()
        # zope.event.notify(ObjectInitializedEvent(analysis))
        changeWorkflowState(analysis,
                            "bika_analysis_workflow", "sample_received")
    else:
        logger.error(
            "Not known Reflex Rule action %s." % (action.get('action', '')))
        return 0
    # Get the recreated time number
    created_number = base.getReflexRuleActionLevel()
    # Incrementing the creation time number
    analysis.setReflexRuleActionLevel(created_number + 1)
    analysis.setReflexRuleAction(action.get('action', ''))
    analysis.setReflexAnalysisOf(base)
    analysis.setResult('')
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
