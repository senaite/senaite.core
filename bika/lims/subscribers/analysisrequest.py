from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ActionSucceededEventHandler(ar, event):
    workflow = getToolByName(ar, 'portal_workflow')
    pc = getToolByName(ar, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(ar, 'plone_utils').addPortalMessage

    # set this before transitioning to prevent this handler from reacting
    if hasattr(ar, '_skip_ActionSucceededEvent'):
        del ar._skip_ActionSucceededEvent
        return

    if event.action == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject()
        # receive the AR's sample
        sample = ar.getSample()
        try:
            workflow.doActionFor(sample, event.action)
            sample.reindexObject()
        except WorkflowException, msg:
            pass
        # receive all analyses in this AR.
        analyses = ar.getAnalyses()
        if not analyses:
            addPortalMessage(_("Add one or more Analyses first."))
            transaction.abort()
        for analysis in analyses:
            # ignore 'not requested' analyses
            if analysis.review_state == 'not_requested':
                continue
            try:
                analysis= analysis.getObject()
                workflow.doActionFor(analysis, event.action)
                analysis.reindexObject()
            except WorkflowException, errmsg:
                pass

    if event.action == "assign":
        ar._assigned_to_worksheet = True

    if event.action == "submit":
        # Check all analyses, verify that they are in sample_recieved,
        # and that their Result is anything other than an empty string,
        # and submit them
        analyses = ar.getAnalyses()
        for analysis in analyses:
            if analysis.review_state == 'not_requested':
                continue
            if analysis.review_state != 'sample_received':
                continue
            try:
                analysis = analysis.getObject()
                workflow.doActionFor(analysis, event.action)
                analysis.reindexObject()
            except WorkflowException:
                pass

    if event.action == "verify":
        # verify all analyses in this AR.
        mt = getToolByName(ar, 'portal_membership')
        member = mt.getAuthenticatedMember()
        analyses = ar.getAnalyses()
        for analysis in analyses:
            # ignore 'not requested' analyses
            if analysis.review_state == 'not_requested':
                continue
            analysis = analysis.getObject()
            if 'Manager' not in member.getRoles():
                # fail if we are the user who submitted this analysis
                review_history = workflow.getInfoFor(analysis, 'review_history')
                review_history.reverse()
                for e in review_history:
                    if e.get('action') == 'submit':
                        if e.get('actor') == user.getId():
                            transaction.abort()
                            addPortalMessage(_("Results cannot be verified by the submitting user."))
                            return
                        break
            try:
                    workflow.doActionFor(analysis, event.action)
                    analysis.reindexObject()
            except WorkflowException:
                pass

    if event.action == "retract":
        # retract all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            # ignore 'not requested' analyses
            if analysis.review_state == 'not_requested':
                continue
            analysis = analysis.getObject()
            try:
                workflow.doActionFor(analysis, event.action)
                if analysis._assigned_to_worksheet:
                    workflow.doActionFor(analysis, 'assign')
                analysis.reindexObject()
            except WorkflowException:
                pass
        if ar._assigned_to_worksheet:
            workflow.doActionFor(ar, 'assign')
        ar.reindexObject()

    if event.action == "publish":
        ar.setDatePublished(DateTime())
        ar.reindexObject()
        # publish all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            # ignore 'not requested' analyses
            if analysis.review_state == 'not_requested':
                continue
            analysis = analysis.getObject()
            try:
                workflow.doActionFor(analysis, event.action)
                analysis.reindexObject()
            except WorkflowException:
                pass
