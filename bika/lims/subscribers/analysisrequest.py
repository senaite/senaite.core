from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ActionSucceededEventHandler(ar, event):
    workflow = getToolByName(ar, 'portal_workflow')
    pc = getToolByName(ar, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(ar, 'plone_utils').addPortalMessage

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
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            try:
                if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
            except:
                transaction.abort()
                raise WorkflowException, _("One or more analyses transitions failed.")
            analysis.reindexObject()

    if event.action == "submit":
        # submit all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            try:
                if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
            except:
                transaction.abort()
                raise WorkflowException, _("One or more analyses transitions failed.")
            analysis.reindexObject()

    if event.action == "verify":
        # verify all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            # fail if we are the same user who submitted this analysis
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
                if event.action in [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
            except:
                transaction.abort()
                raise WorkflowException, _("One or more analyses transitions failed.")
                return
            analysis.reindexObject()
