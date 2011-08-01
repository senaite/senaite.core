from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser.client import ClientSamplesView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
import json
import plone

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
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def fmtDateSampled(self):
        date_sampled = self.request.form.has_key("DateSampled") and \
                     self.request.form["DateSampled"] or \
                     self.context.getDateSampled().strftime("%Y-%m-%d")
        return date_sampled

class AJAXSampleSubmit():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)

        if form.has_key("save_button"):
            sample = self.context
            sampleType = form['SampleType']
            samplePoint = form['SamplePoint']
            errors = {}
            pc = getToolByName(self.context, 'portal_catalog')
            if sampleType == '':
                errors['SampleType'] = 'Sample Type is required'
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
        self.context.plone_utils.addPortalMessage(message, 'info')
        return json.dumps({'success':message})

class SamplesView(ClientSamplesView):
    """ The main portal Samples action tab
    """
    show_editable_border = False
    contentFilter = {'portal_type':'Sample', 'path':{"query": ["/"], "level" : 0 }}
    title = "Samples"
    description = ""


    from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

def ActionSucceededEventHandler(obj, event):
    wf = getToolByName(obj, 'portal_workflow')
    pc = getToolByName(obj, 'portal_catalog')
    rc = getToolByName(obj, 'reference_catalog')

    if event.action == "receive":
        obj.setDateReceived(DateTime())
        for ar in obj.getAnalysisRequests():
            review_state = wf.getInfoFor(ar, 'review_state', '')
            if review_state != 'sample_due':
                continue
            wf.doActionFor(ar, event.action)
            ar.reindexObject()
        obj.reindexObject()

