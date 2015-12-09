from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import t
from Products.CMFCore.utils import getToolByName


class ClientAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        # The contentfilter's path is context sensitive, because this
        # view is used for Client Batch context also:
        self.contentFilter['path'] = {
            "query": "/".join(context.getPhysicalPath()),
            "level": 0}
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
        self.review_states = review_states

    def __call__(self):
        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        translate = self.context.translate
        # client contact required
        active_contacts = [c for c in self.context.objectValues('Contact') if
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if isActive(self.context):
            if self.context.portal_type == "Client" and not active_contacts:
                msg = _(
                    "Client contact required before request may be submitted")
                addPortalMessage(msg)
            else:
                if mtool.checkPermission(AddAnalysisRequest, self.context):
                    self.context_actions[t(_('Add'))] = {
                        'url': self.context.absolute_url() + \
                               "/portal_factory/AnalysisRequest" + \
                               "/Request new analyses/ar_add",
                        'icon': '++resource++bika.lims.images/add.png'}

        return super(ClientAnalysisRequestsView, self).__call__()


class ClientBatchAnalysisRequestsView(ClientAnalysisRequestsView):
    pass
