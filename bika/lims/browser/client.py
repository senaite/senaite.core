from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.publish import Publish
from bika.lims.browser.bika_listing import WorkflowAction
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

        originating_url = self.request.get_header("referer",
                                                  self.context.absolute_url())

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
                self.context.plone_utils.addPortalMessage("No action provided", 'error')
                self.request.response.redirect(originating_url)

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
            self.request.response.redirect(originating_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class ClientAnalysisRequestsView(BikaListingView):

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter = {'portal_type':'AnalysisRequest'}
        self.review_state = 'all'
        if context.objectValues('Contact'):
            self.content_add_actions = {_('Analysis Request'):
                                        "analysisrequest_add"}
            self.description = ""
        else:
            self.content_add_actions = {}
            self.description = "Client contact required before request may be submitted"
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.title = "%s: %s" % (self.context.Title(),
                                 _("Analysis Requests"))

        self.columns = {
            'getRequestID': {'title': _('Request ID')},
            'ClientOrderNumber': {'title': _('Client Order')},
            'ClientReference': {'title': _('Client Ref')},
            'ClientSampleID': {'title': _('Client Sample')},
            'SampleTypeTitle': {'title': _('Sample Type')},
            'SamplePointTitle': {'title': _('Sample Point')},
            'DateReceived': {'title': _('Date Received')},
            'DatePublished': {'title': _('Date Published')},
            'state_title': {'title': _('State'), },
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': ['receive', 'submit', 'retract', 'prepublish', 'publish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived',
                        'DatePublished',
                        'state_title']},
            {'id':'sample_due',
             'title': _('Sample due'),
             'contentFilter': {'review_state': 'sample_due'},
             'transitions': ['receive', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle']},
            {'id':'sample_received',
             'title': _('Sample received'),
             'contentFilter': {'review_state': 'sample_received'},
             'transitions': ['cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived']},
            {'id':'assigned',
             'title': _('Assigned to Worksheet'),
             'contentFilter': {'worksheetanalysis_review_state': 'assigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published')},
             'transitions': ['submit', 'retract', 'publish', 'prepublish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state': 'to_be_verified'},
             'transitions': ['verify', 'prepublish', 'retract', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified'},
             'transitions': ['publish', 'republish', 'cancel', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived']},
            {'id':'published',
             'title': _('Published'),
             'contentFilter': {'review_state': 'published'},
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived',
                        'DatePublished']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': ('sample_due', 'sample_received',
                                                'to_be_verified', 'attachment_due',
                                                'verified', 'published')},
             'transitions': ['republish', 'reinstate'],
             'columns':['getRequestID',
                        'ClientOrderNumber',
                        'ClientReference',
                        'ClientSampleID',
                        'SampleTypeTitle',
                        'SamplePointTitle',
                        'DateReceived',
                        'DatePublished',
                        'state_title']},
            ]

    @property
    def folderitems(self):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getRequestID'])

            items[x]['ClientOrderNumber'] = obj.getClientOrderNumber()
            items[x]['ClientReference'] = obj.getClientReference()
            items[x]['ClientSampleID'] = obj.getClientSampleID()
            items[x]['SampleTypeTitle'] = obj.getSampleTypeTitle()
            items[x]['SamplePointTitle'] = obj.getSamplePointTitle()
            items[x]['DateReceived'] = obj.getDateReceived() and \
                self.context.toLocalizedTime(obj.getDateReceived(), \
                                             long_format = 0) or ''
            items[x]['DatePublished'] = obj.getDatePublished() and \
                self.context.toLocalizedTime(obj.getDatePublished(), \
                                             long_format = 0) or ''

            if workflow.getInfoFor(obj, 'worksheetanalysis_review_state') == 'assigned':
                items[x]['after']['state_title'] = \
                     "<img src='++resource++bika.lims.images/worksheet.png' title='All analyses assigned'/>"

            sample = obj.getSample()
            after_icons = "<a href='%s'><img src='++resource++bika.lims.images/sample.png' title='Sample: %s'></a>" % \
                        (sample.absolute_url(),sample.Title())
            if sample.getSampleType().getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous_small.png' title='Hazardous'>"
            if after_icons:
                items[x]['after']['getRequestID'] = after_icons

        return items

class ClientSamplesView(BikaListingView):

    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Sample',
                              'cancellation_state':'active'}
        self.content_add_actions = {}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.pagesize = 50

        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""

        self.columns = {
            'SampleID': {'title': _('Sample ID')},
            'Requests': {'title': _('Requests')},
            'ClientReference': {'title': _('Client Ref')},
            'ClientSampleID': {'title': _('Client SID')},
            'SampleTypeTitle': {'title': _('Sample Type')},
            'SamplePointTitle': {'title': _('Sample Point')},
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
                         'DateReceived',
                         'state_title']},
            {'id':'due',
             'title': _('Due'),
             'columns': ['SampleID',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
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
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'columns': ['SampleID',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'columns': ['SampleID',
                         'Requests',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
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
                         'DateReceived',
                         'state_title']},
            ]

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['SampleID'] = obj.getSampleID()
            items[x]['replace']['SampleID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['SampleID'])
            items[x]['replace']['Requests'] = ",".join(
                ["<a href='%s'>%s</a>"%(o.absolute_url(), o.Title())
                 for o in obj.getAnalysisRequests()])
            items[x]['ClientReference'] = obj.getClientReference()
            items[x]['ClientSampleID'] = obj.getClientSampleID()
            items[x]['SampleTypeTitle'] = obj.getSampleTypeTitle()
            items[x]['SamplePointTitle'] = obj.getSamplePointTitle()

            items[x]['DateReceived'] = obj.getDateReceived() and \
                 self.context.toLocalizedTime(obj.getDateReceived(), \
                                              long_format = 0) or ''

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous_small.png' title='Hazardous'>"
            if after_icons:
                items[x]['after']['SampleID'] = after_icons


        return items

class ClientARImportsView(BikaListingView):

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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientARProfilesView(BikaListingView):
    def __init__(self, context, request):
        super(ClientARProfilesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARProfile'}
        self.content_add_actions = {_('AR Profile'):
                                    "createObject?type_name=ARProfile"}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = True
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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientAnalysisSpecsView(BikaListingView):

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

    @property
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

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Attachment'}
        self.content_add_actions = {_('Attachment'): "createObject?type_name=Attachment"}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = True
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

    @property
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

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'SupplyOrder'}
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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = obj.getOrderDate()
            items[x]['DateDispatched'] = obj.getDateDispatched()

            items[x]['replace']['OrderNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['OrderNumber'])

        return items

class ClientContactsView(BikaListingView):

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Contact'}
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

    @property
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
