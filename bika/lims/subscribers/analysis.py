from AccessControl import getSecurityManager
from Products.Archetypes.config import REFERENCE_CATALOG
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
import transaction

def ObjectInitializedEventHandler(instance, event):

    # This handler fires for DuplicateAnalysis because
    # DuplicateAnalysis also provides IAnalysis.
    # DuplicateAnalysis doesn't have analysis_workflow.
    if instance.portal_type == "DuplicateAnalysis":
        return

    # 'receive' instance if AR is received.
    # Adding a new instance to an AR retracts the AR to 'sample_received'
    # AR may have to be unassigned too

    ar = instance.aq_parent
    ar_UID = ar.UID()
    wf = getToolByName(instance, 'portal_workflow')
    ar_state = wf.getInfoFor(ar, 'review_state')
    ar_ws_state = wf.getInfoFor(ar, 'worksheetanalysis_review_state')

    if ar_state not in ('sample_registered', 'sampled',
                        'to_be_sampled', 'to_be_preserved',
                        'sample_due'):
        try:
            wf.doActionFor(instance, 'receive')
        except WorkflowException:
            pass

    # Note: AR adds itself to the skiplist so we have to take it off again
    #       to allow possible promotions if other analyses are deleted.
    if ar_state not in ('sample_registered', 'sampled',
                        'to_be_sampled', 'to_be_preserved',
                        'sample_due', 'sample_received'):
        if not instance.REQUEST.has_key('workflow_skiplist'):
            instance.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
        else:
            instance.REQUEST["workflow_skiplist"].append('retract all analyses')
        doActionFor(ar, 'retract')
        skip(ar, 'retract', unskip=True)

    if ar_ws_state == 'assigned':
        wf.doActionFor(ar, 'unassign')
        skip(ar, 'unassign', unskip=True)

    return

def ObjectRemovedEventHandler(instance, event):

    # This handler fires for DuplicateAnalysis because
    # DuplicateAnalysis also provides IAnalysis.
    # DuplicateAnalysis doesn't have analysis_workflow.
    if instance.portal_type == "DuplicateAnalysis":
        return

    # May need to promote the AR's review_state
    #  if all other analyses are at a higher state than this one was.
    wf = getToolByName(instance, 'portal_workflow')
    ar = instance.aq_parent
    ar_UID = ar.UID()
    can_submit = True
    can_attach = True
    can_verify = True
    can_publish = True

    for a in ar.getAnalyses():
        a_state = a.review_state
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',):
            can_submit = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received', 'attachment_due',):
            can_attach = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',
            'attachment_due', 'to_be_verified',):
            can_verify = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',
            'attachment_due', 'to_be_verified', 'verified',):
            can_publish = False

    # Note: AR adds itself to the skiplist so we have to take it off again
    #       to allow multiple promotions (maybe by more than one deleted instance).
    if can_submit and wf.getInfoFor(ar, 'review_state') == 'sample_received':
        wf.doActionFor(ar, 'submit')
        skip(ar, 'submit', unskip=True)
    if can_attach and wf.getInfoFor(ar, 'review_state') == 'attachment_due':
        wf.doActionFor(ar, 'attach')
        skip(ar, 'attach', unskip=True)
    if can_verify and wf.getInfoFor(ar, 'review_state') == 'to_be_verified':
        instance.REQUEST["workflow_skiplist"].append('verify all analyses')
        wf.doActionFor(ar, 'verify')
        skip(ar, 'verify', unskip=True)
    if can_publish and wf.getInfoFor(ar, 'review_state') == 'verified':
        instance.REQUEST["workflow_skiplist"].append('publish all analyses')
        wf.doActionFor(ar, 'publish')
        skip(ar, 'publish', unskip=True)

    ar_ws_state = wf.getInfoFor(ar, 'worksheetanalysis_review_state')
    if ar_ws_state == 'unassigned':
        if not ar.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
            if ar.getAnalyses(worksheetanalysis_review_state = 'assigned'):
                wf.doActionFor(ar, 'assign')
                skip(ar, 'assign', unskip=True)

    return

