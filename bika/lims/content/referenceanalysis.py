# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import logger, deprecated
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME, STD_TYPES
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.subscribers import skip
from bika.lims.utils.analysis import get_significant_digits
from plone.app.blob.field import BlobField
from zope.interface import implements
from plone.api.user import has_permission

schema = schema.copy() + Schema((
    StringField(
        'ReferenceType',
        vocabulary=STD_TYPES,
    ),
    BlobField(
        'RetractedAnalysesPdfReport',
    ),
    StringField(
        'ReferenceAnalysesGroupID',
    )
))


class ReferenceAnalysis(AbstractAnalysis):
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getSupplierUID(self):
        return self.aq_parent.aq_parent.UID()

    @deprecated("You should use the Reference Analysis title directly.")
    def Title(self):
        """Return the Service ID as title
        Titles of analyses are always the same as the title of the service.
        """
        s = self.getService()
        s = s and s.Title() or ''
        return safe_unicode(s).encode('utf-8')

    def getDefaultUncertainty(self, result=None):
        """ Calls self.Service.getUncertainty with either the provided
            result value or self.Result
        """
        return self.getService().getUncertainty(
            result and result or self.getResult())

    def getUncertainty(self, result=None):
        """ Returns the uncertainty for this analysis and result.
            Returns the value from Schema's Uncertainty field if the
            Service has the option 'Allow manual uncertainty'. Otherwise,
            do a callback to getDefaultUncertainty()
        """
        serv = self.getService()
        schu = self.Schema().getField('Uncertainty').get(self)
        if schu and serv.getAllowManualUncertainty():
            try:
                schu = float(schu)
                return schu
            except ValueError:
                # if uncertainty is not a number, return default value
                return self.getDefaultUncertainty(result)
        return self.getDefaultUncertainty(result)

    def getSample(self):
        """ Conform to Analysis
        """
        return self.aq_parent

    security.declarePublic('setResult')

    def setResult(self, value, **kw):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        self.getField('Result').set(self, value, **kw)

    security.declarePublic('current_date')

    @staticmethod
    def current_date():
        """ return current date """
        return DateTime()

    def getExpiryDate(self):
        """It is used as a metacolumn.
        Returns the expiration date from the reference sample.
        """
        return self.aq_parent.getExpiryDate()

    def getReferenceResults(self):
        """
        It is used as metacolumn
        """
        return self.aq_parent.getReferenceResults()

    def isVerifiable(self):
        """
        Checks it the current analysis can be verified. This is, its not a
        cancelled analysis and has no dependenant analyses not yet verified
        :returns: True or False
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
        :returns: true or false
        """
        # Check if the user has "Bika: Verify" privileges
        username = member.getUserName()
        allowed = has_permission(VerifyPermission, username=username)
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

        # Checking verifiability depending on multi-verification type of
        # bika_setup
        if self.bika_setup.getNumberOfRequiredVerifications() > 1:
            mv_type = self.bika_setup.getTypeOfmultiVerification()
            # If user verified before and self_multi_disabled, then return False
            if mv_type == 'self_multi_disabled' and self.wasVerifiedByUser(
                    username):
                return False

            # If user is the last verificator and consecutively
            # multi-verification
            # is disabled, then return False
            # Comparing was added just to check if this method is called
            # before/after
            # verification
            elif mv_type == 'self_multi_not_cons' and username == \
                    self.getLastVerificator() and \
                            self.getNumberOfVerifications() < \
                            self.getNumberOfRequiredVerifications():
                return False

        # All checks pass
        return True

    def guard_verify_transition(self):
        """
        Checks if the verify transition can be performed to the current
        Analysis by the current user depending on the user roles, as
        well as the status of the analysis
        :returns: true or false
        """
        mtool = getToolByName(self, "portal_membership")
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
        # If all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        # if the worksheet analyst is not assigned, the worksheet can't  be
        # transitioned.
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
        self.reindexObject()

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                        ('sample_due', 'sample_received', 'attachment_due',
                         'assigned',):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, 'attach')
        self.reindexObject()

    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # Escalate action to the Worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if not skip(ws, "retract", peek=True):
            if workflow.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, "retract")
            else:
                if "retract all analyses" \
                        not in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append(
                        "retract all analyses")
                workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        if ws and len(ws) > 0:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state == 'to_be_verified' and not skip(ws, "verify",
                                                         peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, 'review_state') in \
                            ('sample_due', 'sample_received', 'attachment_due',
                             'to_be_verified', 'assigned'):
                        all_verified = False
                        break
                if all_verified:
                    if "verify all analyses" \
                            not in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append(
                            "verify all analyses")
                    workflow.doActionFor(ws, "verify")
        self.reindexObject()

    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        if 'context_uid' in self.REQUEST:
            wsUID = self.REQUEST['context_uid']
            ws = rc.lookupObject(wsUID)

            # retract the worksheet to 'open'
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state != 'open':
                if 'workflow_skiplist' not in self.REQUEST:
                    self.REQUEST['workflow_skiplist'] = [
                        'retract all analyses', ]
                else:
                    self.REQUEST["workflow_skiplist"].append(
                        'retract all analyses')
                workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a
        # review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = False

        analyses = ws.getAnalyses()

        # We flag this worksheet as empty if there is ONE UNASSIGNED
        # analysis left: worksheet.removeAnalysis() hasn't removed it from
        # the layout yet at this stage.
        if len(analyses) == 1 \
                and workflow.getInfoFor(analyses[0],
                                        'review_state') == 'unassigned':
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
                    ('assigned', 'sample_due', 'sample_received',
                     'attachment_due',):
                can_attach = False
            if a_state in \
                    ('assigned', 'sample_due', 'sample_received',
                     'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
            # Note: WS adds itself to the skiplist so we have to take it off
            # again
            #       to allow multiple promotions (maybe by more than one self).
            if can_submit and workflow.getInfoFor(ws, 'review_state') == 'open':
                workflow.doActionFor(ws, 'submit')
                skip(ws, 'submit', unskip=True)
            if can_attach and workflow.getInfoFor(ws,
                                                  'review_state') == \
                    'attachment_due':
                workflow.doActionFor(ws, 'attach')
                skip(ws, 'attach', unskip=True)
            if can_verify and workflow.getInfoFor(ws,
                                                  'review_state') == \
                    'to_be_verified':
                self.REQUEST["workflow_skiplist"].append('verify all analyses')
                workflow.doActionFor(ws, 'verify')
                skip(ws, 'verify', unskip=True)
        else:
            if workflow.getInfoFor(ws, 'review_state') != 'open':
                workflow.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)
        self.reindexObject()


registerType(ReferenceAnalysis, PROJECTNAME)
