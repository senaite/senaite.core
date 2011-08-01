from AccessControl import getSecurityManager
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

def ActionSucceededEventHandler(obj, event):
    wf = getToolByName(obj, 'portal_workflow')
    pc = getToolByName(obj, 'portal_catalog')
    user = getSecurityManager().getUser()
    addPortalMessage = getToolByName(obj, 'plone_utils').addPortalMessage

    if event.action == "receive":
        """ set the max hours allowed """
        service = obj.getService()
        maxhours = service.getMaxHoursAllowed()
        if not maxhours:
            maxhours = 0
        obj.setMaxHoursAllowed(maxhours)
        """ set the due date """
        starttime = obj.aq_parent.getDateReceived()
        """ default to old calc in case no calendars  """
        """ still need a due time for selection to ws """
        duetime = starttime + maxhours / 24.0
##        if maxhours:
##            maxminutes = maxhours * 60
##            try:
##                bct = getToolByName(self, BIKA_CALENDAR_TOOL)
##            except:
##                bct = None
##            if bct:
##                duetime = bct.getDurationAdded(starttime, maxminutes)
        obj.setDueDate(duetime)
        obj.reindexObject()

    if event.action == "submit":
        # if we are submitting a calculated result, then also
        # submit dependent services.
        service = obj.getService()
        calculation = service.getCalculation()
        if calculation:
            for dep in calculation.getDependentServices():
                if 'submit' in [t['id'] for t in wf.getTransitionsFor(dep)]:
                    wf.doActionFor(dep, 'submit')
        # Escalate submission to the AR
        if 'submit' in [t['id'] for t in wf.getTransitionsFor(obj.aq_parent)]:
            wf.doActionFor(obj.aq_parent, 'submit')

    if event.action == "verify":
        # fail if we are the same user who submitted this analysis
        review_history = wf.getInfoFor(obj, 'review_history')
        review_history.reverse()
        for event in review_history:
            if event.get('action') == 'submit':
                if event.get('actor') == user.getId():
                    transaction.abort()
                break
        # if we are verifying a calculated result, then also
        # verify dependent services.
        service = obj.getService()
        calculation = service.getCalculation()
        if calculation:
            for dep in calculation.getDependentServices():
                if 'verify' in [t['id'] for t in wf.getTransitionsFor(dep)]:
                    wf.doActionFor(dep, 'verify')
        # check if required analysis attachment is present
        if not obj.getAttachment():
            if obj.bika_settings.getAnalysisAttachmentsPermitted():
                if service.getAttachmentOption() == 'r':
                    addPortalMessage(
                        _("Required analysis attachment is missing for ") + obj.Title(), 'info')
                    transaction.abort()
        # Escalate verification to the AR
        if 'verify' in [t['id'] for t in wf.getTransitionsFor(obj.aq_parent)]:
            wf.doActionFor(obj.aq_parent, 'verify')
