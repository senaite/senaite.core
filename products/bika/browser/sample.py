from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from decimal import Decimal
import json

class SampleViewView(BrowserView):
    """ Sample View form
    """
    template = ViewPageTemplateFile("templates/sample_view.pt")

    def __call__(self):
        return self.template()


class SampleEditView(BrowserView):
    """ Sample Edit form
    """

    template = ViewPageTemplateFile("templates/sample_edit.pt")

    def __call__(self):
        if self.request.form.has_key("submitted"):
            return sample_edit_submit(self.context, self.request)
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def fmtDateSampled(self):
        date_sampled = self.request.form.has_key("DateSampled") and self.request.form["DateSampled"] or self.context.getDateSampled().strftime("%Y-%m-%d")
        return date_sampled

def sample_edit_submit(context, request):
    context.plone_utils.addPortalMessage("that might have worked", 'info')
    return json.dumps({'success':"xxx"})


