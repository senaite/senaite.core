from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


class RetestAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is a retest. Display the link to the invalid
    """
    template = ViewPageTemplateFile("templates/retest_ar_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(RetestAnalysisRequestViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view
