from Products.CMFCore.utils import getToolByName
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

class ClientAnalysisRequestsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisRequest'}
    content_add_buttons = {'Analysis Request': "analysisrequest_add"}
    title = "Analysis Requests"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 10
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
    contentFilter = {'portal_type': 'Sample'}
    content_add_buttons = {}
    title = "Samples"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
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
    contentFilter = {'portal_type': 'ARImport'}
    content_add_buttons = {'AR Import': "createObject?type_name=ARImport"}
    title = "Analysis Request Imports"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
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
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

class ClientARProfilesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'ARProfile'}
    content_add_buttons = {'AR Profile': "createObject?type_name=ARProfile"}
    title = "Analysis Request Profiles"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
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
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getProfileTitle': items[x]['url']}

        return items

class ClientAnalysisSpecsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisSpec'}
    content_add_buttons = {'Analysis Spec': "createObject?type_name=AnalysisSpec"}
    title = "Analysis Specifications"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
    wflist_states = []
    columns = {
               'getSampleType': {'title': 'Sample  Type'},
              }
    wflist_states = [
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
    contentFilter = {'portal_type': 'Attachment'}
    content_add_buttons = {'Attachment': "createObject?type_name=Attachment"}
    title = "Attachments"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
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
    contentFilter = {'portal_type': 'Order'}
    content_add_buttons = {'Order': "createObject?type_name=Order"}
    title = "Orders"
    description = ""
    show_editable_border = True
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
    contentFilter = {'portal_type': 'Contact'}
    content_add_buttons = {'Contact': "createObject?type_name=Contact"}
    title = "Contacts"
    description = ""
    show_editable_border = True
    batch = True
    b_size = 100
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
