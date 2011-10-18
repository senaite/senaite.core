from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ObjectInitializedEventHandler(analysis, event):

    # This handler fires for DuplicateAnalysis because
    # DuplicateAnalysis also provides IAnalysis.
    # DuplicateAnalysis doesn't have analysis_workflow.
    if analysis.portal_type == "DuplicateAnalysis":
        return

    logger.info("ObjectInitialized: %s" % analysis.getService().getKeyword())

    # 'receive' analysis if AR is received.
    # Adding a new analysis to an AR retracts the AR to 'received'
    ar = analysis.aq_parent
    wf = getToolByName(analysis, 'portal_workflow')
    ar_state = wf.getInfoFor(ar, 'review_state')
    if ar_state != 'sample_due':
        wf.doActionFor(analysis, 'receive')
    if ar_state not in ('sample_due', 'sample_received'):
        if not analysis.REQUEST.has_key('workflow_skiplist'):
            analysis.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
        else:
            analysis.REQUEST["workflow_skiplist"].append('retract all analyses')
        wf.doActionFor(ar, 'retract')
    return

def ObjectRemovedEventHandler(analysis, event):

    logger.info("ObjectRemoved: %s" % analysis)

    # May need to promote the AR's review_state
    #  if all other analyses are at a higher state than this one was.
    wf = getToolByName(analysis, 'portal_workflow')
    ar = analysis.aq_parent
    ar_UID = ar.UID()
    can_submit = True
    can_attach = True
    can_verify = True
    can_publish = True

    for a in ar.getAnalyses():
        a_state = a.review_state
        if a_state in \
           ('sample_due', 'sample_received',):
            can_submit = False
        if a_state in \
           ('sample_due', 'sample_received', 'attachment_due',):
            can_attach = False
        if a_state in \
           ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
            can_verify = False
        if a_state in \
           ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified', 'verified',):
            can_publish = False

    # Note: AR adds itself to the skiplist so we have to take it off again
    #       to allow multiple promotions (maybe by more than one deleted analysis).
    if can_submit and wf.getInfoFor(ar, 'review_state') == 'sample_received':
        wf.doActionFor(ar, 'submit')
        analysis.REQUEST["workflow_skiplist"].remove(ar_UID)
    if can_attach and wf.getInfoFor(ar, 'review_state') == 'attachment_due':
        wf.doActionFor(ar, 'attach')
        analysis.REQUEST["workflow_attach_skiplist"].remove(ar_UID)
    if can_verify and wf.getInfoFor(ar, 'review_state') == 'to_be_verified':
        analysis.REQUEST["workflow_skiplist"].append('verify all analyses')
        wf.doActionFor(ar, 'verify')
        analysis.REQUEST["workflow_skiplist"].remove(ar_UID)
    if can_publish and wf.getInfoFor(ar, 'review_state') == 'verified':
        analysis.REQUEST["workflow_skiplist"].append('publish all analyses')
        wf.doActionFor(ar, 'publish')
        analysis.REQUEST["workflow_skiplist"].remove(ar_UID)

    ar_ws_state = wf.getInfoFor(ar, 'worksheetanalysis_review_state')
    if ar_ws_state == 'unassigned':
        if not ar.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
            if ar.getAnalyses(worksheetanalysis_review_state = 'assigned'):
                wf.doActionFor(ar, 'assign')
                analysis.REQUEST["workflow_skiplist"].remove(ar_UID)

    return

