from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

#try:
#    from bika.limsCalendar.config import TOOL_NAME as BIKA_CALENDAR_TOOL
#except:
#    pass


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
        maxtime = service.getMaxTimeAllowed()

        if not maxtime:
            maxtime = {'days':0, 'hours':0, 'minutes':0}
        analysis.setMaxTimeAllowed(maxtime)
        # set the due date
        starttime = analysis.aq_parent.getDateReceived()
        # default to old calc in case no calendars
        # still need a due time for selection to ws
        max_days = float(maxtime.get('days', 0)) + \
                 (
                     (float(maxtime.get('hours', 0)) * 3600 + \
                      float(maxtime.get('minutes', 0)) * 60 )
                     / 86400
                 )
        duetime = starttime + max_days
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
        try:
            workflow.doActionFor(analysis.aq_parent, event.action)
        except WorkflowException:
            pass

    if event.action == "verify":
        # fail if we are the same user who submitted this analysis
        mt = getToolByName(analysis, 'portal_membership')
        member = mt.getAuthenticatedMember()
        if 'Manager' not in member.getRoles():
            # fail if we are the user who submitted this analysis
            review_history = workflow.getInfoFor(analysis, 'review_history')
            review_history.reverse()
            for e in review_history:
                if e.get('action') == 'submit':
                    if e.get('actor') == user.getId():
                        transaction.abort()
                        raise WorkflowException, _("Results cannot be verified by the submitting user.")
                    break
        # Verify any dependent services
        for dep in analysis.getDependents():
            try:
                workflow.doActionFor(dep, event.action)
            except WorkflowException:
                pass
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
            if a.review_state in \
               ('sample_due', 'sample_received', 'to_be_verified'):
                all_verified = False
                break
        if all_verified:
            try:
                workflow.doActionFor(analysis.aq_parent, event.action)
            except WorkflowExfeption:
                pass

    if event.action == "retract":
        # Retract our dependencies
        for dep in analysis.getDependencies():
            try:
                workflow.doActionFor(dep, event.action)
                if dep._assigned_to_worksheet:
                    workflow.doActionFor(dep, 'assign')
            except:
                pass
        # Retract our dependents
        for dep in analysis.getDependents():
            try:
                workflow.doActionFor(dep, event.action)
                if dep._assigned_to_worksheet:
                    workflow.doActionFor(dep, 'assign')
            except:
                pass
        # Escalate action to the parent AR
        try:
            analysis.aq_parent._skip_ActionSucceededEvent = True
            workflow.doActionFor(analysis.aq_parent, event.action)
            if analysis.aq_parent._assigned_to_worksheet:
                workflow.doActionFor(analysis.aq_parent, 'assign')
            if hasattr(analysis.aq_parent, '_skip_ActionSucceededEvent'):
                del analysis.aq_parent._skip_ActionSucceededEvent
        except:
            pass
        # if we are assigned to a worksheet, our new
        # state must be 'assigned', not 'received'.
        # XXX hacky, analysis should have multiple workflows
        if analysis._assigned_to_worksheet:
            workflow.doActionFor(analysis, 'assign')
            analysis.reindexObject()

    if event.action == "publish":
        endtime = DateTime()
        analysis.setDateAnalysisPublished(endtime)
        starttime = analysis.aq_parent.getDateReceived()
        service = analysis.getService()
        maxtime = service.getMaxTimeAllowed()
        # set the analysis duration value to default values
        # in case of no calendars or max hours
        if maxtime:
            duration = (endtime - starttime) * 24 * 60
            earliness = duration - maxtime.timedelta()
        else:
            earliness = 0
            duration = 0
##        try:
##            bct = getToolByName(analysis, BIKA_CALENDAR_TOOL)
##        except:
##        bct = None
##        if bct:
##            duration = bct.getDuration(starttime, endtime)
##            # set the earliness of the analysis
##            # will be negative if late
##            if analysis.getDueDate():
##                earliness = bct.getDuration(endtime,
##                                        self.getDueDate())
        analysis.setDuration(duration)
        analysis.setEarliness(earliness)
        analysis.reindexObject()

