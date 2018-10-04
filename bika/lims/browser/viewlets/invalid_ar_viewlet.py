from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from plone.app.layout.viewlets import ViewletBase


class InvalidAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is invalid and display the link to the retest
    """
    template = ViewPageTemplateFile("templates/invalid_ar_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(InvalidAnalysisRequestViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view
