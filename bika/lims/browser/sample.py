from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import TimeOrDate
from bika.lims import EditSample
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class SampleViewView(BrowserView):
    """ Sample View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample_view.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        return self.template()


class SampleEditView(SampleViewView):
    """ Sample Edit form
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample_edit.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        workflow = getToolByName(self.context, 'portal_workflow')

        if workflow.getInfoFor(self.context, 'cancellation_state') == "cancelled":
            self.request.response.redirect(self.context.absolute_url())
        elif not(getSecurityManager().checkPermission(EditSample, self.context)):
            self.request.response.redirect(self.context.absolute_url())
        else:
            can_edit_sample = True
            ars = self.context.getAnalysisRequests()
            for ar in ars:
                for a in ar.getAnalyses():
                    if workflow.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                        can_edit_sample = False
                        break
                if not can_edit_sample:
                    break
            if not can_edit_sample:
                self.request.response.redirect(self.context.absolute_url())
            else:
                return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def fmtDateSampled(self):
        return TimeOrDate(self.context,
                          self.request.form.has_key("DateSampled") and \
                          self.request.form["DateSampled"] or \
                          self.context.getDateSampled())

class ajaxSampleSubmit():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)

        can_edit = True
        workflow = getToolByName(self.context, 'portal_workflow')

        if workflow.getInfoFor(self.context, 'cancellation_state') == "cancelled":
            can_edit = False
        elif not(getSecurityManager().checkPermission(EditSample, self.context)):
            can_edit = False
        else:
            ars = self.context.getAnalysisRequests()
            for ar in ars:
                for a in ar.getAnalyses():
                    if workflow.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                        can_edit = False
                        break
                if not can_edit:
                    break

        if can_edit:
            sample = self.context
            sampleType = form['SampleType']
            samplePoint = form['SamplePoint']
            composite = form['Composite']
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
                DateSampled = form['DateSampled'],
                Composite = composite
            )
            sample.reindexObject()
            ars = sample.getAnalysisRequests()
            for ar in ars:
                ar.reindexObject()
            message = _("Changes Saved.")
        else:
            message = _("Changes not allowed.")

        self.context.plone_utils.addPortalMessage(message, 'info')
        return json.dumps({'success':message})

class SamplesView(ClientSamplesView):
    """ The main portal Analysis Requests action tab
    """

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""
        self.contentFilter = {'portal_type':'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path':{"query": ["/"], "level" : 0 }}
        self.view_url = self.view_url + "/samples"
        self.columns['Client'] = {'title': _('Client')}
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].insert(review_state['columns'].index('SampleID') + 1, 'Client')

        request.set('disable_border', 1)

    def folderitems(self):
        workflow = getToolByName(self.context, "portal_workflow")
        items = ClientSamplesView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                 (obj.aq_parent.absolute_url(), obj.aq_parent.Title())

        return items
