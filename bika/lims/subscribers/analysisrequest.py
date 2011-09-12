from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ActionSucceededEventHandler(ar, event):

    if not hasattr(ar, '_skip_ActionSucceededEventHandler'):
        logger.info("Succeeded: %s on %s" % (event.action,ar))

    wf = getToolByName(ar, 'portal_workflow')
    pc = getToolByName(ar, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(ar, 'plone_utils').addPortalMessage

    if hasattr(ar, '_skip_ActionSucceededEventHandler'):
        return

    elif event.action == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject(idxs=["review_state",])

        # receive the AR's sample
        sample = ar.getSample()
        try:
            sample._skip_ActionSucceededEventHandler = True
            wf.doActionFor(sample, 'receive')
        except WorkflowException, msg:
            pass
        finally:
            del sample._skip_ActionSucceededEventHandler

        # receive all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'sample_due',
                                  full_objects = True)
        for analysis in analyses:
            wf.doActionFor(analysis, 'receive')

    elif event.action == "assign":
        ar._assigned_to_worksheet = True

    elif event.action == "submit":
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
                wf.doActionFor(analysis, event.action)
                analysis.reindexObject(idxs=["review_state",])
            except WorkflowException:
                pass

    elif event.action == "retract":
        # retract all analyses in this AR.
        analyses = ar.getAnalyses(review_state=('to_be_verified', 'verified', 'assigned'),
                                  full_objects = True)
        for analysis in analyses:
            try:
                wf.doActionFor(analysis, 'retract')
                if analysis._assigned_to_worksheet:
                    wf.doActionFor(analysis, 'assign')
            except WorkflowException:
                pass
        if ar._assigned_to_worksheet:
            wf.doActionFor(ar, 'assign')
        ar.reindexObject(idxs=["review_state",])

    elif event.action == "verify":
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
                review_history = wf.getInfoFor(analysis, 'review_history')
                review_history.reverse()
                for e in review_history:
                    if e.get('action') == 'submit':
                        if e.get('actor') == user.getId():
                            transaction.abort()
                            addPortalMessage(_("Results cannot be verified by the submitting user."))
                            return
                        break
            try:
                    wf.doActionFor(analysis, event.action)
                    analysis.reindexObject(idxs=["review_state",])
            except WorkflowException:
                pass

    elif event.action == "publish":
        ar.setDatePublished(DateTime())
        ar.reindexObject(idxs=["review_state",])
        # publish all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            # ignore 'not requested' analyses
            if analysis.review_state == 'not_requested':
                continue
            analysis = analysis.getObject()
            try:
                wf.doActionFor(analysis, event.action)
                analysis.reindexObject(idxs=["review_state",])
            except WorkflowException:
                pass
