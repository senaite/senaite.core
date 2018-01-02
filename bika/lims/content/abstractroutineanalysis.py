# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import BooleanField, FixedPointField, \
    StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import HistoryAwareReferenceField, \
    InterimFieldsField, UIDReferenceField
from bika.lims.browser.widgets import DecimalWidget, RecordsWidget
from bika.lims.catalog.indexers.baseanalysis import sortable_title
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.reflexrule import doReflexRuleAction
from bika.lims.interfaces import IAnalysis, IRoutineAnalysis, \
    ISamplePrepWorkflow
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.workflow import doActionFor, getCurrentState
from bika.lims.workflow import getTransitionDate
from bika.lims.workflow import skip
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow.analysis import STATE_RETRACTED, STATE_REJECTED
from zope.interface import implements

# The physical sample partition linked to the Analysis.
SamplePartition = UIDReferenceField(
    'SamplePartition',
    required=0,
    allowed_types=('SamplePartition',)
)

# True if the analysis is created by a reflex rule
IsReflexAnalysis = BooleanField(
    'IsReflexAnalysis',
    default=False,
    required=0
)

# This field contains the original analysis which was reflected
OriginalReflexedAnalysis = UIDReferenceField(
    'OriginalReflexedAnalysis',
    required=0,
    allowed_types=('Analysis',)
)

# This field contains the analysis which has been reflected following
# a reflex rule
ReflexAnalysisOf = UIDReferenceField(
    'ReflexAnalysisOf',
    required=0,
    allowed_types=('Analysis',)
)

# Which is the Reflex Rule action that has created this analysis
ReflexRuleAction = StringField(
    'ReflexRuleAction',
    required=0,
    default=0
)

# Which is the 'local_id' inside the reflex rule
ReflexRuleLocalID = StringField(
    'ReflexRuleLocalID',
    required=0,
    default=0
)

# Reflex rule triggered actions which the current analysis is responsible for.
# Separated by '|'
ReflexRuleActionsTriggered = StringField(
    'ReflexRuleActionsTriggered',
    required=0,
    default=''
)

# The actual uncertainty for this analysis' result, populated when the result
# is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    precision=10,
    widget=DecimalWidget(
        label=_("Uncertainty")
    )
)
# This field keep track if the field hidden has been set manually or not. If
# this value is false, the system will assume the visibility of this analysis
# in results report will depend on the value set at AR, Profile or Template
# levels (see AnalysisServiceSettings fields in AR). If the value for this
# field is set to true, the system will assume the visibility of the analysis
# will only depend on the value set for the field Hidden (bool).
HiddenManually = BooleanField(
    'HiddenManually',
    default=False,
)

# Routine Analyses have a versioned link to the calculation at creation time.
Calculation = HistoryAwareReferenceField(
    'Calculation',
    allowed_types=('Calculation',),
    relationship='AnalysisCalculation',
    referenceClass=HoldingReference
)

# InterimFields are defined in Calculations, Services, and Analyses.
# In Analysis Services, the default values are taken from Calculation.
# In Analyses, the default values are taken from the Analysis Service.
# When instrument results are imported, the values in analysis are overridden
# before the calculation is performed.
InterimFields = InterimFieldsField(
    'InterimFields',
    schemata='Method',
    widget=RecordsWidget(
        label=_("Calculation Interim Fields"),
        description=_(
            "Values can be entered here which will override the defaults "
            "specified in the Calculation Interim Fields."),
    )
)

schema = schema.copy() + Schema((
    IsReflexAnalysis,
    OriginalReflexedAnalysis,
    ReflexAnalysisOf,
    ReflexRuleAction,
    ReflexRuleActionsTriggered,
    ReflexRuleLocalID,
    SamplePartition,
    Uncertainty,
    HiddenManually,
    Calculation,
    InterimFields,
))


