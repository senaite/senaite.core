# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.schema.referenceanalysis import schema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.subscribers import skip
from bika.lims.workflow import doActionFor
from zope.interface import implements


class ReferenceAnalysis(AbstractAnalysis):
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getSupplier(self):
        """ Returns the Supplier of the ReferenceSample this ReferenceAnalysis
        refers to
        """
        sample = self.getSample()
        if sample:
            return sample.aq_parent

    @security.public
    def getSupplierUID(self):
        supplier = self.getSupplier()
        if supplier:
            return supplier.UID()

    @security.public
    def getSample(self):
        """ Returns the ReferenceSample this ReferenceAnalysis refers to
        Delegates to self.aq_parent
        """
        return self.aq_parent

    @security.public
    def getDueDate(self):
        """Used to populate getDueDate index and metadata. This very simply 
        returns the expiry date of the parent reference sample.
        """
        sample = self.getSample()
        if sample:
            return sample.getExpiryDate()

    @security.public
    def setResult(self, value):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        val = str(value).strip()
        self.getField('Result').set(self, val)

    def getExpiryDate(self):
        """It is used as a metacolumn.
        Returns the expiration date from the reference sample.
        """
        return self.getSample().getExpiryDate()

    def getReferenceResults(self):
        """It is used as metacolumn
        """
        return self.getSample().getReferenceResults()


    def getInstrumentEntryOfResults(self):
        """It is a metacolumn. Returns the same value as the service.
        """
        service = self.getService()
        if not service:
            return None

            return service.getInstrumentEntryOfResults()

    def getInstrumentUID(self):
        """ It is a metacolumn. Returns the same value as the service.
        """
        instrument = self.getInstrument()
        if not instrument:
            return None
        return instrument.UID()

    def getServiceDefaultInstrumentUID(self):
        """ It is used as a metacolumn. Returns the default service's 
        instrument UID
        """
        service = self.getService()
        if not service:
            return None
        ins = service.getInstrument()
        if ins:
            return ins.UID()
        return ''

    def getServiceDefaultInstrumentTitle(self):
        """ It is used as a metacolumn. Returns the default service's 
        instrument UID
        """
        service = self.getService()
        if not service:
            return None
        ins = service.getInstrument()
        if ins:
            return ins.Title()
        return ''

    def getServiceDefaultInstrumentURL(self):
        """ It is used as a metacolumn. Returns the default service's 
        instrument UID
        """
        service = self.getService()
        if not service:
            return None
        ins = service.getInstrument()
        if ins:
            return ins.absolute_url_path()
        return ''

    def getDependencies(self):
        """It doesn't make sense for a ReferenceAnalysis to use
        dependencies, since them are only used in calculations for
        routine analyses
        """
        return []

    @security.public
    def after_submit_transition_event(self):
        """Method triggered after a 'submit' transition for the current
        ReferenceAnalysis is performed.
        By default, the "submit" action for transitions the RefAnalysis to the
        "attachment_due" state. If attachment is not required, the Reference
        Analysis is transitioned to 'to_be_verified' state (via 'attach').
        If all the analyses that belong to the same worksheet are in a suitable
        state, the 'submit' transition to the worksheet is triggered too.
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        # By default, the 'submit' action transitions the ReferenceAnalysis to
        # the 'attachment_due'. Since doActionFor already checks for the guards
        # in this case (guard_attach_transition), try always the transition to
        # 'to_be_verified' via 'attach' action
        # doActionFor will check the
        doActionFor(self, 'attach')

        # Delegate the transition of Worksheet to base class AbstractAnalysis
        super(AbstractAnalysis, self).after_submit_transition_event()

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


registerType(ReferenceAnalysis, PROJECTNAME)
