# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


"""ReferenceAnalysis
"""
from plone import api
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, formatDecimalMark
from bika.lims.utils.analysis import format_numeric_result
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import STD_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.subscribers import skip
from bika.lims.utils.analysis import get_significant_digits
from DateTime import DateTime
from plone.app.blob.field import BlobField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import DateTimeField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements


schema = BikaSchema.copy() + Schema((
    StringField('ReferenceType',
        vocabulary=STD_TYPES,
        widget=SelectionWidget(
            format='select',
            label=_("Reference Type"),
        ),
    ),
    HistoryAwareReferenceField('Service',
        required=1,
        allowed_types=('AnalysisService',),
        relationship='ReferenceAnalysisAnalysisService',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            label=_("Analysis Service"),
        )
    ),
    InterimFieldsField('InterimFields',
        widget=BikaRecordsWidget(
            label=_("Calculation Interim Fields"),
        )
    ),
    StringField('Result',
        widget=StringWidget(
            label=_("Result"),
        )
    ),
    DateTimeField('ResultCaptureDate',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    StringField('ResultDM',
    ),
    ReferenceField('Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='ReferenceAnalysisAttachment',
    ),
    StringField('Analyst',
    ),
    TextField('Remarks',
    ),
    ReferenceField(
        'Instrument',
        required=0,
        allowed_types=('Instrument',),
        relationship='AnalysisInstrument',
        referenceClass=HoldingReference,
    ),
    ReferenceField('Method',
        required = 0,
        allowed_types = ('Method',),
        relationship = 'AnalysisMethod',
        referenceClass = HoldingReference,
    ),
    BlobField('RetractedAnalysesPdfReport',
    ),
    BooleanField('Retested',
        default = False,
        widget = BooleanWidget(
            label=_("Retested"),
        ),
    ),
    ComputedField('ReferenceSampleUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField('SupplierUID',
        expression = 'context.aq_parent.aq_parent.UID()',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField('ServiceUID',
        expression = "context.getService() and context.getService().UID() or ''",
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    StringField('ReferenceAnalysesGroupID',
        widget = StringWidget(
            label=_("ReferenceAnalysesGroupID"),
            visible=False,
        ),
    ),
    ComputedField('Keyword',
        expression = "context.getService() and context.getService().getKeyword() or ''",
    ),
    FixedPointField('Uncertainty',
        widget=DecimalWidget(
            label = _("Uncertainty"),
        ),
    ),

    # Required number of required verifications before this analysis being
    # transitioned to a 'verified' state. This value is set automatically
    # when the analysis is created, based on the value set for the property
    # NumberOfRequiredVerifications from the Analysis Service
    IntegerField('NumberOfRequiredVerifications', default=1),

    # Number of verifications done for this analysis. Each time a 'verify'
    # transition takes place, this value is updated accordingly. The
    # transition will finally succeed when the NumberOfVerifications matches
    # with the NumberOfRequiredVerifications. Meanwhile, the state of the
    # object will remain in 'to_be_verified'
    IntegerField('NumberOfVerifications', default=0),
),
)


class ReferenceAnalysis(BaseContent):
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Service ID as title """
        s = self.getService()
        s = s and s.Title() or ''
        return safe_unicode(s).encode('utf-8')

    def getReviewState(self):
        """ Return the current referencenalysis' state"""
        workflow = getToolByName(self, "portal_workflow")
        return workflow.getInfoFor(self, "review_state")

    def getDefaultUncertainty(self, result=None):
        """ Calls self.Service.getUncertainty with either the provided
            result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def getUncertainty(self, result=None):
        """ Returns the uncertainty for this analysis and result.
            Returns the value from Schema's Uncertainty field if the
            Service has the option 'Allow manual uncertainty'. Otherwise,
            do a callback to getDefaultUncertainty()
        """
        serv = self.getService()
        schu = self.Schema().getField('Uncertainty').get(self)
        if schu and serv.getAllowManualUncertainty() == True:
            try:
                schu = float(schu)
                return schu
            except ValueError:
                # if uncertainty is not a number, return default value
                return self.getDefaultUncertainty(result)
        return self.getDefaultUncertainty(result)

    def getSample(self, result=None):
        """ Conform to Analysis
        """
        return self.aq_parent

    security.declarePublic('setResult')

    def setResult(self, value, **kw):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        self.getField('Result').set(self, value, **kw)

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def isInstrumentValid(self):
        """ Checks if the instrument selected for this analysis
            is valid. Returns false if an out-of-date or uncalibrated
            instrument is assigned. Returns true if the Analysis has
            no instrument assigned or is valid.
        """
        # TODO : Remove when analysis - instrument being assigned directly
        if not self.getInstrument():
            instr = self.getService().getInstrument() \
                    if self.getService().getInstrumentEntryOfResults() \
                    else None
            if instr:
                self.setInstrument(instr)
        # ---8<--------

        return self.getInstrument().isValid() \
                if self.getInstrument() else True

    def isInstrumentAllowed(self, instrument):
        """ Checks if the specified instrument can be set for this
            analysis, according to the Method and Analysis Service.
            If the Analysis Service hasn't set 'Allows instrument entry'
            of results, returns always False. Otherwise, checks if the
            method assigned is supported by the instrument specified.
            The behavoir when no method assigned is different from
            Regular analyses: when no method assigned, the available
            methods for the analysis service are checked and returns
            true if at least one of the methods has support for the
            instrument specified.
        """
        service = self.getService()
        if service.getInstrumentEntryOfResults() is False:
            return False

        if isinstance(instrument, str):
            uid = instrument
        else:
            uid = instrument.UID()

        method = self.getMethod()
        instruments = []
        if not method:
            # Look for Analysis Service methods and instrument support
            instruments = service.getRawInstruments()
        else:
            instruments = method.getInstrumentUIDs()

        return uid in instruments

    def isMethodAllowed(self, method):
        """ Checks if the ref analysis can follow the method specified.
            Looks for manually selected methods when AllowManualResultsEntry
            is set and looks for instruments methods when
            AllowInstrumentResultsEntry is set.
            method param can be either an uid or an object
        """
        if isinstance(method, str):
            uid = method
        else:
            uid = method.UID()

        service = self.getService()
        if service.getManualEntryOfResults() is True \
            and uid in service.getRawMethods():
            return True

        if service.getInstrumentEntryOfResults() is True:
            for ins in service.getInstruments():
                if uid == ins.getRawMethod():
                    return True

        return False

    def getAnalyst(self):
        """ Returns the identifier of the assigned analyst. If there is
            no analyst assigned, and this analysis is attached to a
            worksheet, retrieves the analyst assigned to the parent
            worksheet
        """
        field = self.getField('Analyst')
        analyst = field and field.get(self) or ''
        if not analyst:
            # Is assigned to a worksheet?
            wss = self.getBackReferences('WorksheetAnalysis')
            if len(wss) > 0:
                analyst = wss[0].getAnalyst()
                field.set(self, analyst)
        return analyst if analyst else ''

    def getAnalystName(self):
        """ Returns the name of the currently assigned analyst
        """
        mtool = getToolByName(self, 'portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member is not None:
            return analyst_member.getProperty('fullname')
        else:
            return ''

    def getFormattedResult(self, specs=None, decimalmark='.', sciformat=1):
        """Formatted result:
        1. If the result is not floatable, return it without being formatted
        2. If the analysis specs has hidemin or hidemax enabled and the
           result is out of range, render result as '<min' or '>max'
        3. If the result is floatable, render it to the correct precision
        specs param is optional. A dictionary as follows:
            {'min': <min_val>,
             'max': <max_val>,
             'error': <error>,
             'hidemin': <hidemin_val>,
             'hidemax': <hidemax_val>}
        :param sciformat: 1. The sci notation has to be formatted as aE^+b
                          2. The sci notation has to be formatted as a·10^b
                          3. As 2, but with super html entity for exp
                          4. The sci notation has to be formatted as a·10^b
                          5. As 4, but with super html entity for exp
                          By default 1
        """
        result = self.getResult()
        service = self.getService()

        # 1. If the result is not floatable, return it without being formatted
        try:
            result = float(result)
        except:
            return result

        # 2. If the analysis specs has enabled hidemin or hidemax and the
        #    result is out of range, render result as '<min' or '>max'
        belowmin = False
        abovemax = False
        if not specs:
            uid = self.getServiceUID()
            specs = self.aq_parent.getResultsRangeDict().get(uid, {})
        hidemin = specs.get('hidemin', '')
        hidemax = specs.get('hidemax', '')
        try:
            belowmin = hidemin and result < float(hidemin) or False
        except:
            belowmin = False
            pass
        try:
            abovemax = hidemax and result > float(hidemax) or False
        except:
            abovemax = False
            pass

        # 2.1. If result is below min and hidemin enabled, return '<min'
        if belowmin:
            return formatDecimalMark('< %s' % hidemin, decimalmark)

        # 2.2. If result is above max and hidemax enabled, return '>max'
        if abovemax:
            return formatDecimalMark('> %s' % hidemax, decimalmark)

        # 3. If the result is floatable, render it to the correct precision
        return formatDecimalMark(format_numeric_result(self, result, sciformat), decimalmark)

    def getPrecision(self, result=None):
        """
        Returns the precision for the Analysis.
        - ManualUncertainty not set: returns the precision from the
            AnalysisService.
        - ManualUncertainty set and Calculate Precision from Uncertainty
          is also set in Analysis Service: calculates the precision of the
          result according to the manual uncertainty set.
        - ManualUncertainty set and Calculatet Precision from Uncertainty
          not set in Analysis Service: returns the result as-is.
        Further information at AnalysisService.getPrecision()
        """
        serv = self.getService()
        schu = self.Schema().getField('Uncertainty').get(self)
        if schu and serv.getAllowManualUncertainty() == True \
            and serv.getPrecisionFromUncertainty() == True:
            uncertainty = self.getUncertainty(result)
            if uncertainty == 0:
                return 1
            return get_significant_digits(uncertainty)
        else:
            return serv.getPrecision(result)

    def isVerifiable(self):
        """
        Checks it the current analysis can be verified. This is, its not a
        cancelled analysis and has no dependenant analyses not yet verified
        :return: True or False
        """
        # Check if the analysis is active
        workflow = getToolByName(self, "portal_workflow")
        objstate = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if objstate == "cancelled":
            return False

        # Check if the analysis state is to_be_verified
        review_state = workflow.getInfoFor(self, "review_state")
        if review_state != 'to_be_verified':
            return False

        # Check if the analysis has dependencies not yet verified
        for d in self.getDependencies():
            review_state = workflow.getInfoFor(d, "review_state")
            if review_state in (
                    "to_be_sampled", "to_be_preserved", "sample_due",
                    "sample_received", "attachment_due", "to_be_verified"):
                return False

        # All checks passsed
        return True

    def isUserAllowedToVerify(self, member):
        """
        Checks if the specified user has enough privileges to verify the
        current analysis. Apart of roles, the function also checks if the
        option IsSelfVerificationEnabled is set to true at Service or
        Bika Setup levels and validates if according to this value, together
        with the user roles, the analysis can be verified. Note that this
        function only returns if the user can verify the analysis, but not if
        the analysis is ready to be verified (see isVerifiable)
        :member: user to be tested
        :return: true or false
        """
        # Check if the user has "Bika: Verify" privileges
        username = member.getUserName()
        allowed = api.user.has_permission(VerifyPermission, username=username)
        if not allowed:
            return False

        # Check if the user who submited the result is the same as the current
        workflow = getToolByName(self, "portal_workflow")
        user_id = member.getUser().getId()
        self_submitted = False
        try:
            review_history = workflow.getInfoFor(self, "review_history")
            review_history = self.reverseList(review_history)
            for event in review_history:
                if event.get("action") == "submit":
                    self_submitted = event.get("actor") == user_id
                    break
        except WorkflowException:
            # https://jira.bikalabs.com/browse/LIMS-2037;
            # Sometimes the workflow history is inexplicably missing!
            # Let's assume the user that submitted the result is not the same
            # as the current logged user
            self_submitted = False

        # The submitter and the user must be different unless the analysis has
        # the option SelfVerificationEnabled set to true
        selfverification = self.getService().isSelfVerificationEnabled()
        if self_submitted and not selfverification:
            return False

        # All checks pass
        return True

    def guard_verify_transition(self):
        """
        Checks if the verify transition can be performed to the current
        Analysis by the current user depending on the user roles, as
        well as the status of the analysis
        :return: true or false
        """
        mtool = getToolByName(self, "portal_membership")
        checkPermission = mtool.checkPermission
        # Check if the analysis is in a "verifiable" state
        if self.isVerifiable():
            # Check if the user can verify the analysis
            member = mtool.getAuthenticatedMember()
            return self.isUserAllowedToVerify(member)
        return False

    def workflow_script_submit(self):
        if skip(self, "submit"):
            return
        workflow = getToolByName(self, "portal_workflow")
        self.reindexObject(idxs=["review_state", ])
        # If all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
        if ws.getAnalyst() and not skip(ws, "submit", peek=True):
            all_submitted = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                   ('sample_due', 'sample_received', 'assigned',):
                    all_submitted = False
                    break
            if all_submitted:
                workflow.doActionFor(ws, 'submit')
        # If no problem with attachments, do 'attach' action.
        can_attach = True
        if not self.getAttachment():
            service = self.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            workflow.doActionFor(self, 'attach')

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])

        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                   ('sample_due', 'sample_received', 'attachment_due', 'assigned',):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, 'attach')

    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # Escalate action to the Worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if not skip(ws, "retract", peek=True):
            if workflow.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, "retract")
            else:
                if not "retract all analyses" in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append("retract all analyses")
                workflow.doActionFor(ws, 'retract')

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])

        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        if ws and len(ws) > 0:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state == 'to_be_verified' and not skip(ws, "verify", peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, 'review_state') in \
                       ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified', 'assigned'):
                        all_verified = False
                        break
                if all_verified:
                    if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append("verify all analyses")
                    workflow.doActionFor(ws, "verify")

    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
        if 'context_uid' in self.REQUEST:
            wsUID = self.REQUEST['context_uid']
            ws = rc.lookupObject(wsUID)

            # retract the worksheet to 'open'
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state != 'open':
                if 'workflow_skiplist' not in self.REQUEST:
                    self.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
                else:
                    self.REQUEST["workflow_skiplist"].append('retract all analyses')
                workflow.doActionFor(ws, 'retract')

    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = False

        analyses = ws.getAnalyses()

        # We flag this worksheet as empty if there is ONE UNASSIGNED
        # analysis left: worksheet.removeAnalysis() hasn't removed it from
        # the layout yet at this stage.
        if len(analyses) == 1 \
           and workflow.getInfoFor(analyses[0], 'review_state') == 'unassigned':
            ws_empty = True

        for a in analyses:
            a_state = workflow.getInfoFor(a, 'review_state')
            if a_state in \
               ('assigned', 'sample_due', 'sample_received',):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due',):
                can_attach = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one self).
            if can_submit and workflow.getInfoFor(ws, 'review_state') == 'open':
                workflow.doActionFor(ws, 'submit')
                skip(ws, 'submit', unskip=True)
            if can_attach and workflow.getInfoFor(ws, 'review_state') == 'attachment_due':
                workflow.doActionFor(ws, 'attach')
                skip(ws, 'attach', unskip=True)
            if can_verify and workflow.getInfoFor(ws, 'review_state') == 'to_be_verified':
                self.REQUEST["workflow_skiplist"].append('verify all analyses')
                workflow.doActionFor(ws, 'verify')
                skip(ws, 'verify', unskip=True)
        else:
            if workflow.getInfoFor(ws, 'review_state') != 'open':
                workflow.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)


registerType(ReferenceAnalysis, PROJECTNAME)