def AfterTransitionEventHandler(instance, event):

    # DuplicateAnalysis doesn't have analysis_workflow.
    if instance.portal_type == "DuplicateAnalysis":
        return

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    action_id = event.transition.id

    if skip(instance, action_id):
        return

    service = instance.getService()
    wf = getToolByName(instance, 'portal_workflow')
    ar = instance.aq_parent
    part = instance.getSamplePartition()

    if action_id == "attach":
        instance.reindexObject(idxs = ["review_state", ])
        # Dependencies are already at least 'to_be_verified', ignore them.
        #----------------------------------------------------------------
        # Check our dependents:
        # If    it is 'attachment_due'
        # And   it's attachments are OK
        # And   all it's dependencies are at least 'to_be_verified'
        # Then: 'attach' it.:
        dependents = instance.getDependents()
        for dependent in dependents:
            if not skip(dependent, 'attach', peek=True):
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
                        if wf.getInfoFor(dependency, 'review_state') in \
                           ('to_be_sampled', 'to_be_preserved', 'sample_due',
                            'sample_received', 'attachment_due',):
                            can_attach = False
                            break
                if can_attach:
                    doActionFor(dependent, 'attach')

        # If all analyses in this AR have been attached
        # escalate the action to the parent AR
        ar_state = wf.getInfoFor(ar, 'review_state')
        if ar_state == 'attachment_due' and not skip(ar, 'attach', peek=True):
            can_attach = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('to_be_sampled', 'to_be_preserved',
                    'sample_due', 'sample_received', 'attachment_due',):
                    can_attach = False
                    break
            if can_attach:
                wf.doActionFor(ar, 'attach')

        # If assigned to a worksheet and all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            ws_state = wf.getInfoFor(ws, 'review_state')
            if ws_state == 'attachment_due' and not skip(ws, action_id, peek=True):
                can_attach = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('to_be_sampled', 'to_be_preserved', 'sample_due',
                        'sample_received', 'attachment_due', 'assigned',):
                        # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                        can_attach = False
                        break
                if can_attach:
                    wf.doActionFor(ws, 'attach')

        return

    #------------------------------------------------------
    # End of "attach" code, back to your basic nightmare...
    #------------------------------------------------------


    elif action_id == "receive":
        instance.updateDueDate()
        instance.reindexObject()

    elif action_id == "submit":
        instance.reindexObject(idxs = ["review_state", ])
        # Dependencies are submitted already, ignore them.
        #-------------------------------------------------
        # Submit our dependents
        # Need to check for result and status of dependencies first
        dependents = instance.getDependents()
        for dependent in dependents:
            if not skip(dependent, action_id, peek=True):
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
                        if wf.getInfoFor(dependency, 'review_state') in \
                           ('to_be_sampled', 'to_be_preserved',
                            'sample_due', 'sample_received',):
                            can_submit = False
                if can_submit:
                    wf.doActionFor(dependent, 'submit')

        # If all analyses in this AR have been submitted
        # escalate the action to the parent AR
        if not skip(ar, action_id, peek=True):
            all_submitted = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('to_be_sampled', 'to_be_preserved',
                    'sample_due', 'sample_received',):
                    all_submitted = False
                    break
            if all_submitted:
                wf.doActionFor(ar, 'submit')

        # If assigned to a worksheet and all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
            if ws.getAnalyst() and not skip(ws, action_id, peek=True):
                all_submitted = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('to_be_sampled', 'to_be_preserved',
                        'sample_due', 'sample_received', 'assigned',):
                        # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                        all_submitted = False
                        break
                if all_submitted:
                    wf.doActionFor(ws, 'submit')

        # If no problem with attachments, do 'attach' action for this instance.
        can_attach = True
        if not instance.getAttachment():
            service = instance.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            dependencies = instance.getDependencies()
            for dependency in dependencies:
                if wf.getInfoFor(dependency, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due',):
                    can_attach = False
        if can_attach:
            wf.doActionFor(instance, 'attach')

    elif action_id == "retract":
        instance.reindexObject(idxs = ["review_state", ])
        # retract our dependencies
        if not "retract all dependencies" in instance.REQUEST['workflow_skiplist']:
            for dependency in instance.getDependencies():
                if not skip(dependency, action_id, peek=True):
                    if wf.getInfoFor(dependency, 'review_state') in ('attachment_due', 'to_be_verified',):
                        # (NB: don't retract if it's verified)
                        wf.doActionFor(dependency, 'retract')
        # Retract our dependents
        for dep in instance.getDependents():
            if not skip(dep, action_id, peek=True):
                if wf.getInfoFor(dep, 'review_state') != 'sample_received':
                    instance.REQUEST["workflow_skiplist"].append("retract all dependencies")
                    wf.doActionFor(dep, 'retract')
                    instance.REQUEST["workflow_skiplist"].remove("retract all dependencies")
        # Escalate action to the parent AR
        if not skip(ar, action_id, peek=True):
            if wf.getInfoFor(ar, 'review_state') == 'sample_received':
                skip(ar, action_id)
            else:
                if not "retract all analyses" in instance.REQUEST['workflow_skiplist']:
                    instance.REQUEST["workflow_skiplist"].append("retract all analyses")
                wf.doActionFor(ar, 'retract')
        # Escalate action to the Worksheet (if it's on one).
        ws = instance.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            if not skip(ws, action_id, peek=True):
                if wf.getInfoFor(ws, 'review_state') == 'open':
                    skip(ws, 'retract')
                else:
                    if not "retract all analyses" in instance.REQUEST['workflow_skiplist']:
                        instance.REQUEST["workflow_skiplist"].append("retract all analyses")
                    wf.doActionFor(ws, 'retract')

    elif action_id == "verify":
        instance.reindexObject(idxs = ["review_state", ])

        # Don't verify our dependencies, they're done (or will be done by AR).
        #---------------------------------------------------------------------
        # Check for dependents, ensure all their dependencies
        # have been verified, and submit/verify them
        for dependent in instance.getDependents():
            if not skip(dependent, action_id, peek=True):
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
                                    ('to_be_sampled', 'to_be_preserved',
                                     'sample_due', 'sample_received',
                                     'attachment_due', 'to_be_verified'):
                                    can_submit = False
                                    break
                            if can_submit:
                                wf.doActionFor(dependent, 'submit')
                    else:
                        if review_state == 'to_be_verified':
                            can_verify = True
                            for dependency in dependencies:
                                if wf.getInfoFor(dependency, 'review_state') in \
                                    ('to_be_sampled', 'to_be_preserved',
                                     'sample_due', 'sample_received',
                                     'attachment_due', 'to_be_verified'):
                                    can_verify = False
                                    break
                            if can_verify:
                                wf.doActionFor(dependent, 'verify')

        # If all analyses in this AR are verified
        # escalate the action to the parent AR
        if not skip(ar, action_id, peek=True):
            all_verified = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due', 'to_be_verified'):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in instance.REQUEST['workflow_skiplist']:
                    instance.REQUEST["workflow_skiplist"].append("verify all analyses")
                wf.doActionFor(ar, "verify")

        # If this is on a worksheet and all it's other analyses are verified,
        # then verify the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            ws_state = wf.getInfoFor(ws, 'review_state')
            if ws_state == 'to_be_verified' and not skip(ws, action_id, peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    if wf.getInfoFor(a, 'review_state') in \
                       ('to_be_sampled', 'to_be_preserved', 'sample_due',
                        'sample_received', 'attachment_due', 'to_be_verified',
                        'assigned'):
                        # Note: referenceanalyses and duplicateanalyses can
                        # still have review_state = "assigned".
                        all_verified = False
                        break
                if all_verified:
                    if not "verify all analyses" in instance.REQUEST['workflow_skiplist']:
                        instance.REQUEST["workflow_skiplist"].append("verify all analyses")
                    wf.doActionFor(ws, "verify")

    elif action_id == "publish":
        endtime = DateTime()
        instance.setDateAnalysisPublished(endtime)
        starttime = instance.aq_parent.getDateReceived()
        starttime = starttime or instance.created()
        service = instance.getService()
        maxtime = service.getMaxTimeAllowed()
        # set the instance duration value to default values
        # in case of no calendars or max hours
        if maxtime:
            duration = (endtime - starttime) * 24 * 60
            maxtime_delta = int(maxtime.get('hours', 0)) * 86400
            maxtime_delta += int(maxtime.get('hours', 0)) * 3600
            maxtime_delta += int(maxtime.get('minutes', 0)) * 60
            earliness = duration - maxtime_delta
        else:
            earliness = 0
            duration = 0
        instance.setDuration(duration)
        instance.setEarliness(earliness)
        instance.reindexObject()

    #---------------------
    # Secondary workflows:
    #---------------------

    elif action_id == "cancel":
        instance.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        # If it is assigned to a worksheet, unassign it.
        if wf.getInfoFor(instance, 'worksheetanalysis_review_state') == 'assigned':
            ws = instance.getBackReferences("WorksheetAnalysis")[0]
            skip(instance, action_id, unskip=True)
            ws.removeAnalysis(instance)

    elif action_id == "assign":
        instance.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        rc = getToolByName(instance, REFERENCE_CATALOG)
        wsUID = instance.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # retract the worksheet to 'open'
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state != 'open':
            if not instance.REQUEST.has_key('workflow_skiplist'):
                instance.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
            else:
                instance.REQUEST["workflow_skiplist"].append('retract all analyses')
            wf.doActionFor(ws, 'retract')

        # If all analyses in this AR have been assigned,
        # escalate the action to the parent AR
        if not skip(ar, action_id, peek=True):
            if not ar.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
                wf.doActionFor(ar, 'assign')

    elif action_id == "unassign":
        instance.reindexObject(idxs = ["worksheetanalysis_review_state", ])
        rc = getToolByName(instance, REFERENCE_CATALOG)
        wsUID = instance.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # Escalate the action to the parent AR if it is assigned
        # Note: AR adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions/demotions (maybe by more than one instance).
        if wf.getInfoFor(ar, 'worksheetanalysis_review_state') == 'assigned':
            wf.doActionFor(ar, 'unassign')
            skip(ar, action_id, unskip=True)

        # If it has been duplicated on the worksheet, delete the duplicates.
        dups = instance.getBackReferences("DuplicateAnalysisAnalysis")
        for dup in dups:
            ws.removeAnalysis(dup)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = True

        for a in ws.getAnalyses():
            ws_empty = False
            a_state = wf.getInfoFor(a, 'review_state')
            if a_state in \
               ('to_be_sampled', 'to_be_preserved', 'assigned',
                'sample_due', 'sample_received',):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
               ('to_be_sampled', 'to_be_preserved', 'assigned',
                'sample_due', 'sample_received', 'attachment_due',):
                can_attach = False
            if a_state in \
               ('to_be_sampled', 'to_be_preserved', 'assigned', 'sample_due',
                'sample_received', 'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one instance).
            if can_submit and wf.getInfoFor(ws, 'review_state') == 'open':
                wf.doActionFor(ws, 'submit')
                skip(ws, action_id, unskip=True)
            if can_attach and wf.getInfoFor(ws, 'review_state') == 'attachment_due':
                wf.doActionFor(ws, 'attach')
                skip(ws, action_id, unskip=True)
            if can_verify and wf.getInfoFor(ws, 'review_state') == 'to_be_verified':
                instance.REQUEST["workflow_skiplist"].append('verify all analyses')
                wf.doActionFor(ws, 'verify')
                skip(ws, action_id, unskip=True)
        else:
            if wf.getInfoFor(ws, 'review_state') != 'open':
                wf.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)

    return
