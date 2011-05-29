from Products.CMFCore.utils import getToolByName
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
from Products.bika import bikaMessageFactory as _

class ClientAnalysisRequestsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisRequest'}
        self.content_add_buttons = {'Analysis Request': "analysisrequest_add"}
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Requests"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 10
        self.columns = {
               'getRequestID': {'title': 'Request ID'},
               'getContact': {'title': 'Contact'},
               'getClientOrderNumber': {'title': 'Client Order'},
               'ClientReference': {'title': 'Client Ref'},
               'ClientSampleID': {'title': 'Client Sample'},
               'SampleType': {'title': 'Sample Type'},
               'SamplePoint': {'title': 'Sample Point'},
               'getDateReceived': {'title': 'Date Received'},
               'getDatePublished': {'title': 'Date Published'},
               'state_title': {'title': 'State'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived',
                                'getDatePublished',
                                'state_title'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    {'title': 'Sample due', 'id':'sample_due',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    {'title': 'Sample received', 'id':'sample_received',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    {'title': 'Assigned to Worksheet', 'id':'assigned',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
                    {'title': 'To be verified', 'id':'to_be_verified',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
                    {'title': 'Verified', 'id':'verified',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
                    {'title': 'Published', 'id':'published',
                     'columns':['getRequestID',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived',
                                'getDatePublished']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            sample = obj.getSample()
            items[x]['SampleType'] = sample.getSampleType().Title()
            items[x]['SamplePoint'] = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            items[x]['ClientReference'] = sample.getClientReference()
            items[x]['ClientSampleID'] = sample.getClientSampleID()
            items[x]['getDateReceived'] = obj.getDateReceived() and self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''
            items[x]['getDatePublished'] = obj.getDatePublished() and self.context.toLocalizedTime(obj.getDatePublished(), long_format = 0) or ''

            items[x]['links'] = {'getRequestID': items[x]['url']}

        return items

class ClientSamplesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Sample'}
        self.content_add_buttons = {}
        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'getSampleID': {'title': 'Sample ID'},
               'Requests': {'title': 'Requests'},
               'getClientReference': {'title':'Client Ref'},
               'getClientSampleID': {'title':'Client SID'},
               'SampleType': {'title': 'Sample Type'},
               'SamplePoint': {'title': 'Sample Point'},
               'getDateReceived': {'title': 'Date Received'},
               'state_title': {'title': 'State'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived',
                                 'state_title']},
                    {'title': 'Due', 'id':'due',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint']},
                    {'title': 'Received', 'id':'received',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived']},
                    {'title': 'Expired', 'id':'expired',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived']},
                    {'title': 'Disposed', 'id':'disposed',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived']},

                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['Requests'] = ",".join([o.Title() for o in obj.getAnalysisRequests()])
            items[x]['SampleType'] = obj.getSampleType().Title()
            items[x]['SamplePoint'] = obj.getSamplePoint().Title()
            items[x]['getDateReceived'] = obj.getDateReceived() and self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''

            items[x]['links'] = {'getSampleID': items[x]['url']}

        return items

class ClientARImportsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARImport'}
        self.content_add_buttons = {'AR Import': "createObject?type_name=ARImport"}
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Request Imports"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'title_or_id': {'title': 'Import'},
               'getDateImported': {'title': 'Date Imported'},
               'getStatus': {'title':'Validity'},
               'getDateApplied': {'title':'Date Submitted'},
               'state_title': {'title': 'State'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id',
                                 'getDateImported',
                                 'getStatus',
                                 'getDateApplied',
                                 'state_title']},
                    {'title': 'Imported', 'id':'imported',
                     'columns': ['title_or_id',
                                 'getDateImported',
                                 'getStatus']},
                    {'title': 'Applied', 'id':'submitted',
                     'columns': ['title_or_id',
                                 'getDateImported',
                                 'getStatus',
                                 'getDateApplied']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

class ClientARProfilesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientARProfilesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARProfile'}
        self.content_add_buttons = {'AR Profile': "createObject?type_name=ARProfile"}
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Request Profiles"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'getProfileTitle': {'title': 'Title'},
               'getProfileKey': {'title': 'Profile Key'},
              }
        self.wflist_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['getProfileTitle',
                                 'getProfileKey']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getProfileTitle': items[x]['url']}

        return items

class ClientAnalysisSpecsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisSpec'}
        self.content_add_buttons = {'Analysis Spec': "createObject?type_name=AnalysisSpec"}
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Specifications"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'getSampleType': {'title': 'Sample  Type'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getSampleType']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getSampleType': items[x]['url']}

        return items

class ClientAttachmentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Attachment'}
        self.content_add_buttons = {'Attachment': "createObject?type_name=Attachment"}
        self.title = "%s: %s" % (self.context.Title(), _("Attachments"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'getTextTitle': {'title': 'Request ID'},
               'AttachmentFile': {'title': 'File'},
               'AttachmentType': {'title': 'Attachment Type'},
               'ContentType': {'title': 'Content Type'},
               'FileSize': {'title': 'Size'},
               'DateLoaded': {'title': 'Date Loaded'},
              }
        self.wflist_states = [
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
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
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

            items[x]['links'] = {'getTextTitle': obj_url,
                                 'AttachmentFile': "%s/at_download/AttachmentFile" % obj_url}
        return items

class ClientOrdersView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Order'}
        self.content_add_buttons = {'Order': "createObject?type_name=Order"}
        self.title = "%s: %s" % (self.context.Title(), _("Orders"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.full_objects = False
        self.columns = {
               'OrderNumber': {'title': 'Order Number'},
               'OrderDate': {'title': 'Order Date'},
               'DateDispatched': {'title':'Date dispatched'},
               'state_title': {'title':'State'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['OrderNumber',
                                 'OrderDate',
                                 'DateDispatched',
                                 'state_title']},
                    {'title': 'Pending', 'id':'pending',
                     'columns': ['OrderNumber',
                                 'OrderDate']},
                    {'title': 'Dispatched', 'id':'dispatched',
                     'columns': ['OrderNumber',
                                 'OrderDate',
                                 'DateDispatched']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = obj.getOrderDate()
            items[x]['DateDispatched'] = obj.getDateDispatched()

            items[x]['links'] = {'OrderNumber': obj.absolute_url()}

        return items

class ClientContactsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Contact'}
        self.content_add_buttons = {'Contact': "createObject?type_name=Contact"}
        self.title = "%s: %s" % (self.context.Title(), _("Contacts"))
        self.description = ""
        self.show_editable_border = True
        self.batch = True
        self.b_size = 100
        self.columns = {
               'getFullname': {'title': 'Full Name'},
               'getEmailAddress': {'title': 'Email Address'},
               'getBusinessPhone': {'title':'Business Phone'},
               'getMobilePhone': {'title':'Mobile Phone'},
               'getFax': {'title': 'Fax'},
              }
        self.wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getFullname',
                                 'getEmailAddress',
                                 'getBusinessPhone',
                                 'getMobilePhone',
                                 'getFax']},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getFullname': items[x]['url'] + "/edit"}

        return items
