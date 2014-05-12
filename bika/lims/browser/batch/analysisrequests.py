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
        bc = getToolByName(self.context, 'bika_catalog')
        if 'BatchUID' not in contentFilter.keys():
            contentFilter['BatchUID'] = self.context.UID()
        return bc(contentFilter)

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # Client contact required (if client is associated)
            client = self.context.getClient()
            if hasattr(client, 'getContacts') and client.getContacts():
                self.context_actions[self.context.translate(_('Add new'))] = {
                    'url': self.context.absolute_url() + \
                        "/portal_factory/"
                        "AnalysisRequest/Request new analyses/ar_add?col_count=1",
                    'icon': '++resource++bika.lims.images/add.png'}
            # else:
                # addPortalMessage = self.context.plone_utils.addPortalMessage
                # msg = _("Client contact required before request may be submitted")
                # addPortalMessage(self.context.translate(msg))
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
