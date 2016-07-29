from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class AnalysisRequestRetractView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_retract_mail.pt")

    def __init__(self, context, request, publish=False):
        super(AnalysisRequestRetractView, self).__init__(context, request)

    def __call__(self):
        return self.template()