class AbstractRoutineAnalysis(AbstractAnalysis):
    implements(IAnalysis, IRequestAnalysis, IRoutineAnalysis, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getRequest(self):
        """Returns the Analysis Request this analysis belongs to.
        Delegates to self.aq_parent
        """
        ar = self.aq_parent
        return ar

    @security.public
    def getRequestID(self):
        """Used to populate catalog values.
        Returns the ID of the parent analysis request.
        """
        ar = self.getRequest()
        if ar:
            return ar.getId()

    @security.public
    def getRequestUID(self):
        """Returns the UID of the parent analysis request.
        """
        ar = self.getRequest()
        if ar:
            return ar.UID()

    @security.public
    def getRequestURL(self):
        """Returns the url path of the Analysis Request object this analysis
        belongs to. Returns None if there is no Request assigned.
        :return: the Analysis Request URL path this analysis belongs to
        :rtype: str
        """
        request = self.getRequest()
        if request:
            return request.absolute_url_path()

    @security.public
    def getClientTitle(self):
        """Used to populate catalog values.
        Returns the Title of the client for this analysis' AR.
        """
        request = self.getRequest()
        if request:
            client = request.getClient()
            if client:
                return client.Title()

    @security.public
    def getClientUID(self):
        """Used to populate catalog values.
        Returns the UID of the client for this analysis' AR.
        """
        request = self.getRequest()
        if request:
            client = request.getClient()
            if client:
                return client.UID()

    @security.public
    def getClientURL(self):
        """This method is used to populate catalog values
        Returns the URL of the client for this analysis' AR.
        """
        request = self.getRequest()
        if request:
            client = request.getClient()
            if client:
                return client.absolute_url_path()

    @security.public
    def getClientOrderNumber(self):
        """Used to populate catalog values.
        Returns the ClientOrderNumber of the associated AR
        """
        request = self.getRequest()
        if request:
            return request.getClientOrderNumber()

    @security.public
    def getDateReceived(self):
        """Used to populate catalog values.
        Returns the date on which the "receive" transition was invoked on this
        analysis' Sample.
        """
        return getTransitionDate(self, 'receive', return_as_datetime=True)

    @security.public
    def getDatePublished(self):
        """Used to populate catalog values.
        Returns the date on which the "publish" transition was invoked on this
        analysis.
        """
        return getTransitionDate(self, 'publish', return_as_datetime=True)

    @security.public
    def getDateSampled(self):
        """Used to populate catalog values.
        Only has value when sampling_workflow is active.
        """
        return getTransitionDate(self, 'sample', return_as_datetime=True)

    @security.public
    def getStartProcessDate(self):
        """Returns the date time when the analysis was received. If the
        analysis hasn't yet been received, returns None
        Overrides getStartProcessDateTime from the base class
        :return: Date time when the analysis is ready to be processed.
        :rtype: DateTime
        """
        return self.getDateReceived()

    @security.public
    def getSamplePartitionUID(self):
        part = self.getSamplePartition()
        if part:
            return part.UID()

    @security.public
    def getSamplePointUID(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            samplepoint = sample.getSamplePoint()
            if samplepoint:
                return samplepoint.UID()

    @security.public
    def getSamplePartitionID(self):
        """Used to populate catalog values.
        Returns the sample partition ID
        """
        partition = self.getSamplePartition()
        if partition:
            return partition.getId()
        return ''

    @security.public
    def getDueDate(self):
        """Used to populate getDueDate index and metadata.
        This calculates the difference between the time that the sample
        partition associated with this analysis was recieved, and the
        maximum turnaround time.
        """
        maxtime = self.getMaxTimeAllowed()
        if not maxtime:
            maxtime = getToolByName(self, 'bika_setup').getDefaultTurnaroundTime()
        max_days = float(maxtime.get('days', 0)) + (
            (float(maxtime.get('hours', 0)) * 3600 +
             float(maxtime.get('minutes', 0)) * 60)
            / 86400
        )
        part = self.getSamplePartition()
        if part:
            starttime = part.getDateReceived()
            duetime = starttime + max_days if starttime else ''
            return duetime

    @security.public
    def getCalculationTitle(self):
        """Used to populate catalog values
        """
        calculation = self.getCalculation()
        if calculation:
            return calculation.Title()

    @security.public
    def getCalculationUID(self):
        """Used to populate catalog values
        """
        calculation = self.getCalculation()
        if calculation:
            return calculation.UID()

    @security.public
    def getSampleTypeUID(self):
        """Used to populate catalog values.
        """
        sample = self.getSample()
        if sample:
            sampletype = sample.getSampleType()
            if sampletype:
                return sampletype.UID()

    @security.public
    def getBatchUID(self):
        """This method is used to populate catalog values
        """
        request = self.getRequest()
        if request:
            return request.getBatchUID()

    @security.public
    def getAnalysisRequestPrintStatus(self):
        """This method is used to populate catalog values
        """
        request = self.getRequest()
        if request:
            return request.getPrinted()

    @security.public
    def getAnalysisSpecs(self, specification=None):
        """Retrieves the analysis specs to be applied to this analysis.
        Allowed values for specification= 'client', 'lab', None If
        specification is None, client specification gets priority from lab
        specification. If no specification available for this analysis,
        returns None
        """
        sample = self.getSample()
        client_uid = self.getClientUID()
        if not sample or not client_uid:
            return None

        sampletype = sample.getSampleType()
        sampletype_uid = sampletype and sampletype.UID() or ''
        bsc = getToolByName(self, 'bika_setup_catalog')

        # retrieves the desired specs if None specs defined
        if not specification:
            proxies = bsc(portal_type='AnalysisSpec',
                          getClientUID=client_uid,
                          getSampleTypeUID=sampletype_uid)

            if len(proxies) == 0:
                # No client specs available, retrieve lab specs
                proxies = bsc(portal_type='AnalysisSpec',
                              getSampleTypeUID=sampletype_uid)
        else:
            specuid = self.bika_setup.bika_analysisspecs.UID()
            if specification == 'client':
                specuid = client_uid
            proxies = bsc(portal_type='AnalysisSpec',
                          getSampleTypeUID=sampletype_uid,
                          getClientUID=specuid)

        outspecs = None
        for spec in (p.getObject() for p in proxies):
            if self.getKeyword() in spec.getResultsRangeDict():
                outspecs = spec
                break

        return outspecs

    @security.public
    def getResultsRange(self, specification=None):
        """Returns the valid results range for this analysis, a dictionary
        with the following keys: 'keyword', 'uid', 'min', 'max ', 'error',
        'hidemin', 'hidemax', 'rangecomment' Allowed values for
        specification='ar', 'client', 'lab', None If specification is None,
        the following is the priority to get the results range: AR > Client >
        Lab If no specification available for this analysis, returns {}
        """
        rr = {}
        an = self

        if specification == 'ar' or specification is None:
            if an.aq_parent and an.aq_parent.portal_type == 'AnalysisRequest':
                rr = an.aq_parent.getResultsRange()
                rr = [r for r in rr if r.get('keyword', '') == an.getKeyword()]
                rr = rr[0] if rr and len(rr) > 0 else {}
                if rr:
                    rr['uid'] = self.UID()
        if not rr:
            # Let's try to retrieve the specs from client and/or lab
            specs = an.getAnalysisSpecs(specification)
            rr = specs.getResultsRangeDict() if specs else {}
            rr = rr.get(an.getKeyword(), {}) if rr else {}
            if rr:
                rr['uid'] = self.UID()
        return rr

    @security.public
    def getSiblings(self, retracted=False):
        """
        Return the siblings analyses, using the parent to which the current
        analysis belongs to as the source
        :param retracted: If false, retracted/rejected siblings are dismissed
        :type retracted: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        raise NotImplementedError("getSiblings is not implemented.")

    @security.public
    def getDependents(self, retracted=False):
        """
        Returns a list of siblings who depend on us to calculate their result.
        :param retracted: If false, retracted/rejected dependents are dismissed
        :type retracted: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        dependents = []
        for sibling in self.getSiblings(retracted=retracted):
            calculation = sibling.getCalculation()
            if not calculation:
                continue
            depservices = calculation.getDependentServices()
            dep_keywords = [dep.getKeyword() for dep in depservices]
            if self.getKeyword() in dep_keywords:
                dependents.append(sibling)
        return dependents

    @security.public
    def getDependencies(self, retracted=False):
        """
        Return a list of siblings who we depend on to calculate our result.
        :param retracted: If false retracted/rejected dependencies are dismissed
        :type retracted: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        calc = self.getCalculation()
        if not calc:
            return []

        dependencies = []
        for sibling in self.getSiblings(retracted=retracted):
            # We get all analyses that depend on me, also if retracted (maybe
            # I am one of those that are retracted!)
            deps = sibling.getDependents(retracted=True)
            deps = [dep.UID() for dep in deps]
            if self.UID() in deps:
                dependencies.append(sibling)
        return dependencies

    @security.public
    def getPrioritySortkey(self):
        """
        Returns the key that will be used to sort the current Analysis, from
        most prioritary to less prioritary.
        :return: string used for sorting
        """
        analysis_request = self.getRequest()
        if analysis_request is None:
            return None
        ar_sort_key = analysis_request.getPrioritySortkey()
        ar_id = analysis_request.getId().lower()
        title = sortable_title(self)
        if callable(title):
            title = title()
        return '{}.{}.{}'.format(ar_sort_key, ar_id, title)

    @security.public
    def getHidden(self):
        """ Returns whether if the analysis must be displayed in results
        reports or not, as well as in analyses view when the user logged in
        is a Client Contact.

        If the value for the field HiddenManually is set to False, this function
        will delegate the action to the method getAnalysisServiceSettings() from
        the Analysis Request.

        If the value for the field HiddenManually is set to True, this function
        will return the value of the field Hidden.
        :return: true or false
        :rtype: bool
        """
        if self.getHiddenManually():
            return self.getField('Hidden').get(self)
        request = self.getRequest()
        if request:
            service_uid = self.getServiceUID()
            ar_settings = request.getAnalysisServiceSettings(service_uid)
            return ar_settings.get('hidden', False)
        return False

    @security.public
    def setHidden(self, hidden):
        """ Sets if this analysis must be displayed or not in results report and
        in manage analyses view if the user is a lab contact as well.

        The value set by using this field will have priority over the visibility
        criteria set at Analysis Request, Template or Profile levels (see
        field AnalysisServiceSettings from Analysis Request. To achieve this
        behavior, this setter also sets the value to HiddenManually to true.
        :param hidden: true if the analysis must be hidden in report
        :type hidden: bool
        """
        self.setHiddenManually(True)
        self.getField('Hidden').set(self, hidden)

    @security.public
    def setReflexAnalysisOf(self, analysis):
        """Sets the analysis that has been reflexed in order to create this
        one, but if the analysis is the same as self, do nothing.
        :param analysis: an analysis object or UID
        """
        if not analysis or analysis.UID() == self.UID():
            pass
        else:
            self.getField('ReflexAnalysisOf').set(self, analysis)

    @security.public
    def addReflexRuleActionsTriggered(self, text):
        """This function adds a new item to the string field
        ReflexRuleActionsTriggered. From the field: Reflex rule triggered
        actions from which the current analysis is responsible of. Separated
        by '|'
        :param text: is a str object with the format '<UID>.<rulename>' ->
        '123354.1'
        """
        old = self.getReflexRuleActionsTriggered()
        self.setReflexRuleActionsTriggered(old + text + '|')

    @security.public
    def getOriginalReflexedAnalysisUID(self):
        """
        Returns the uid of the original reflexed analysis.
        """
        original = self.getOriginalReflexedAnalysis()
        if original:
            return original.UID()
        return ''

    @security.private
    def _reflex_rule_process(self, wf_action):
        """This function does all the reflex rule process.
        :param wf_action: is a string containing the workflow action triggered
        """
        workflow = getToolByName(self, 'portal_workflow')
        # Check out if the analysis has any reflex rule bound to it.
        # First we have get the analysis' method because the Reflex Rule
        # objects are related to a method.
        a_method = self.getMethod()
        # After getting the analysis' method we have to get all Reflex Rules
        # related to that method.
        if a_method:
            all_rrs = a_method.getBackReferences('ReflexRuleMethod')
            # Once we have all the Reflex Rules with the same method as the
            # analysis has, it is time to get the rules that are bound to the
            # same analysis service that is using the analysis.
            for rule in all_rrs:
                state = workflow.getInfoFor(rule, 'inactive_state')
                if state == 'inactive':
                    continue
                # Getting the rules to be done from the reflex rule taking
                # in consideration the analysis service, the result and
                # the state change
                action_row = rule.getActionReflexRules(self, wf_action)
                # Once we have the rules, the system has to execute its
                # instructions if the result has the expected result.
                doReflexRuleAction(self, action_row)

    @security.public
    def guard_to_be_preserved(self):
        """Returns if the Sample Partition to which this Analysis belongs needs
        to be prepreserved, so the Analysis. If the analysis has no Sample
        Partition assigned, returns False.
        Delegates to Sample Partitions's guard_to_be_preserved
        """
        part = self.getSamplePartition()
        return part and part.guard_to_be_preserved()

    @security.public
    def workflow_script_submit(self):
        """
        Method triggered after a 'submit' transition for the current analysis
        is performed. Responsible of triggering cascade actions such as
        transitioning dependent analyses, transitioning worksheets, etc
        depending on the current analysis and other analyses that belong to the
        same Analysis Request or Worksheet.
        This function is called automatically by
        bika.lims.workfow.AfterTransitionEventHandler
        """
        # The analyses that depends on this analysis to calculate their results
        # must be transitioned too, otherwise the user will be forced to submit
        # them individually. Note that the automatic transition of dependents
        # must only take place if all their dependencies have been submitted
        # already.
        for dependent in self.getDependents():
            # If this submit transition has already been done for this
            # dependent analysis within the current request, continue.
            if skip(dependent, 'submit', peek=True):
                continue

            # TODO Workflow. All below and inside this loop should be moved to
            # a guard_submit_transition inside analysis

            # If this dependent has already been submitted, omit
            if dependent.getSubmittedBy():
                continue

            # The dependent cannot be transitioned if doesn't have result
            if not dependent.getResult():
                continue

            # If the calculation associated to the dependent analysis requires
            # the manual introduction of interim fields, do not transition the
            # dependent automatically, force the user to do it manually.
            calculation = dependent.getCalculation()
            if calculation and calculation.getInterimFields():
                continue

            # All dependencies from this dependent analysis are ok?
            deps = dependent.getDependencies()
            dsub = [dep for dep in deps if wasTransitionPerformed(dep, 'submit')]
            if len(deps) == len(dsub):
                # The statuses of all dependencies of this dependent are ok
                # (at least, all of them have been submitted already)
                doActionFor(dependent, 'submit')

        # Do all the reflex rules process
        self._reflex_rule_process('submit')

        # If all analyses from the Analysis Request to which this Analysis
        # belongs have been submitted, then promote the action to the parent
        # Analysis Request
        ar = self.getRequest()
        ans = [an.getObject() for an in ar.getAnalyses()]
        anssub = [an for an in ans if wasTransitionPerformed(an, 'submit')]
        if len(ans) == len(anssub):
            doActionFor(ar, 'submit')

        # Delegate the transition of Worksheet to base class AbstractAnalysis
        super(AbstractRoutineAnalysis, self).workflow_script_submit()
