from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
from bika.lims import EditSample
from bika.lims import PMF
from bika.lims.browser.analyses import AnalysesView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone

class SamplePartitionsView(AnalysesView):

    def selected_cats(self, items):
        return self.categories

    def __init__(self, context, request, **kwargs):
        super(SamplePartitionsView, self).__init__(context, request, **kwargs)
        self.columns['request'] = {'title': _("Analysis Request")}
        self.review_states[0]['columns'].insert(0, "request")

    def folderitems(self, full_objects=True):
        self.contentsMethod = self.context.getAnalyses
        wf = getToolByName(self.context, 'portal_workflow')
        items = super(SamplePartitionsView, self).folderitems()

        self.categories = []
        for x in range(len(items)):

            part = items[x]['obj'].getSamplePartition()
            rs = wf.getInfoFor(part, 'review_state')
            state_title = wf.getTitleForStateOnType(rs, part.portal_type)

            container = part.getContainer()
            container = container and " | %s"%container.Title() or ''
            preservation = part.getPreservation()
            preservation = preservation and " | %s"%preservation.Title() or ''

            cat = "%s%s%s | %s" % \
                (part.id, container, preservation, state_title)
            items[x]['category'] = cat
            if not cat in self.categories:
                self.categories.append(cat)

            ar = items[x]['obj'].aq_parent
            items[x]['request'] = ''
            items[x]['after']['request'] = "<a href='%s'>%s</a>" % \
                (ar.absolute_url(), ar.id)

        return items

class SampleViewView(BrowserView):
    """ Sample View/Edit form
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.TimeOrDate = TimeOrDate

    def now(self):
        return DateTime()

    def __call__(self):

        form = self.request.form

        if 'submitted' in self.request.form:

            message = None

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
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                if sampleType == '':
                    message = _('Sample Type is required')
                else:
                    if not bsc(portal_type = 'SampleType', title = sampleType):
                        message = _("${sampletype} is not a valid sample type",
                                    mapping={'sampletype':sampleType})
                if samplePoint != "":
                    if not bsc(portal_type = 'SamplePoint', title = samplePoint):
                        message = _("${samplepoint} is not a valid sample point",
                                    mapping={'sampletype':samplePoint})
                if not message:
                    sample.edit(
                        ClientReference = form['ClientReference'],
                        ClientSampleID = form['ClientSampleID'],
                        SampleType = sampleType,
                        SamplePoint = samplePoint,
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

            ## End of form submit handler

        p = SamplePartitionsView(self.context,
                                 self.request,
                                 sort_on = 'getServiceTitle')
        p.allow_edit = True
        p.review_states[0]['transitions'] = [{'id':'submit'},
                                             {'id':'retract'},
                                             {'id':'verify'}]
        p.show_select_column = True
        self.parts = p.contents_table()

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
            'getSampleID': {'title': _('Sample ID'),
                         'index':'getSampleID'},
            'Client': {'title': _("Client"),
                       'toggle': True,},
            'Requests': {'title': _('Requests'),
                         'sortable': False,
                         'toggle': False},
            'getClientReference': {'title': _('Client Ref'),
                                'index': 'getClientReference',
                                'toggle': False},
            'getClientSampleID': {'title': _('Client SID'),
                               'index': 'getClientSampleID',
                               'toggle': False},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                'index': 'getSampleTypeTitle'},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                'index': 'getSamplePointTitle',
                                'toggle': False},
            'getSamplingDate': {'title': _('Sampling Date'),
                             'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                             'toggle': True},
            'getSampler': {'title': _('Sampler'),
                             'toggle': True},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle': False},
            'state_title': {'title': _('State'),
                            'index':'review_state'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived',
                         'state_title']},
            {'id':'to_be_sampled',
             'title': _('To Be Sampled'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'to_be_preserved',
             'title': _('To Be Preserved'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'sample_due',
             'title': _('Due'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'sample_received',
             'title': _('Received'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'transitions': [{'id':'reinstate'}, ],
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'DateReceived',
                         'getDateSampled',
                         'getSampler',
                         'state_title']},
            ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)

        translate = self.context.translation_service.translate

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['getSampleID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], obj.getSampleID())

            requests = ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
                        for o in obj.getAnalysisRequests()]
            items[x]['replace']['Requests'] = ",".join(requests)

            items[x]['Client'] = obj.aq_parent.Title()
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())

            items[x]['DateReceived'] = TimeOrDate(self.context,
                                                  obj.getDateReceived())

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='Hazardous' src='++resource++bika.lims.images/hazardous.png'>"
            if obj.getSamplingDate() > DateTime():
                after_icons += "<img src='++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    translate(_("Future dated sample"))
            if after_icons:
                items[x]['after']['getSampleID'] = after_icons

        return items

class ajaxSetDateSampled():
    """ DateSampled is set immediately.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            return
        for part in self.context.objectValues("SamplePartition"):
            if not part.getDateSampled():
                part.setDateSampled(value)
        return "ok"

class ajaxSetSampler():
    """ Sampler is set immediately.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(value):
            return
        for part in self.context.objectValues("SamplePartition"):
            if not part.getSampler():
                part.setSampler(value)
        return "ok"
