from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.publish import Publish
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.config import ManageResults
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import logger
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
import plone

class ClientWorkflowAction(WorkflowAction):
    """ Workflow actions taken in AnalysisRequest context
        This function is called to do the worflow actions
        that apply to objects transitioned directly
        from Client views
    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')

        # use came_from to decide which UI action was clicked.
        # "workflow_action" is the action name specified in the
        # portal_workflow transition url.
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            # workflow_action_button is the action name specified in
            # the bika_listing_view table buttons.
            came_from = "workflow_action_button"
            action = form.get(came_from, '')
            # XXX some browsers agree better than others about our JS ideas.
            if type(action) == type([]): action = action[0]
            if not action:
                logger.info("No workflow action provided")
                self.destination_url = self.request.get_header("referer",
                                       self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return

        if action in ('prepublish', 'publish', 'prepublish'):
            # We pass a list of AR objects to Publish.
            # it returns a list of AR IDs which were actually published.
            ARs_to_publish = []
            transitioned = []
            if 'paths' in form:
                for path in form['paths']:
                    item_id = path.split("/")[-1]
                    item_path = path.replace("/" + item_id, '')
                    ar = pc(id = item_id,
                              path = {'query':item_path,
                                      'depth':1})[0].getObject()
                    # can't publish inactive items
                    if not(
                        'bika_inactive_workflow' in workflow.getChainFor(ar) and \
                        workflow.getInfoFor(ar, 'inactive_state', '') == 'inactive'):
                        ARs_to_publish.append(ar)

                transitioned = Publish(self.context,
                                       self.request,
                                       action,
                                       ARs_to_publish)()

            if len(transitioned) > 1:
                message = _('message_items_published',
                    default = '${items} were published.',
                    mapping = {'items': ', '.join(transitioned)})
            elif len(transitioned) == 1:
                message = _('message_item_published',
                    default = '${items} was published.',
                    mapping = {'items': ', '.join(transitioned)})
            else:
                message = _('No ARs were published.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class ClientAnalysisRequestsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter = {'portal_type':'AnalysisRequest',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
        self.review_state = 'all'
        self.content_add_actions = {_('Analysis Request'):
                                    "analysisrequest_add"}
        self.description = ""
        wf = getToolByName(self.context, 'portal_workflow')
        active_contacts = [c for c in context.objectValues('Contact') if \
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if context.portal_type == "Client" and not active_contacts:
            self.content_add_actions = {}
            self.context.plone_utils.addPortalMessage(
                _("Client contact required before request may be submitted"))
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.title = "%s: %s" % (self.context.Title(),
                                 _("Analysis Requests"))

        self.columns = {
            'getRequestID': {'title': _('Request ID')},
            'getClientOrderNumber': {'title': _('Client Order')},
            'getClientReference': {'title': _('Client Ref')},
            'getClientSampleID': {'title': _('Client Sample')},
            'getSampleTypeTitle': {'title': _('Sample Type')},
            'getSamplePointTitle': {'title': _('Sample Point')},
            'DateSampled': {'title': _('Date Sampled')},
            'future_DateSampled': {'title': _('Sampling Date')},
            'getDateReceived': {'title': _('Date Received')},
            'getDatePublished': {'title': _('Date Published')},
            'state_title': {'title': _('State'), },
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': ['receive', 'submit', 'retract', 'verify', 'prepublish', 'publish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived',
                        'getDatePublished',
                        'state_title']},
            {'id':'sample_due',
             'title': _('Sample due'),
             'contentFilter': {'review_state': 'sample_due',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['receive', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'future_DateSampled',
                        'getSampleTypeTitle',
                        'getSamplePointTitle']},
            {'id':'sample_received',
             'title': _('Sample received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived']},
            {'id':'assigned',
             'title': _('Assigned to Worksheet'),
             'contentFilter': {'worksheetanalysis_review_state': 'assigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['submit', 'retract', 'publish', 'prepublish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived',
                        'state_title']},
            {'id':'unassigned',
             'title': _('Not Assigned'),
             'contentFilter': {'worksheetanalysis_review_state': 'unassigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['submit', 'retract', 'publish', 'prepublish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state': 'to_be_verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['verify', 'prepublish', 'retract', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['publish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived']},
            {'id':'published',
             'title': _('Published'),
             'contentFilter': {'review_state': 'published',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived',
                        'getDatePublished']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': ('sample_due', 'sample_received',
                                                'to_be_verified', 'attachment_due',
                                                'verified', 'published'),
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions': ['republish', 'reinstate'],
             'columns':['getRequestID',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'DateSampled',
                        'getDateReceived',
                        'getDatePublished',
                        'state_title']},
            ]

    def folderitems(self):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            if getSecurityManager().checkPermission(ManageResults, obj):
                url = obj.absolute_url() + "/manage_results"
            else:
                url = obj.absolute_url()
            items[x]['getRequestID'] = obj.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])

            datesampled = obj.getSample().getDateSampled()
            items[x]['DateSampled'] = TimeOrDate(self.context, datesampled, long_format=0)
            items[x]['future_DateSampled'] = datesampled.Date() > DateTime() and \
                TimeOrDate(self.context, datesampled) or ''

            items[x]['getDateReceived'] = \
                TimeOrDate(self.context, obj.getDateReceived())

            items[x]['getDatePublished'] = \
                TimeOrDate(self.context, obj.getDatePublished())

            if workflow.getInfoFor(obj, 'worksheetanalysis_review_state') == 'assigned':
                items[x]['after']['state_title'] = \
                     "<img src='++resource++bika.lims.images/worksheet.png' title='All analyses assigned'/>"

            sample = obj.getSample()
            after_icons = "<a href='%s'><img src='++resource++bika.lims.images/sample.png' title='Sample: %s'></a>" % \
                        (sample.absolute_url(), sample.Title())
            if sample.getSampleType().getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous_small.png' title='Hazardous'>"
            if after_icons:
                items[x]['after']['getRequestID'] = after_icons

        return items

class ClientSamplesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
        self.content_add_actions = {}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""

        self.columns = {
            'SampleID': {'title': _('Sample ID')},
            'Requests': {'title': _('Requests')},
            'ClientReference': {'title': _('Client Ref')},
            'ClientSampleID': {'title': _('Client SID')},
            'SampleTypeTitle': {'title': _('Sample Type')},
            'SamplePointTitle': {'title': _('Sample Point')},
            'DateSampled': {'title': _('Date Sampled')},
            'future_DateSampled': {'title': _('Sampling Date')},
            'DateReceived': {'title': _('Date Received')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['SampleID',
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
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'future_DateSampled',
                         'SampleTypeTitle',
                         'SamplePointTitle']},
            {'id':'received',
             'title': _('Received'),
             'columns': ['SampleID',
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
             'transitions': ['reinstate'],
             'columns': ['SampleID',
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

            datesampled = obj.getDateSampled()
            items[x]['DateSampled'] = TimeOrDate(self.context, datesampled, long_format=0)
            items[x]['future_DateSampled'] = datesampled.Date() > DateTime() and \
                TimeOrDate(self.context, datesampled) or ''

            items[x]['DateReceived'] = TimeOrDate(self.context, obj.getDateReceived())

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='Hazardous' src='++resource++bika.lims.images/hazardous_small.png'>"
            if after_icons:
                items[x]['after']['SampleID'] = after_icons

        return items

class ClientARImportsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARImport'}
        self.content_add_actions = {_('AR Import'): "createObject?type_name=ARImport"}
        self.show_editable_border = True
        self.self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.title = "%s: %s" % (self.context.Title(), \
                                 _("Analysis Request Imports"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Import')},
            'getDateImported': {'title': _('Date Imported')},
            'getStatus': {'title': _('Validity')},
            'getDateApplied': {'title': _('Date Submitted')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied',
                         'state_title']},
            {'title': _('Imported'), 'id':'imported',
             'columns': ['title',
                         'getDateImported',
                         'getStatus']},
            {'title': _('Applied'), 'id':'submitted',
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientARProfilesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientARProfilesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARProfile'}
        self.content_add_actions = {_('AR Profile'):
                                    "createObject?type_name=ARProfile"}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.title = "%s: %s" % (self.context.Title(),
                                 _("Analysis Request Profiles"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title')},
            'getProfileKey': {'title': _('Profile Key')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['title', 'getProfileKey']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientAnalysisSpecsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisSpec'}
        self.content_add_actions = {_('Analysis Spec'): \
                               "createObject?type_name=AnalysisSpec"}
        self.show_editable_border = True
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.title = "%s: %s" % (self.context.Title(), \
                                 _("Analysis Specifications"))
        self.description = ""

        self.columns = {
            'getSampleType': {'title': _('Sample  Type')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['getSampleType'],
             },
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']

            items[x]['getSampleType'] = obj.getSampleType() and \
                 obj.getSampleType().Title()

            items[x]['replace']['getSampleType'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getSampleType'])

        return items



class ClientAttachmentsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Attachment',
                              'sort_order': 'reverse'}
        self.content_add_actions = {_('Attachment'): "createObject?type_name=Attachment"}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.title = "%s: %s" % (self.context.Title(), _("Attachments"))
        self.description = ""

        self.columns = {
            'getTextTitle': {'title': _('Request ID')},
            'AttachmentFile': {'title': _('File')},
            'AttachmentType': {'title': _('Attachment Type')},
            'ContentType': {'title': _('Content Type')},
            'FileSize': {'title': _('Size')},
            'DateLoaded': {'title': _('Date Loaded')},
        }
        self.review_states = [
            {'title': 'All', 'id':'all',
             'columns': ['getTextTitle',
                         'AttachmentFile',
                         'AttachmentType',
                         'ContentType',
                         'FileSize',
                         'DateLoaded']},
        ]

    def lookupMime(self, name):
        mimetool = getToolByName(self, 'mimetypes_registry')
        mimetypes = mimetool.lookup(name)
        if len(mimetypes):
            return mimetypes[0].name()
        else:
            return name

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            obj_url = obj.absolute_url()
            file = obj.getAttachmentFile()
            icon = file.getBestIcon()

            items[x]['AttachmentFile'] = file.filename()
            items[x]['AttachmentType'] = obj.getAttachmentType().Title()
            items[x]['AttachmentType'] = obj.getAttachmentType().Title()
            items[x]['ContentType'] = self.lookupMime(file.getContentType())
            items[x]['FileSize'] = '%sKb' % (file.get_size() / 1024)
            items[x]['DateLoaded'] = obj.getDateLoaded()

            items[x]['replace']['getTextTitle'] = "<a href='%s'>%s</a>" % \
                 (obj_url, items[x]['getTextTitle'])

            items[x]['replace']['AttachmentFile'] = \
                 "<a href='%s/at_download/AttachmentFile'>%s</a>" % \
                 (obj_url, items[x]['AttachmentFile'])
        return items

class ClientOrdersView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'SupplyOrder',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
        self.content_add_actions = {_('Order'): "createObject?type_name=SupplyOrder"}
        self.show_editable_border = True
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.title = "%s: %s" % (self.context.Title(), _("Orders"))
        self.description = ""

        self.columns = {
            'OrderNumber': {'title': _('Order Number')},
            'OrderDate': {'title': _('Order Date')},
            'DateDispatched': {'title': _('Date dispatched')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['OrderNumber',
                         'OrderDate',
                         'DateDispatched',
                         'state_title']},
            {'title': _('Pending'), 'id':'pending',
             'columns': ['OrderNumber',
                         'OrderDate']},
            {'title': _('Dispatched'), 'id':'dispatched',
             'columns': ['OrderNumber',
                         'OrderDate',
                         'DateDispatched']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = TimeOrDate(self.context, obj.getOrderDate())
            items[x]['DateDispatched'] = TimeOrDate(self.context, obj.getDateDispatched())

            items[x]['replace']['OrderNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['OrderNumber'])

        return items

class ClientContactsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Contact',
                              'sort_on':'sortable_title'}
        self.content_add_actions = {_('Contact'):
                                    "createObject?type_name=Contact"}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.pagesize = 50

        self.title = "%s: %s" % (self.context.Title(), _("Contacts"))
        self.description = ""

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }
        self.review_states = [
            {'title': 'All', 'id':'all',
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']
            items[x]['getFullname'] = obj.getFullname()
            items[x]['getEmailAddress'] = obj.getEmailAddress()
            items[x]['getBusinessPhone'] = obj.getBusinessPhone()
            items[x]['getMobilePhone'] = obj.getMobilePhone()

            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

            if items[x]['getEmailAddress']:
                items[x]['replace']['getEmailAddress'] = "<a href='mailto:%s'>%s</a>" % \
                     (items[x]['getEmailAddress'], items[x]['getEmailAddress'])

        return items
