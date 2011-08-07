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
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            try:
                if event.action in \
                   [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
                    analysis.reindexObject()
            except WorkflowException, errmsg:
                transaction.abort()
                raise WorkflowException, \
                      _("One or more transitions failed: ") + str(errmsg)

    if event.action == "assign":
        ar._assigned_to_worksheet = True

    if event.action == "submit":
        # submit all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            try:
                if event.action in \
                   [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
                    analysis.reindexObject()
            except WorkflowException, errmsg:
                transaction.abort()
                raise WorkflowException, \
                      _("One or more transitions failed: ") + str(errmsg)

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
                if event.action in \
                   [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
                    analysis.reindexObject()
            except WorkflowException, errmsg:
                transaction.abort()
                raise WorkflowException, \
                      _("One or more transitions failed: ") + str(errmsg)

    if event.action == "retract":
        # retract all analyses in this AR.
        analyses = ar.getAnalyses()
        for analysis in analyses:
            review_state = workflow.getInfoFor(analysis, 'review_state')
            # ignore 'not requested' analyses
            if review_state == 'not_requested':
                continue
            try:
                if event.action in \
                   [t['id'] for t in workflow.getTransitionsFor(analysis)]:
                    workflow.doActionFor(analysis, event.action)
                    if analysis._assigned_to_worksheet:
                        workflow.doActionFor(analysis, 'assign')
                    analysis.reindexObject()
            except WorkflowException, errmsg:
                transaction.abort()
                raise WorkflowException, \
                      _("One or more transitions failed: ") + str(errmsg)
        if ar._assigned_to_worksheet:
            workflow.doActionFor(ar, 'assign')
        ar.reindexObject()







