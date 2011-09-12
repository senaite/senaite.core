from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ObjectInitializedEventHandler(analysis, event):
    wf = getToolByName(analysis, 'portal_workflow')
    ar = obj.aq_parent

    # creating a new analysis retracts parent AR to 'received'
    ar_state = wf.getInfoFor(ar, 'review_state')
    if ar_state not in ('sample_due', 'sample_received'):
        ar._skip_ActionSucceededEventHandler
        wf.doActionFor(ar, 'retract')

def ActionSucceededEventHandler(analysis, event):

    if not hasattr(analysis, '_skip_ActionSucceededEventHandler'):
        logger.info("%s on %s" % (event.action,analysis.getService().getKeyword()))

    wf = getToolByName(analysis, 'portal_workflow')
    pc = getToolByName(analysis, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(analysis, 'plone_utils').addPortalMessage

    if hasattr(analysis, '_skip_ActionSucceededEventHandler'):
        return

    elif event.action == "receive":
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
        analysis.setDueDate(duetime)
        analysis.reindexObject(idxs=["review_state",])

    elif event.action == "assign":
        analysis._assigned_to_worksheet = True
        # Escalate action to the parent AR
        if event.action in [t['id'] for t in wf.getTransitionsFor(analysis.aq_parent)]:
            wf.doActionFor(analysis.aq_parent, event.action)

    elif event.action == "submit":
        # Submit our dependents
        dependents = analysis.getDependents()
        logger.info("dependents: %s" % dependents)
        for dependent in dependents:
            try:
                wf.doActionFor(dependent, 'submit')
            except WorkflowException:
                pass
        # submit our dependencies,
        dependencies = analysis.getDependencies()
        logger.info("dependencies: %s" % dependencies)
        for dependency in dependencies:
            # if they have a result
            if not dependency.getResult():
                raise WorkflowException
            # and if all their dependents (which are our siblings) are to_be_verified
            for dependent in dependency.getDependents():
                #if dependent == analysis:
                #    continue
                try:
                    wf.doActionFor(dependent, 'submit')
                except WorkflowException:
                    pass
        # Escalate action to the parent AR
        ar = aq_inner(analysis.aq_parent)
        try:
            ar._skip_ActionSucceededEventHandler = True
            wf.doActionFor(ar, 'submit')
        except:
            pass
        finally:
            del ar._skip_ActionSucceededEventHandler

    elif event.action == "retract":
        # Retract our dependents
        for dep in analysis.getDependents():
            try:
                wf.doActionFor(dep, 'retract')
                if dep._assigned_to_worksheet:
                    wf.doActionFor(dep, 'assign')
            except WorkflowException:
                pass
        # retract our dependencies
        for dependency in analysis.getDependencies():
            if wf.getInfoFor(dependency, 'review_state') == 'sample_received':
                continue
            for dependent in dependency.getDependents():
                try:
                    wf.doActionFor(dependent, 'retract')
                except WorkflowException:
                    pass
        # Escalate action to the parent AR
        ar = aq_inner(analysis.aq_parent)
        try:
            ar._skip_ActionSucceededEventHandler = True
            wf.doActionFor(ar, 'retract')
            if ar._assigned_to_worksheet:
                wf.doActionFor(ar, 'assign')
        except:
            pass
        finally:
            del ar._skip_ActionSucceededEventHandler
        # if we are assigned to a worksheet, our new
        # state must be 'assigned', not 'received'.
        # XXX hacky, analysis should have multiple workflows
        if analysis._assigned_to_worksheet:
            wf.doActionFor(analysis, 'assign')

    elif event.action == "verify":
        # fail if we are the same user who submitted this analysis
        mt = getToolByName(analysis, 'portal_membership')
        member = mt.getAuthenticatedMember()
        if 'Manager' not in member.getRoles():
            review_history = wf.getInfoFor(analysis, 'review_history')
            review_history.reverse()
            for e in review_history:
                if e.get('action') == 'submit':
                    if e.get('actor') == user.getId():
                        transaction.abort()
                        raise WorkflowException, _("Results cannot be verified by the submitting user.")
                    break
        # Check our dependencies, if their deps are satisfied, verify them.
        for dependency in analysis.getDependencies():
            if wf.getInfoFor(dependency, 'review_state') == 'verified':
                continue
            can_submit_dependency = True
            for dependent in dependency.getDependents():
                if wf.getInfoFor(dependent, 'review_state') != 'verified':
                    can_submit_dependency = False
                    break
            if can_submit_dependency:
                try:
                    wf.doActionFor(dependency, 'verify')
                except WorkflowException:
                    pass
        # Check for dependents, verify that all their dependencies are
        # ready, and verify them
        for dependent in analysis.getDependents():
            if wf.getInfoFor(dependent, 'review_state') == 'verified':
                continue
            can_submit_dependent = True
            for dependency in dependent.getDependencies():
                if wf.getInfoFor(dependency, 'review_state') != 'verified':
                    can_submit_dependent = False
                    break
            if can_submit_dependent:
                try:
                    wf.doActionFor(dependent, 'verify')
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
        ar = analysis.aq_parent
        for a in ar.getAnalyses():
            if a.review_state in \
               ('sample_due', 'sample_received', 'to_be_verified'):
                all_verified = False
                break
        if all_verified:
            try:
                ar._skip_ActionSucceededEventHandler = True
                wf.doActionFor(ar, event.action)
            except WorkflowAction:
                pass
            finally:
                del ar._skip_ActionSucceededEventHandler

    elif event.action == "publish":
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
        analysis.reindexObject(idxs=["review_state",])