def ActionSucceededEventHandler(analysis, event):

    if event.action == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not analysis.REQUEST.has_key('workflow_attach_skiplist'):
            analysis.REQUEST['workflow_attach_skiplist'] = [analysis.UID(), ]
        else:
            if analysis.UID() in analysis.REQUEST['workflow_attach_skiplist']:
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
            if not dependent.UID() in analysis.REQUEST['workflow_attach_skiplist']:
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
        if not ar.UID() in analysis.REQUEST['workflow_attach_skiplist']:
            can_attach = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received', 'attachment_due',):
                    can_attach = False
                    break
            if can_attach:
                wf.doActionFor(ar, 'attach')

        # If assigned to a worksheet and all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            if not ws.UID() in analysis.REQUEST['workflow_attach_skiplist']:
                can_attach = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('sample_due', 'sample_received', 'attachment_due', 'assigned',):
                        # Note: referenceanalyses can still have review_state = "assigned" (as at 21 Sep 2011).
                        can_attach = False
                        break
                if can_attach:
                    wf.doActionFor(ws, 'attach')

        return

    #------------------------------------------------------
    # End of "attach" code, back to your basic nightmare...
    #------------------------------------------------------

    if not analysis.REQUEST.has_key('workflow_skiplist'):
        analysis.REQUEST['workflow_skiplist'] = [analysis.UID(), ]
    else:
        if analysis.UID() in analysis.REQUEST['workflow_skiplist']:
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
        #-------------------------------------------------
        # Submit our dependents
        # Need to check for result and status of dependencies first
        dependents = analysis.getDependents()
        for dependent in dependents:
            if not dependent.UID() in analysis.REQUEST['workflow_skiplist']:
                can_submit = True
                if not dependent.getResult():
                    can_submit = False
                else:
                    interim_fields = False
                    service = dependent.getService()
                    calculation = service.getCalculation()
                    if calculation:
                        interim_fields = calculation.getInterimFields()
                    if interim_fields:
                        can_submit = False
                if can_submit:
                    dependencies = dependent.getDependencies()
                    for dependency in dependencies:
                        if wf.getInfoFor(dependency, 'review_state') in ('sample_due', 'sample_received',):
                            can_submit = False
                if can_submit:
                    wf.doActionFor(dependent, 'submit')

        # If all analyses in this AR have been submitted
        # escalate the action to the parent AR
        if not ar.UID() in analysis.REQUEST['workflow_skiplist']:
            all_submitted = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received',):
                    all_submitted = False
                    break
            if all_submitted:
                wf.doActionFor(ar, 'submit')

        # If assigned to a worksheet and all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            # if the worksheet analyst is not assigned, the worksheet transition
            # be transitioned.
            if ws.getAnalyst() and not ws.UID() in analysis.REQUEST['workflow_skiplist']:
                all_submitted = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('sample_due', 'sample_received', 'assigned',):
                        # Note: referenceanalyses can still have review_state = "assigned" (as at 21 Sep 2011).
                        all_submitted = False
                        break
                if all_submitted:
                    wf.doActionFor(ws, 'submit')

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
        if not "retract all dependencies" in analysis.REQUEST['workflow_skiplist']:
            for dependency in analysis.getDependencies():
                if not dependency.UID() in analysis.REQUEST['workflow_skiplist']:
                    if wf.getInfoFor(dependency, 'review_state') in ('attachment_due', 'to_be_verified',):
                        # (NB: don't retract if it's verified)
                        wf.doActionFor(dependency, 'retract')
        # Retract our dependents
        for dep in analysis.getDependents():
            if not dep.UID() in analysis.REQUEST['workflow_skiplist']:
                if wf.getInfoFor(dep, 'review_state') != 'sample_received':
                    analysis.REQUEST["workflow_skiplist"].append("retract all dependencies")
                    wf.doActionFor(dep, 'retract')
                    analysis.REQUEST["workflow_skiplist"].remove("retract all dependencies")
        # Escalate action to the parent AR
        if not ar.UID() in analysis.REQUEST['workflow_skiplist']:
            if wf.getInfoFor(ar, 'review_state') == 'sample_received':
                analysis.REQUEST["workflow_skiplist"].append(ar.UID())
            else:
                if not "retract all analyses" in analysis.REQUEST['workflow_skiplist']:
                    analysis.REQUEST["workflow_skiplist"].append("retract all analyses")
                wf.doActionFor(ar, 'retract')
        # Escalate action to the Worksheet (if it's on one).
        ws = analysis.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            if not ws.UID() in analysis.REQUEST['workflow_skiplist']:
                if wf.getInfoFor(ws, 'review_state') == 'open':
                    analysis.REQUEST["workflow_skiplist"].append(ws.UID())
                else:
                    if not "retract all analyses" in analysis.REQUEST['workflow_skiplist']:
                        analysis.REQUEST["workflow_skiplist"].append("retract all analyses")
                    wf.doActionFor(ws, 'retract')

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

        # Don't verify our dependencies, they're done (or will be done by AR).
        #---------------------------------------------------------------------
        # Check for dependents, ensure all their dependencies
        # have been verified, and submit/verify them
        for dependent in analysis.getDependents():
            if not dependent.UID() in analysis.REQUEST['workflow_skiplist']:
                if dependent.getResult():
                    review_state = wf.getInfoFor(dependent, 'review_state')
                    interim_fields = False
                    service = dependent.getService()
                    calculation = service.getCalculation()
                    if calculation:
                        interim_fields = calculation.getInterimFields()
                    dependencies = dependent.getDependencies()
                    if interim_fields:
                        if review_state == 'sample_received':
                            can_submit = True
                            for dependency in dependencies:
                                if wf.getInfoFor(dependency, 'review_state') in \
                                    ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified'):
                                    can_submit = False
                                    break
                            if can_submit:
                                wf.doActionFor(dependent, 'submit')
                    else:
                        if review_state == 'to_be_verified':
                            can_verify = True
                            for dependency in dependencies:
                                if wf.getInfoFor(dependency, 'review_state') in \
                                    ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified'):
                                    can_verify = False
                                    break
                            if can_verify:
                                wf.doActionFor(dependent, 'verify')

        # If all analyses in this AR are verified
        # escalate the action to the parent AR
        if not ar.UID() in analysis.REQUEST['workflow_skiplist']:
            all_verified = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified'):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in analysis.REQUEST['workflow_skiplist']:
                    analysis.REQUEST["workflow_skiplist"].append("verify all analyses")
                wf.doActionFor(ar, "verify")

        # If this is on a worksheet and all it's other analyses are verified,
        # then verify the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            if not ws.UID() in analysis.REQUEST['workflow_skiplist']:
                all_verified = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified', 'assigned'):
                        # Note: referenceanalyses can still have review_state = "assigned" (as at 21 Sep 2011).
                        all_verified = False
                        break
                if all_verified:
                    if not "verify all analyses" in analysis.REQUEST['workflow_skiplist']:
                        analysis.REQUEST["workflow_skiplist"].append("verify all analyses")
                    wf.doActionFor(ws, "verify")

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
            maxtime_delta = maxtime.get('hours', 0) * 86400
            maxtime_delta += maxtime.get('hours', 0) * 3600
            maxtime_delta += maxtime.get('minutes', 0) * 60
            earliness = duration - maxtime_delta
        else:
            earliness = 0
            duration = 0
        analysis.setDuration(duration)
        analysis.setEarliness(earliness)
        analysis.reindexObject()

    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.action == "cancel":
        analysis.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        # If it is assigned to a worksheet, unassign it before cancelation.
        if wf.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'assigned':
            wf.doActionFor(analysis, 'unassign')
            analysis.REQUEST["workflow_skiplist"].remove(analysis.UID())

    elif event.action == "assign":
        analysis.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        rc = getToolByName(analysis, 'reference_catalog')
        wsUID = analysis.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # retract the worksheet to 'open'
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state != 'open':
            if not analysis.REQUEST.has_key('workflow_skiplist'):
                analysis.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
            else:
                analysis.REQUEST["workflow_skiplist"].append('retract all analyses')
            wf.doActionFor(ws, 'retract')

        # If all analyses in this AR have been assigned,
        # escalate the action to the parent AR
        if not ar.UID() in analysis.REQUEST['workflow_skiplist']:
            if not ar.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
                wf.doActionFor(ar, 'assign')

    elif event.action == "unassign":
        analysis.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        # Analysis will be removed from the worksheet later by higher level code
        ws = analysis.getBackReferences('WorksheetAnalysis')[0]
        ws_UID = ws.UID()

        # Escalate the action to the parent AR if it is assigned
        # Note: AR adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions/demotions (maybe by more than one analysis).
        ar_UID = ar.UID()
        if wf.getInfoFor(ar, 'worksheetanalysis_review_state') == 'assigned':
            wf.doActionFor(ar, 'unassign')
            analysis.REQUEST["workflow_skiplist"].remove(ar_UID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = True

        for a in ws.getAnalyses():
            ws_empty = False
            a_state = wf.getInfoFor(a, 'review_state')
            if a_state in \
               ('sample_due', 'sample_received',):
                can_submit = False
            if a_state in \
               ('sample_due', 'sample_received', 'attachment_due',):
                can_attach = False
            if a_state in \
               ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one analysis).
            if can_submit and wf.getInfoFor(ws, 'review_state') == 'open':
                wf.doActionFor(ws, 'submit')
                analysis.REQUEST["workflow_skiplist"].remove(ws_UID)
            if can_attach and wf.getInfoFor(ws, 'review_state') == 'attachment_due':
                wf.doActionFor(ws, 'attach')
                analysis.REQUEST["workflow_attach_skiplist"].remove(ws_UID)
            if can_verify and wf.getInfoFor(ws, 'review_state') == 'to_be_verified':
                analysis.REQUEST["workflow_skiplist"].append('verify all analyses')
                wf.doActionFor(ws, 'verify')
                analysis.REQUEST["workflow_skiplist"].remove(ws_UID)
        else:
            if wf.getInfoFor(ws, 'review_state') != 'open':
                wf.doActionFor(ws, 'retract')

    return
