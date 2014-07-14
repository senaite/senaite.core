from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import *
from bika.lims.browser.analysisrequest import AnalysisRequestManageResultsView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from plone.app.layout.globals.interfaces import IViewView
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

import plone

class AnalysisRequestResultsNotRequestedView(AnalysisRequestManageResultsView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_analyses_not_requested.pt")

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            childid = childar and childar.getRequestID() or None
            message = _('This Analysis Request has been withdrawn and is shown '
                        'for trace-ability purposes only. Retest: ${retest_child_id}.',
                        mapping={"retest_child_id":childid if childid else ''})
            self.context.plone_utils.addPortalMessage(message, 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _(
                'This Analysis Request has been generated automatically due to '
                'the retraction of the Analysis Request ${retracted_request_id}.',
                mapping={"retracted_request_id": par.getRequestID()})
            self.context.plone_utils.addPortalMessage(message, 'info')

        can_do = getSecurityManager().checkPermission(ResultsNotRequested, ar)
        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(can_do):
            self.request.response.redirect(ar.absolute_url())
        else:
            return self.template()
