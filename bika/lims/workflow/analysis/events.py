from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from bika.lims import logger
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed


def after_submit(obj):
    """
    Method triggered after a 'submit' transition for the current analysis
    is performed. If the current analysis belongs to a Worksheet and all
    the analyses from this worksheet has been submitted, then promotes the
    'submit' transition to the Worksheet.
    The child class AbstractRegularAnalysis overrides this function and
    do manage the logic required for regular analyses and duplicates.
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    ws = obj.getBackReferences("WorksheetAnalysis")
    if ws:
        # If assigned to a worksheet and all analyses within the worksheet have
        # been submitted, then submit the worksheet
        ws = ws[0]
        ans = ws.getAnalyses()
        anssub = [an for an in ans if wasTransitionPerformed(an, 'submit')]
        if len(ans) == len(anssub):
            doActionFor(ws, 'submit')


def after_retract(obj):
    # TODO Workflow Analysis - review this function
    # Rename the analysis to make way for it's successor.
    # Support multiple retractions by renaming to *-0, *-1, etc
    parent = obj.aq_parent
    kw = obj.getKeyword()
    analyses = [x for x in parent.objectValues("Analysis")
                if x.getId().startswith(obj.getId())]

    # LIMS-1290 - Analyst must be able to retract, which creates a new
    # Analysis.  So, _verifyObjectPaste permission check must be cancelled:
    parent._verifyObjectPaste = str
    parent.manage_renameObject(kw, "{0}-{1}".format(kw, len(analyses)))
    delattr(parent, '_verifyObjectPaste')

    # Create new analysis from the retracted obj
    analysis = create_analysis(parent, obj)
    changeWorkflowState(
        analysis, "bika_analysis_workflow", "sample_received")

    # Assign the new analysis to this same worksheet, if any.
    ws = obj.getBackReferences("WorksheetAnalysis")
    if ws:
        ws = ws[0]
        ws.addAnalysis(analysis)
    analysis.reindexObject()

    # retract our dependencies
    dependencies = obj.getDependencies()
    for dependency in dependencies:
        doActionFor(dependency, 'retract')

    # Retract our dependents
    dependents = obj.getDependents()
    for dependent in dependents:
        doActionFor(dependent, 'retract')


@security.public
def after_verify(obj):
    # TODO Workflow Analysis - Review after_verify function
    if skip(self, "verify"):
        return
    username=getToolByName(self,'portal_membership').getAuthenticatedMember().getUserName()
    obj.addVerificator(username)
    workflow = get_tool("portal_workflow")
    state = workflow.getInfoFor(self, 'cancellation_state', 'active')
    if state == "cancelled":
        return False
    # Do all the reflex rules process
    obj._reflex_rule_process('verify')
    # If all analyses in this AR are verified escalate the action to the
    # parent AR
    ar = obj.aq_parent
    if not skip(ar, "verify", peek=True):
        all_verified = True
        for a in ar.getAnalyses():
            if a.review_state in ("to_be_sampled", "to_be_preserved",
                                  "sample_due", "sample_received",
                                  "attachment_due", "to_be_verified"):
                all_verified = False
                break
        if all_verified:
            if "verify all analyses" \
                    not in obj.REQUEST['workflow_skiplist']:
                obj.REQUEST["workflow_skiplist"].append(
                    "verify all analyses")
            workflow.doActionFor(ar, "verify")
    # If this is on a worksheet and all it's other analyses are verified,
    # then verify the worksheet.
    ws = obj.getBackReferences("WorksheetAnalysis")
    if ws:
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, "review_state")
        if ws_state == "to_be_verified" and not skip(ws, "verify",
                                                     peek=True):
            all_verified = True
            for a in ws.getAnalyses():
                state = workflow.getInfoFor(a, "review_state")
                if state in ("to_be_sampled", "to_be_preserved",
                             "sample_due", "sample_received",
                             "attachment_due", "to_be_verified",
                             "assigned"):
                    all_verified = False
                    break
            if all_verified:
                if "verify all analyses" \
                        not in obj.REQUEST['workflow_skiplist']:
                    obj.REQUEST["workflow_skiplist"].append(
                        "verify all analyses")
                workflow.doActionFor(ws, "verify")
    obj.reindexObject()

@security.public
def after_publish(obj):
    if skip(self, "publish"):
        return
    workflow = get_tool("portal_workflow")
    state = workflow.getInfoFor(self, 'cancellation_state', 'active')
    if state == "cancelled":
        return False
    endtime = DateTime()
    obj.setDateAnalysisPublished(endtime)
    starttime = obj.aq_parent.getDateReceived()
    starttime = starttime or obj.created()
    maxtime = obj.getMaxTimeAllowed()
    # set the instance duration value to default values
    # in case of no calendars or max hours
    if maxtime:
        duration = (endtime - starttime) * 24 * 60
        maxtime_delta = int(maxtime.get("hours", 0)) * 86400
        maxtime_delta += int(maxtime.get("hours", 0)) * 3600
        maxtime_delta += int(maxtime.get("minutes", 0)) * 60
        earliness = duration - maxtime_delta
    else:
        earliness = 0
        duration = 0
    obj.setDuration(duration)
    obj.setEarliness(earliness)
    obj.reindexObject()

@security.public
def after_cancel(obj):
    if skip(self, "cancel"):
        return
    workflow = get_tool("portal_workflow")
    # If it is assigned to a worksheet, unassign it.
    state = workflow.getInfoFor(self, 'worksheetanalysis_review_state')
    if state == 'assigned':
        ws = obj.getBackReferences("WorksheetAnalysis")[0]
        skip(self, "cancel", unskip=True)
        ws.removeAnalysis(self)
    obj.reindexObject()

@security.public
def after_reject(obj):
    if skip(self, "reject"):
        return
    workflow = get_tool("portal_workflow")
    # If it is assigned to a worksheet, unassign it.
    state = workflow.getInfoFor(self, 'worksheetanalysis_review_state')
    if state == 'assigned':
        ws = obj.getBackReferences("WorksheetAnalysis")[0]
        ws.removeAnalysis(self)
    obj.reindexObject()

@security.public
def after_attach(obj):
    if skip(self, "attach"):
        return
    workflow = get_tool("portal_workflow")
    # If all analyses in this AR have been attached escalate the action
    # to the parent AR
    ar = obj.aq_parent
    state = workflow.getInfoFor(ar, "review_state")
    if state == "attachment_due" and not skip(ar, "attach", peek=True):
        can_attach = True
        for a in ar.getAnalyses():
            if a.review_state in ("to_be_sampled", "to_be_preserved",
                                  "sample_due", "sample_received",
                                  "attachment_due"):
                can_attach = False
                break
        if can_attach:
            workflow.doActionFor(ar, "attach")
    # If assigned to a worksheet and all analyses on the worksheet have
    # been attached, then attach the worksheet.
    ws = obj.getBackReferences('WorksheetAnalysis')
    if ws:
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, "review_state")
        if ws_state == "attachment_due" \
                and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                state = workflow.getInfoFor(a, "review_state")
                if state in ("to_be_sampled", "to_be_preserved",
                             "sample_due", "sample_received",
                             "attachment_due", "assigned"):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, "attach")
    obj.reindexObject()

@security.public
def after_assign(obj):
    if skip(self, "assign"):
        return
    workflow = get_tool("portal_workflow")
    uc = get_tool("uid_catalog")
    ws = uc(UID=obj.REQUEST["context_uid"])[0].getObject()
    # retract the worksheet to 'open'
    ws_state = workflow.getInfoFor(ws, "review_state")
    if ws_state != "open":
        if "workflow_skiplist" not in obj.REQUEST:
            obj.REQUEST["workflow_skiplist"] = ["retract all analyses", ]
        else:
            obj.REQUEST["workflow_skiplist"].append("retract all analyses")
        allowed_transitions = \
            [t["id"] for t in workflow.getTransitionsFor(ws)]
        if "retract" in allowed_transitions:
            workflow.doActionFor(ws, "retract")
    # If all analyses in this AR have been assigned,
    # escalate the action to the parent AR
    if not skip(self, "assign", peek=True):
        if not obj.getAnalyses(
                worksheetanalysis_review_state="unassigned"):
            try:
                allowed_transitions = \
                    [t["id"] for t in workflow.getTransitionsFor(self)]
                if "assign" in allowed_transitions:
                    workflow.doActionFor(self, "assign")
            except WorkflowException:
                logger.error(
                    "assign action failed for analysis %s" % obj.getId())
    obj.reindexObject()

@security.public
def after_unassign(obj):
    if skip(self, "unassign"):
        return
    workflow = get_tool("portal_workflow")
    uc = get_tool("uid_catalog")
    ws = uc(UID=obj.REQUEST["context_uid"])[0].getObject()
    # Escalate the action to the parent AR if it is assigned
    # Note: AR adds itself to the skiplist so we have to take it off again
    #       to allow multiple promotions/demotions (maybe by more than
    #       one instance).
    state = workflow.getInfoFor(self, "worksheetanalysis_review_state")
    if state == "assigned":
        workflow.doActionFor(self, "unassign")
        skip(self, "unassign", unskip=True)
    # If it has been duplicated on the worksheet, delete the duplicates.
    obj.remove_duplicates(ws)
    # May need to promote the Worksheet's review_state
    # if all other analyses are at a higher state than this one was.
    # (or maybe retract it if there are no analyses left)
    can_submit = True
    can_attach = True
    can_verify = True
    ws_empty = True
    for a in ws.getAnalyses():
        ws_empty = False
        a_state = workflow.getInfoFor(a, "review_state")
        if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                       "sample_due", "sample_received"):
            can_submit = False
        else:
            if not ws.getAnalyst():
                can_submit = False
        if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                       "sample_due", "sample_received", "attachment_due"):
            can_attach = False
        if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                       "sample_due", "sample_received", "attachment_due",
                       "to_be_verified"):
            can_verify = False
    if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it
        # off again to allow multiple promotions (maybe by more than
        # one instance).
        state = workflow.getInfoFor(ws, "review_state")
        if can_submit and state == "open":
            workflow.doActionFor(ws, "submit")
            skip(ws, 'unassign', unskip=True)
        state = workflow.getInfoFor(ws, "review_state")
        if can_attach and state == "attachment_due":
            workflow.doActionFor(ws, "attach")
            skip(ws, 'unassign', unskip=True)
        state = workflow.getInfoFor(ws, "review_state")
        if can_verify and state == "to_be_verified":
            obj.REQUEST['workflow_skiplist'].append("verify all analyses")
            workflow.doActionFor(ws, "verify")
            skip(ws, 'unassign', unskip=True)
    else:
        if workflow.getInfoFor(ws, "review_state") != "open":
            workflow.doActionFor(ws, "retract")
            skip(ws, "retract", unskip=True)
    obj.reindexObject()
