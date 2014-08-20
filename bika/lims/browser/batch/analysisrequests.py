from operator import itemgetter
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as _ARAV
from bika.lims.browser.analysisrequest import AnalysisRequestsView as _ARV
from bika.lims.permissions import *
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class AnalysisRequestsView(_ARV, _ARAV):
    template = ViewPageTemplateFile(
        "../analysisrequest/templates/analysisrequests.pt")
    ar_add = ViewPageTemplateFile("../analysisrequest/templates/ar_add.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

    def contentsMethod(self, contentFilter):
        #bc = getToolByName(self.context, 'bika_catalog')
        #import pdb;pdb.set_trace()
        #if 'BatchUID' not in contentFilter.keys():
        #    contentFilter['BatchUID'] = self.context.UID()
        #return bc(contentFilter)
        return self.context.getBackReferences("AnalysisRequestBatch")

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            layout = 'columns'
            ar_count = '4'
            self.context_actions[self.context.translate(_('Add new'))] = {
                    'url': '%(context_url)s/portal_factory/AnalysisRequest/Request new analyses/ar_add?layout=%(layout)s&ar_count=%(ar_count)s' % {
                            'context_url': self.context.absolute_url(),
                            'layout': layout,
                            'ar_count': ar_count,
                            }, 
                'icon': '++resource++bika.lims.images/add.png'}

            # This is permitted from the global permission above, AddAnalysisRequest.
            review_states = []
            for review_state in self.review_states:
                custom_actions = review_state.get('custom_actions', [])
                custom_actions.extend([{'id': 'copy_to_new',
                                        'title': _('Copy to new'),
                                        'url': 'workflow_action?action=copy_to_new'},
                                       ])
                review_state['custom_actions'] = custom_actions
                review_states.append(review_state)
            self.review_states = review_states

        return super(AnalysisRequestsView, self).__call__()

    def getMemberDiscountApplies(self):
        client = self.context.getClient()
        return client and client.getMemberDiscountApplies() or False

    def getRestrictedCategories(self):
        client = self.context.getClient()
        return client and client.getRestrictedCategories() or []

    def getDefaultCategories(self):
        client = self.context.getClient()
        return client and client.getDefaultCategories() or []
