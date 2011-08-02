from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ActionSucceededEventHandler(analysis, event):
    workflow = getToolByName(analysis, 'portal_workflow')
    pc = getToolByName(analysis, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(analysis, 'plone_utils').addPortalMessage

    if event.action == "receive":
        # set the max hours allowed
        service = analysis.getService()
        maxhours = service.getMaxHoursAllowed()
        if not maxhours:
            maxhours = 0
        analysis.setMaxHoursAllowed(maxhours)
        # set the due date
        starttime = analysis.aq_parent.getDateReceived()
        # default to old calc in case no calendars
        # still need a due time for selection to ws
        duetime = starttime + maxhours / 24.0
##        if maxhours:
##            maxminutes = maxhours * 60
##            try:
##                bct = getToolByName(self, BIKA_CALENDAR_TOOL)
##            except:
##                bct = None
##            if bct:
##                duetime = bct.getDurationAdded(starttime, maxminutes)
        analysis.setDueDate(duetime)
        analysis.reindexObject()

    if event.action == "submit":
        # if we are submitting a calculated result, then also
        # submit dependent services.
        service = analysis.getService()
        calculation = service.getCalculation()
        if calculation:
            for dep in calculation.getDependentServices():
                if event.action in [t['id'] for t in workflow.getTransitionsFor(dep)]:
                    workflow.doActionFor(dep, event.action)
        # Escalate submission to the AR
        if 'submit' in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            workflow.doActionFor(analysis.aq_parent, 'submit')

    if event.action == "verify":
        # fail if we are the same user who submitted this analysis
        review_history = workflow.getInfoFor(analysis, 'review_history')
        review_history.reverse()
        for event in review_history:
            if event.get('action') == 'submit':
                if event.get('actor') == user.getId():
                    transaction.abort()
                    raise WorkflowException, _("Results cannot be verified by the submitting user.")
                break
        # if we are verifying a calculated result, then also
        # verify dependent services.
        service = analysis.getService()
        calculation = service.getCalculation()
        if calculation:
            for dep in calculation.getDependentServices():
                if 'verify' in [t['id'] for t in workflow.getTransitionsFor(dep)]:
                    workflow.doActionFor(dep, 'verify')
        # check if required analysis attachment is present
        if not analysis.getAttachment():
            if analysis.bika_settings.getAnalysisAttachmentsPermitted():
                if service.getAttachmentOption() == 'r':
                    transaction.abort()
                    raise WorkflowException, _("Required analysis attachment is missing for ") + analysis.Title()
        # Escalate verification to the AR
        if 'verify' in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            workflow.doActionFor(analysis.aq_parent, 'verify')

    if event.action == "retract":
        # retract our parent AR
        # retract calculated analyses in our AR if they depend on us.
        #
        self._escalateWorkflowDependancies('retract')
        self._escalateWorkflowAction('retract')
        if self._assigned_to_worksheet:
            self.portal_workflow.doActionFor(self, 'assign')
            self.reindexObject()
            self._escalateWorkflowDependancies('assign')
            self._escalateWorkflowAction('assign')
