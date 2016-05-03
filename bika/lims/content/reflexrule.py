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

    def getExpectedValuesAndRules(self, as_uid):
        """
        This function returns the expected values (even if they are discrete or
        not) and the rules defined for the analysis service.
        :as_uid: is the analysis service uid to obtain the rules and expected
            values from.
        :return: a list of dictionaries:
            [{
            'expected_values':(X,Y),
            'actions': [{'action': 'duplicate', },
                        {,},
                        ...]
            }, ...]
        """
        action_sets = self.getReflexRules()
        l = []
        for action_set in action_sets:
            if action_set.get('analysisservice', '') == as_uid and\
                    action_set.get('range0', ''):
                l.append({
                    'expected_values': (
                        action_set.get('range0', ''),
                        action_set.get('range1', '')
                        ),
                    'actions': action_set.get('actions', [])
                    })
            elif action_set.get('analysisservice', '') == as_uid and\
                    not(action_set.get('range0', '')):
                l.append({
                    'expected_values': action_set.get('resultoption', ''),
                    'actions': action_set.get('actions', [])
                    })
            else:
                pass
        return l

    def getRules(self, as_uid, result):
        """
        This function returns a list of dictionaries with the rules to be done
        for the analysis service.
        :as_uid: is the analysis service uid for the query.
        :result: the value of the result as string.
        :return: [{'action': 'duplicate', ...}, {,}, ...]
        """
        # Getting a list with the rules and expected values related to the
        # analysis service
        action_sets = self.getExpectedValuesAndRules(as_uid)
        r = []
        # Checking if the there are rules for this result
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


def doReflexRuleAction(base, action_row):
    """
    This function executes all the reflex rule actions inside action_row using
    the object in the variable 'base' as the starting point
    :base: a full analysis object
    :action_row: a list of dictionaries containing the actions to do
        [{'action': 'duplicate', ...}, {,}, ...]
    """
    for action in action_row:
        # If the analysis has been retracted yet, just duplicate it
        workflow = getToolByName(base, "portal_workflow")
        state = workflow.getInfoFor(base, 'review_state')
        if action.get('action', '') == 'repeat' and state != 'retracted':
            # Repeat an analysis consist on cancel it and then create a new
            # analysis with the same analysis service used for the canceled
            # one (always working with the same sample). It'll do a retract
            # action
            doActionFor(base, 'retract')
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
            logger.warn("Not known Reflex Rule action %s." %
                        (action.get('action', '')))
    return True
