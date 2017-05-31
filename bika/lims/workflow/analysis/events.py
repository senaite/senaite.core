from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from bika.lims import logger
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed

from plone.api.portal import get_tool


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


def after_verify(obj):
    """
    Method triggered after a 'verify' transition for the analysis passed in
    is performed. Promotes the transition to the Analysis Request and to
    Worksheet (if the analysis is assigned to any)
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    # Do all the reflex rules process
    obj._reflex_rule_process('verify')

    # Escalate to Analysis Request. Note that the guard for verify transition
    # from Analysis Request will check if the AR can be transitioned, so there
    # is no need to check here if all analyses within the AR have been
    # transitioned already.
    ar = obj.getRequest()
    doActionFor(ar, 'verify')

    # Ecalate to Worksheet. Note that the guard for verify transition from
    # Worksheet will check if the Worksheet can be transitioned, so there is no
    # need to check here if all analyses within the WS have been transitioned
    # already
    ws = obj.getBackReferences("WorksheetAnalysis")
    doActionFor(ws, 'verify')


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
