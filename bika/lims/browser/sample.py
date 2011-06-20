from bika.lims.browser.client import ClientSamplesView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from plone.app.content.browser.interfaces import IFolderContentsView
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

    form = request.form
    sample = context

    if form.has_key("save_button"):
        sample.edit(
            ClientReference = form['ClientReference'],
            ClientSampleID = form['ClientSampleID'],
            SampleType = form['SampleType'],
            SamplePoint = form['SamplePoint'],
            DateSampled = form['DateSampled']
        )
        sample.reindexObject()
        message = "Changes Saved."
    else:
        message = "Changes Cancelled."
    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})

class SamplesView(ClientSamplesView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type':'Sample', 'path':{"query": ["/"], "level" : 0 }}
    title = "Samples"
    description = ""
