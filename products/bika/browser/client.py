from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_list import BikaListView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

#class RedirectToActions(BrowserView):
#    def __init__(self, context, request):
#        self.context = context
#        self.request = request
#        request.SESSION.set('client_setup_state', 'actions')
#    def __call__(self):
#        self.request.RESPONSE.redirect(self.context.absolute_url())
#
#class RedirectToSetup(BrowserView):
#    def __init__(self, context, request):
#        self.context = context
#        self.request = request
#        request.SESSION.set('client_setup_state', 'setup')
#    def __call__(self):
#        self.request.RESPONSE.redirect(self.context.absolute_url() + "/edit")

class ClientAnalysisRequestsView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['AnalysisRequest']
    contentFilter = {'portal_type': 'AnalysisRequest'}
    title = "Analysis Requests"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    columns = {
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
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived',
                                'getDatePublished',
                                'wf_state']},
                    {'title': 'Sample due', 'id':'sample_due',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint']},
                    {'title': 'Sample received', 'id':'sample_received',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
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
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
                    {'title': 'Verified', 'id':'verified',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived']},
                    {'title': 'Published', 'id':'published',
                     'columns':['getRequestID',
                                'getContact',
                                'getClientOrderNumber',
                                'ClientReference',
                                'ClientSampleID',
                                'SampleType',
                                'SamplePoint',
                                'getDateReceived',
                                'getDatePublished']},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            sample = items[x]['obj'].Sample
            items[x]['SampleType'] = sample.getSampleType().Title()
            items[x]['SamplePoint'] = sample.getSamplePoint().Title()
            items[x]['ClientReference'] = sample.getClientReference()
            items[x]['ClientSampleID'] = sample.getClientSampleID()

            items[x]['links'] = {'getRequestID': items[x]['url']}

        return items

class ClientSamplesView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['Sample']
    contentFilter = {'portal_type': 'Sample'}
    title = "Samples"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'getSampleID': {'title': 'Sample ID'},
               'Requests': {'title': 'Requests'},
               'getClientReference': {'title':'Client Ref'},
               'getClientSampleID': {'title':'Client SID'},
               'SampleType': {'title': 'Sample Type'},
               'SamplePoint': {'title': 'Sample Point'},
               'getDateReceived': {'title': 'Date Received'},
               'state_title': {'title': 'State'},
              }
    wflist_states = [
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
                                 'SamplePoint',
                                 'getDateReceived',
                                 'state_title']},
                    {'title': 'Received', 'id':'received',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived',
                                 'state_title']},
                    {'title': 'Expired', 'id':'expired',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived',
                                 'state_title']},
                    {'title': 'Disposed', 'id':'disposed',
                     'columns': ['getSampleID',
                                 'Requests',
                                 'getClientReference',
                                 'getClientSampleID',
                                 'SampleType',
                                 'SamplePoint',
                                 'getDateReceived',
                                 'state_title']},

                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['Requests'] = items[x]['obj'].getAnalysisRequests()
            items[x]['SampleType'] = items[x]['obj'].getSampleType().Title()
            items[x]['SamplePoint'] = items[x]['obj'].getSamplePoint().Title()

            items[x]['links'] = {'getSampleID': items[x]['url']}

        return items

class ClientARImportsView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['ARImport']
    contentFilter = {'portal_type': 'ARImport'}
    title = "Analysis Request Imports"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'title_or_id': {'title': 'Import'},
               'getDateImported': {'title': 'Date Imported'},
               'getStatus': {'title':'Validity'},
               'getDateApplied': {'title':'Date Submitted'},
               'state_title': {'title': 'State'},
              }
    wflist_states = [
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
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

class ClientARProfilesView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['ARProfile']
    contentFilter = {'portal_type': 'ARProfile'}
    title = "Analysis Request Profiles"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'getProfileTitle': {'title': 'Title'},
               'getProfileKey': {'title': 'Profile Key'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getProfileTitle',
                                 'getProfileKey']},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getProfileTitle': items[x]['url']}

        return items

class ClientAnalysisSpecsView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['AnalysisSpec']
    contentFilter = {'portal_type': 'AnalysisSpec'}
    title = "Analysis Specs"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'getSampleType': {'title': 'Sample  Type'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getSampleType']},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getSampleType': items[x]['url']}

        return items

class ClientAttachmentsView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['Attachment']
    contentFilter = {'portal_type': 'AnalysisSpec'}
    title = "Attachments"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'getTextTitle': {'title': 'Request ID'},
               'AttachmentFile': {'title': 'File'},
               'AttachmentType': {'title': 'Attachment Type'},
               'ContentType': {'title': 'Content Type'},
               'FileSize': {'title': 'Size'},
               'DateLoaded': {'title': 'Date Loaded'},
              }
    wflist_states = [
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
        items = BikaListView.folderitems(self)
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

class ClientOrdersView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['Orders', ]
    contentFilter = {'portal_type': 'Orders'}
    title = "Orders"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'OrderNumber': {'title': 'Order Number'},
               'OrderDate': {'title': 'Order Date'},
               'DateDispatched': {'title':'Date dispatched'},
               'state_title': {'title':'State'},
              }
    wflist_states = [
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
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = obj.getOrderDate()
            items[x]['DateDispatched'] = obj.getDateDispatched()

            items[x]['links'] = {'OrderNumber': obj.absolute_url()}

        return items

class ClientContactsView(BikaListView):
    implements(IFolderContentsView)
    allowed_content_types = ['Contact']
    contentFilter = {'portal_type': 'Contact'}
    title = "Contacts"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'getFullname': {'title': 'Full Name'},
               'getEmailAddress': {'title': 'Email Address'},
               'getBusinessPhone': {'title':'Business Phone'},
               'getMobilePhone': {'title':'Mobile Phone'},
               'getFax': {'title': 'Fax'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getFullName',
                                 'getEmailAddress',
                                 'getBusinessPhone',
                                 'getMobilePhone',
                                 'getFax']},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getFullName': items[x]['url']}

        return items

