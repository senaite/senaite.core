from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ObjectInitializedEventHandler(analysis, event):

    logger.info("%s on %s" % (event.action, analysis.getService().getKeyword()))

    skiplist = analysis.REQUEST["workflow_skiplist"]
    skiplist.append(analysis.UID())

    # creating a new analysis retracts parent AR to 'received'
    ar = analysis.aq_parent
    if not ar.UID() in skiplist:
        wf = getToolByName(analysis, 'portal_workflow')
        ar_state = wf.getInfoFor(ar, 'review_state')
        if ar_state not in ('sample_due', 'sample_received'):
            wf.doActionFor(ar, 'retract')

def ActionSucceededEventHandler(analysis, event):

    logger.info("%s on %s" % (event.action, analysis.getService().getKeyword()))

    skiplist = analysis.REQUEST["workflow_skiplist"]
    skiplist.append(analysis.UID())

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
        # submit our dependencies,
        dependencies = analysis.getDependencies()
        logger.info("dependencies: %s" % dependencies)
        for dependency in dependencies:
            if not dependency.UID() in skiplist:
                if wf.getInfoFor(dependency, 'review_state') == 'sample_received':
                    wf.doActionFor(dependency, 'submit')

        # Submit our dependents
        # Need to check for result and attachment first
        dependents = analysis.getDependents()
        logger.info("dependents: %s" % dependents)
        for dependent in dependents:
            if not dependent.UID() in skiplist:
                can_submit = True
                if not dependent.getResult():
                    can_submit = False
                else:
                    if not dependent.getAttachment():
                        service = dependent.getService()
                        if service.getAttachmentOption() == 'r':
                            can_submit = False
                if can_submit:
                    wf.doActionFor(dependent, 'submit')

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

    elif event.action == "retract":
        # retract our dependencies
        for dependency in analysis.getDependencies():
            if not dependency.UID() in skiplist:
                if wf.getInfoFor(dependency, 'review_state') != 'sample_received':
                    wf.doActionFor(dependency, 'retract')
        # Retract our dependents
        for dep in analysis.getDependents():
            if not dep.UID() in skiplist:
                if wf.getInfoFor(dep, 'review_state') != 'sample_received':
                    wf.doActionFor(dep, 'retract')
        # Escalate action to the parent AR
        if not ar.UID() in skiplist:
            if wf.getInfoFor(ar, 'review_state') != 'sample_received':
                wf.doActionFor(ar, 'retract')

    elif event.action == "verify":
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
            if not dependency.UID() in skiplist:
                if wf.getInfoFor(dependency, 'review_state') == 'to_be_verified':
                    wf.doActionFor(dependency, 'verify')

        # Check for dependents, verify that all their dependencies are
        # ready, and verify them
        for dependent in analysis.getDependents():
            if not dependent.UID() in skiplist:
                if wf.getInfoFor(dependent, 'review_state') == 'to_be_verified':
                    can_verify_dependent = True
                    for dependency in dependent.getDependencies():
                        if not dependency.UID() in skiplist:
                            if wf.getInfoFor(dependency, 'review_state') in \
                               ('sample_due', 'sample_received', 'to_be_verified'):
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
                   ('sample_due', 'sample_received', 'to_be_verified'):
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

