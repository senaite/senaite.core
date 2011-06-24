from bika.lims.browser.client import ClientSamplesView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.CMFCore.utils import getToolByName
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
        sampleType = form['SampleType']
        samplePoint = form['SamplePoint']
        errors = {}
        pc = getToolByName(context, 'portal_catalog')
        if not pc(portal_type = 'SampleType', Title = sampleType):
            errors['SampleType'] = sampleType + ' is not a valid sample type'
        if samplePoint != "":
            if not pc(portal_type = 'SamplePoint', Title = samplePoint):
                errors['SamplePoint'] = samplePoint + ' is not a valid sample point'
        if errors:
            return json.dumps({'errors':errors})

        sample.edit(
            ClientReference = form['ClientReference'],
            ClientSampleID = form['ClientSampleID'],
            SampleType = sampleType,
            SamplePoint = samplePoint,
            DateSampled = form['DateSampled']
        )
        sample.reindexObject()
        ars = sample.getAnalysisRequests()
        for ar in ars:
            ar.reindexObject()
        message = "Changes Saved."
    else:
        message = "Changes Cancelled."
    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})

class SamplesView(ClientSamplesView):
    contentFilter = {'portal_type':'Sample', 'path':{"query": ["/"], "level" : 0 }}
    title = "Samples"
    description = ""

