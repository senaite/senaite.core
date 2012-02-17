from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
from bika.lims import EditSample
from bika.lims import PMF, logger
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

    def now(self):
        return DateTime()

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

    def now(self):
        return DateTime()

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
            composite = form.get('Composite', False)
            errors = {}
            bsc = getToolByName(self.context, 'bika_setup_catalog')
            if sampleType == '':
                errors['SampleType'] = 'Sample Type is required'
            else:
                if not bsc(portal_type = 'SampleType', Title = sampleType):
                    errors['SampleType'] = sampleType + ' is not a valid sample type'
            if samplePoint != "":
                if not bsc(portal_type = 'SamplePoint', Title = samplePoint):
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
            message = PMF("Changes saved.")
        else:
            message = _("Changes not allowed")

        self.context.plone_utils.addPortalMessage(message, 'info')
        return json.dumps({'success':message})

class SamplesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path': {'query': "/",
                                       'level': 0 }
                              }
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        if self.view_url.find("/samples") > -1:
            self.request.set('disable_border', 1)
        else:
            self.view_url = self.view_url + "/samples"

        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.title = _("Samples")
        self.description = ""

        self.columns = {
            'SampleID': {'title': _('Sample ID'),
                         'index':'getSampleID'},
            'Client': {'title': _("Client"),
                       'toggle': True,},
            'Requests': {'title': _('Requests'),
                         'sortable': False,
                         'toggle': False},
            'ClientReference': {'title': _('Client Ref'),
                                'index': 'getClientReference',
                                'toggle': False},
            'ClientSampleID': {'title': _('Client SID'),
                               'index': 'getClientSampleID',
                               'toggle': False},
            'SampleTypeTitle': {'title': _('Sample Type'),
                                'index': 'getSampleTypeTitle'},
            'SamplePointTitle': {'title': _('Sample Point'),
                                'index': 'getSamplePointTitle',
                                'toggle': False},
            'DateSampled': {'title': _('Date Sampled'),
                            'index':'getDateSampled'},
            'future_DateSampled': {'title': _('Sampling Date'),
                                   'index':'getDateSampled'},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle': False},
            'state_title': {'title': _('State'),
                            'index':'review_state'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateSampled',
                         'DateReceived',
                         'state_title']},
            {'id':'due',
             'title': _('Due'),
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'future_DateSampled',
                         'SampleTypeTitle',
                         'SamplePointTitle']},
            {'id':'received',
             'title': _('Received'),
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateSampled',
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateSampled',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateSampled',
                         'DateReceived']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'transitions': [{'id':'reinstate'}, ],
             'columns': ['SampleID',
                         'Client',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateSampled',
                         'DateReceived',
                         'state_title']},
            ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)

        translate = self.context.translation_service.translate

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['SampleID'] = obj.getSampleID()
            items[x]['replace']['SampleID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['SampleID'])
            items[x]['replace']['Requests'] = ",".join(
                ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
                 for o in obj.getAnalysisRequests()])
            items[x]['ClientReference'] = obj.getClientReference()
            items[x]['ClientSampleID'] = obj.getClientSampleID()
            items[x]['SampleTypeTitle'] = obj.getSampleTypeTitle()
            items[x]['SamplePointTitle'] = obj.getSamplePointTitle()
            items[x]['Client'] = obj.aq_parent.Title()
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                     (obj.aq_parent.absolute_url(), obj.aq_parent.Title())

            datesampled = obj.getDateSampled()
            items[x]['DateSampled'] = TimeOrDate(self.context, datesampled, long_format = 0)
            items[x]['future_DateSampled'] = datesampled.Date() > DateTime() and \
                TimeOrDate(self.context, datesampled) or ''

            items[x]['DateReceived'] = TimeOrDate(self.context, obj.getDateReceived())

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='Hazardous' src='++resource++bika.lims.images/hazardous.png'>"
            if datesampled > DateTime():
                after_icons += "<img src='++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    translate(_("Future dated sample"))
            if after_icons:
                items[x]['after']['SampleID'] = after_icons

        return items
