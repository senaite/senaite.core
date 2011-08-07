from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction


def ActionSucceededEventHandler(analysis, event):
    workflow = getToolByName(analysis, 'portal_workflow')
    pc = getToolByName(analysis, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(analysis, 'plone_utils').addPortalMessage

    # set this before transitioning to prevent this handler from reacting
    if hasattr(analysis, '_skip_ActionSucceededEvent'):
        del analysis._skip_ActionSucceededEvent
        return

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

    if event.action == "assign":
        analysis._assigned_to_worksheet = True
        # Escalate action to the parent AR
        if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            workflow.doActionFor(analysis.aq_parent, event.action)

    if event.action == "submit":
        # Check for dependents, verify that all their dependencies are
        # ready, and submit them
        for dependent in analysis.getDependents():
            if workflow.getInfoFor(dependent, 'review_state') == 'to_be_verified':
                continue
            can_submit_dependent = True
            for dependency in dependent.getDependencies():
                if workflow.getInfoFor(dependency, 'review_state') == 'sample_received':
                    can_submit_dependent = False
                    break
            if can_submit_dependent:
                workflow.doActionFor(dependent, event.action)

        # Escalate action to the parent AR
        if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            workflow.doActionFor(analysis.aq_parent, event.action)

    if event.action == "verify":
        # fail if we are the same user who submitted this analysis
        review_history = workflow.getInfoFor(analysis, 'review_history')
        review_history.reverse()
        for e in review_history:
            if e.get('action') == 'submit':
                if e.get('actor') == user.getId():
                    transaction.abort()
                    raise WorkflowException, _("Results cannot be verified by the submitting user.")
                break
##        # Cannot verify analyses with dependencies; they are verified
##        # automatically when all their dependencies are verified.
##        service = analysis.getService()
##        calculation = service.getCalculation()
##        if calculation and calculation.getDependentServices():
##            transaction.abort()
##            return
        # Check for dependents, verify that all their dependencies are
        # ready, and verify them.
        for dependent in analysis.getDependents():
            if workflow.getInfoFor(dependent, 'review_state') == 'verified':
                continue
            can_submit = False
            for dependency in dependent.getDependencies():
                if workflow.getInfoFor(dependency, 'review_state') in \
                   ('sample_received', 'to_be_verified'):
                    can_submit = False
            if can_submit:
                workflow.doActionFor(dependent, event.action)
        # check for required Analysis Attachments
        service = analysis.getService()
        if not analysis.getAttachment():
            if analysis.bika_setup.getAnalysisAttachmentsPermitted():
                if service.getAttachmentOption() == 'r':
                    transaction.abort()
                    raise WorkflowException, _("Required analysis attachment is missing for ") + analysis.Title()
        # If all analyses in this AR are verified
        # escalate the action to the parent AR
        all_verified = True
        for a in analysis.aq_parent.getAnalyses():
            if workflow.getInfoFor(a, 'review_state') in \
               ('sample_due', 'sample_received', 'to_be_verified'):
                all_verified = False
                break
        if all_verified and \
           event.action in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            workflow.doActionFor(analysis.aq_parent, event.action)

    if event.action == "retract":
        # Retract our dependencies
        for dep in analysis.getDependencies():
            if event.action in [t['id'] for t in workflow.getTransitionsFor(dep)]:
                workflow.doActionFor(dep, event.action)
                if dep._assigned_to_worksheet:
                    workflow.doActionFor(dep, 'assign')
        # Retract our dependents
        for dep in analysis.getDependents():
            if event.action in [t['id'] for t in workflow.getTransitionsFor(dep)]:
                workflow.doActionFor(dep, event.action)
                if dep._assigned_to_worksheet:
                    workflow.doActionFor(dep, 'assign')
        # Escalate action to the parent AR
        # hacky: set AR._skip_ActionSucceededEvent so that AR doesn't delegate to our sibling analyses
        if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis.aq_parent)]:
            analysis.aq_parent._skip_ActionSucceededEvent = True
            workflow.doActionFor(analysis.aq_parent, event.action)
            if analysis.aq_parent._assigned_to_worksheet:
                workflow.doActionFor(analysis.aq_parent, 'assign')
        # if we are assigned to a worksheet, our new
        # state must be 'assigned', not 'received'.
        # XXX hacky, analysis should have multiple workflows
        if analysis._assigned_to_worksheet:
            workflow.doActionFor(analysis, 'assign')
            analysis.reindexObject()






