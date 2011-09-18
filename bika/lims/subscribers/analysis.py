from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ObjectInitializedEventHandler(analysis, event):

    logger.info("Starting: %s on %s" % (event.action, analysis.getService().getKeyword()))

    # creating a new analysis retracts parent AR to 'received'
    ar = analysis.aq_parent
    wf = getToolByName(analysis, 'portal_workflow')
    ar_state = wf.getInfoFor(ar, 'review_state')
    if ar_state not in ('sample_due', 'sample_received'):
        if not analysis.REQUEST.has_key('workflow_skiplist'):
            analysis.REQUEST['workflow_skiplist'] = [ar.UID(), ]
        else:
            analysis.REQUEST["workflow_skiplist"].append(ar.UID())
        wf.doActionFor(ar, 'retract')

    return

def ActionSucceededEventHandler(analysis, event):

    if event.action == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not analysis.REQUEST.has_key('workflow_attach_skiplist'):
            analysis.REQUEST['workflow_attach_skiplist'] = [analysis.UID(), ]
            skiplist = analysis.REQUEST['workflow_attach_skiplist']
        else:
            skiplist = analysis.REQUEST['workflow_attach_skiplist']
            if analysis.UID() in skiplist:
                logger.info("an Skip")
                return
            else:
                analysis.REQUEST["workflow_attach_skiplist"].append(analysis.UID())

        logger.info("Starting: %s on %s" % (event.action, analysis.getService().getKeyword()))

        wf = getToolByName(analysis, 'portal_workflow')
        ar = analysis.aq_parent

        analysis.reindexObject(idxs = ["review_state", ])
        # Dependencies are already at least 'to_be_verified', ignore them.
        #----------------------------------------------------------------
        # Check our dependents:
        # If    it is 'attachment_due'
        # And   it's attachments are OK
        # And   all it's dependencies are at least 'to_be_verified'
        # Then: 'attach' it.:
        dependents = analysis.getDependents()
        for dependent in dependents:
            if not dependent.UID() in skiplist:
                can_attach = True
                if wf.getInfoFor(dependent, 'review_state') != 'attachment_due':
                    can_attach = False
                else:
                    if not dependent.getAttachment():
                        service = dependent.getService()
                        if service.getAttachmentOption() == 'r':
                            can_attach = False
                if can_attach:
                    dependencies = dependent.getDependencies()
                    for dependency in dependencies:
                        if wf.getInfoFor(dependency, 'review_state') in ('sample_due', 'sample_received', 'attachment_due',):
                            can_attach = False
                if can_attach:
                    wf.doActionFor(dependent, 'attach')

        # If all analyses in this AR have been attached
        # escalate the action to the parent AR
        if not ar.UID() in skiplist:
            can_attach = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received', 'attachment_due',):
                    can_attach = False
                    break
            if can_attach:
                wf.doActionFor(ar, 'attach')

        return

    #------------------------------------------------------
    # End of "attach" code, back to your basic nightmare...
    #------------------------------------------------------

    if not analysis.REQUEST.has_key('workflow_skiplist'):
        analysis.REQUEST['workflow_skiplist'] = [analysis.UID(), ]
        skiplist = analysis.REQUEST['workflow_skiplist']
    else:
        skiplist = analysis.REQUEST['workflow_skiplist']
        if analysis.UID() in skiplist:
            logger.info("an Skip")
            return
        else:
            analysis.REQUEST["workflow_skiplist"].append(analysis.UID())

    logger.info("Starting: %s on %s" % (event.action, analysis.getService().getKeyword()))

    wf = getToolByName(analysis, 'portal_workflow')
    ar = analysis.aq_parent

    if event.action == "receive":
        # set the max hours allowed
        service = analysis.getService()
        maxtime = service.getMaxTimeAllowed()

        if not maxtime:
            maxtime = {'days':0, 'hours':0, 'minutes':0}
        analysis.setMaxTimeAllowed(maxtime)
        # set the due date
        starttime = ar.getDateReceived()
        # default to old calc in case no calendars
        # still need a due time for selection to ws
        max_days = float(maxtime.get('days', 0)) + \
                 (
                     (float(maxtime.get('hours', 0)) * 3600 + \
                      float(maxtime.get('minutes', 0)) * 60)
                     / 86400
                 )
        duetime = starttime + max_days
        analysis.setDueDate(duetime)
        analysis.reindexObject()

    elif event.action == "submit":
        analysis.reindexObject(idxs = ["review_state", ])
        # Dependencies are submitted already, ignore them.
        # Dependents are submitted separately, ignore them.
        #-------------------------------------------------
        # If all analyses in this AR have been submitted
        # escalate the action to the parent AR
        if not ar.UID() in skiplist:
            all_submitted = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received',):
                    all_submitted = False
                    break
            if all_submitted:
                wf.doActionFor(ar, 'submit')

        # If no problem with attachments, do 'attach' action for this analysis.
        can_attach = True
        if not analysis.getAttachment():
            service = analysis.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            dependencies = analysis.getDependencies()
            for dependency in dependencies:
                if wf.getInfoFor(dependency, 'review_state') in ('sample_due', 'sample_received', 'attachment_due',):
                    can_attach = False
        if can_attach:
            wf.doActionFor(analysis, 'attach')

    elif event.action == "retract":
        analysis.reindexObject(idxs = ["review_state", ])
        # retract our dependencies
        for dependency in analysis.getDependencies():
            if not dependency.UID() in skiplist:
                if wf.getInfoFor(dependency, 'review_state') in ('attachment_due', 'to_be_verified', 'verified',):
                    # (NB: don't retract if it's published)
                    wf.doActionFor(dependency, 'retract')
        # Retract our dependents
        for dep in analysis.getDependents():
            if not dep.UID() in skiplist:
                if wf.getInfoFor(dep, 'review_state') != 'sample_received':
                    wf.doActionFor(dep, 'retract')
        # Escalate action to the parent AR
        if not ar.UID() in skiplist:
            if wf.getInfoFor(ar, 'review_state') == 'sample_received':
                analysis.REQUEST["workflow_skiplist"].append(ar.UID())
            else:
                if not "retract all analyses" in skiplist:
                    analysis.REQUEST["workflow_skiplist"].append("retract all analyses")
                wf.doActionFor(ar, 'retract')

    elif event.action == "verify":
        analysis.reindexObject(idxs = ["review_state", ])
        # fail if we are the same user who submitted this analysis
        mt = getToolByName(analysis, 'portal_membership')
        member = mt.getAuthenticatedMember()
        user = getSecurityManager().getUser()
        if 'Manager' not in member.getRoles():
            review_history = wf.getInfoFor(analysis, 'review_history')
            review_history.reverse()
            for e in review_history:
                if e.get('action') == 'submit':
                    if e.get('actor') == user.getId():
                        transaction.abort()
                        raise WorkflowException, _("Results cannot be verified by the submitting user.")
                    break

        # Verify our dependencies.
        for dependency in analysis.getDependencies():
            # Don't have to check if they're 'to_be_verified'.
            # If this analysis is, they must be too.
            if not dependency.UID() in skiplist:
                wf.doActionFor(dependency, 'verify')

        # Check for dependents, ensure all their dependencies
        # have been verified, and verify them
        for dependent in analysis.getDependents():
            if not dependent.UID() in skiplist:
                if wf.getInfoFor(dependent, 'review_state') == 'to_be_verified':
                    can_verify_dependent = True
                    for dependency in dependent.getDependencies():
                        if not dependency.UID() in skiplist:
                            if wf.getInfoFor(dependency, 'review_state') in \
                               ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified'):
                                can_verify_dependent = False
                                break
                    if can_verify_dependent:
                        wf.doActionFor(dependent, 'verify')

        # If all analyses in this AR are verified
        # escalate the action to the parent AR
        if not ar.UID() in skiplist:
            all_verified = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified'):
                    all_verified = False
                    break
            if all_verified:
                wf.doActionFor(ar, "verify")

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
        analysis.reindexObject()

    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.action == "assign":
        analysis.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        # If all analyses in this AR have been assigned
        # escalate the action to the parent AR
        if not ar.UID() in skiplist:
            if not ar.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
                wf.doActionFor(ar, 'assign')

    elif event.action == "unassign":
        analysis.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        # Escalate the action to the parent AR if it is assigned
        if not ar.UID() in skiplist:
            if wf.getInfoFor(ar, 'worksheetanalysis_review_state') == 'assigned':
                wf.doActionFor(ar, 'unassign')

    return
