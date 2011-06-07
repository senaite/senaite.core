from Products.CMFCore.utils import getToolByName
from Products.bika import bikaMessageFactory as _
from Products.bika.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

class ClientAnalysisRequestsView(BikaListingView):
    contentFilter = {'portal_type': 'AnalysisRequest'}
    content_add_buttons = {_('Analysis Request'): "analysisrequest_add"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'getRequestID': {'title': _('Request ID')},
           'getContact': {'title': _('Contact')},
           'getClientOrderNumber': {'title': _('Client Order')},
           'ClientReference': {'title': _('Client Ref')},
           'ClientSampleID': {'title': _('Client Sample')},
           'SampleType': {'title': _('Sample Type')},
           'SamplePoint': {'title': _('Sample Point')},
           'getDateReceived': {'title': _('Date Received')},
           'getDatePublished': {'title': _('Date Published')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived',
                            'getDatePublished',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Sample due'), 'id':'sample_due',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Sample received'), 'id':'sample_received',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Assigned to Worksheet'), 'id':'assigned',
                 'columns':['getRequestID',
                            'getContact',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived']},
                {'title': _('To be verified'), 'id':'to_be_verified',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived']},
                {'title': _('Verified'), 'id':'verified',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived']},
                {'title': _('Published'), 'id':'published',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'ClientReference',
                            'ClientSampleID',
                            'SampleType',
                            'SamplePoint',
                            'getDateReceived',
                            'getDatePublished']},
                ]

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Requests"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            sample = obj.getSample()
            items[x]['SampleType'] = sample.getSampleType().Title()
            items[x]['SamplePoint'] = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            items[x]['ClientReference'] = sample.getClientReference()
            items[x]['ClientSampleID'] = sample.getClientSampleID()
            items[x]['getDateReceived'] = obj.getDateReceived() and self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''
            items[x]['getDatePublished'] = obj.getDatePublished() and self.context.toLocalizedTime(obj.getDatePublished(), long_format = 0) or ''

            items[x]['links'] = {'getRequestID': items[x]['url']}

        return items

class ClientSamplesView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'Sample'}
    content_add_buttons = {}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = False
    batch = True
    pagesize = 20

    columns = {
           'getSampleID': {'title': _('Sample ID')},
           'Requests': {'title': _('Requests')},
           'getClientReference': {'title': _('Client Ref')},
           'getClientSampleID': {'title': _('Client SID')},
           'SampleType': {'title': _('Sample Type')},
           'SamplePoint': {'title': _('Sample Point')},
           'getDateReceived': {'title': _('Date Received')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'SampleType',
                             'SamplePoint',
                             'getDateReceived',
                             'state_title']},
                {'title': _('Due'), 'id':'due',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'SampleType',
                             'SamplePoint']},
                {'title': _('Received'), 'id':'received',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'SampleType',
                             'SamplePoint',
                             'getDateReceived']},
                {'title': _('Expired'), 'id':'expired',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'SampleType',
                             'SamplePoint',
                             'getDateReceived']},
                {'title': _('Disposed'), 'id':'disposed',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'SampleType',
                             'SamplePoint',
                             'getDateReceived']},
                ]

    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['Requests'] = ",".join([o.Title() for o in obj.getAnalysisRequests()])
            items[x]['SampleType'] = obj.getSampleType().Title()
            items[x]['SamplePoint'] = obj.getSamplePoint() and obj.getSamplePoint().Title()
            items[x]['getDateReceived'] = obj.getDateReceived() and self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''

            items[x]['links'] = {'getSampleID': items[x]['url']}

        return items

class ClientARImportsView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'ARImport'}
    content_add_buttons = {_('AR Import'): "createObject?type_name=ARImport"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'title_or_id': {'title': _('Import')},
           'getDateImported': {'title': _('Date Imported')},
           'getStatus': {'title': _('Validity')},
           'getDateApplied': {'title': _('Date Submitted')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['title_or_id',
                             'getDateImported',
                             'getStatus',
                             'getDateApplied',
                             'state_title']},
                {'title': _('Imported'), 'id':'imported',
                 'columns': ['title_or_id',
                             'getDateImported',
                             'getStatus']},
                {'title': _('Applied'), 'id':'submitted',
                 'columns': ['title_or_id',
                             'getDateImported',
                             'getStatus',
                             'getDateApplied']},
                ]

    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Request Imports"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

class ClientARProfilesView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'ARProfile'}
    content_add_buttons = {_('AR Profile'): "createObject?type_name=ARProfile"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'getProfileTitle': {'title': _('Title')},
           'getProfileKey': {'title': _('Profile Key')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['getProfileTitle',
                             'getProfileKey']},
                ]

    def __init__(self, context, request):
        super(ClientARProfilesView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Request Profiles"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {'getProfileTitle': items[x]['url'] + "/base_edit"}

        return items

class ClientAnalysisSpecsView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'AnalysisSpec'}
    content_add_buttons = {_('Analysis Spec'): "createObject?type_name=AnalysisSpec"}
    show_editable_border = True
    batch = True
    b_size = 100
    columns = {
           'getSampleType': {'title': _('Sample  Type')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['getSampleType']},
                ]

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Specifications"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {'getSampleType': items[x]['url']}

        return items

class ClientAttachmentsView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'Attachment'}
    content_add_buttons = {_('Attachment'): "createObject?type_name=Attachment"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'getTextTitle': {'title': _('Request ID')},
           'AttachmentFile': {'title': _('File')},
           'AttachmentType': {'title': _('Attachment Type')},
           'ContentType': {'title': _('Content Type')},
           'FileSize': {'title': _('Size')},
           'DateLoaded': {'title': _('Date Loaded')},
          }
    review_states = [
                {'title': 'All', 'id':'all',
                 'columns': ['getTextTitle',
                             'AttachmentFile',
                             'AttachmentType',
                             'ContentType',
                             'FileSize',
                             'DateLoaded']},
                ]

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Attachments"))
        self.description = ""

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
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
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

class ClientOrdersView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'Order'}
    content_add_buttons = {_('Order'): "createObject?type_name=Order"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'OrderNumber': {'title': _('Order Number')},
           'OrderDate': {'title': _('Order Date')},
           'DateDispatched': {'title': _('Date dispatched')},
           'state_title': {'title': _('State')},
          }
    review_states = [
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

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Orders"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = obj.getOrderDate()
            items[x]['DateDispatched'] = obj.getDateDispatched()

            items[x]['links'] = {'OrderNumber': obj.absolute_url()}

        return items

class ClientContactsView(BikaListingView):
    implements(IFolderContentsView)

    contentFilter = {'portal_type': 'Contact'}
    content_add_buttons = {_('Contact'): "createObject?type_name=Contact"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'getFullname': {'title': _('Full Name')},
           'getEmailAddress': {'title': _('Email Address')},
           'getBusinessPhone': {'title': _('Business Phone')},
           'getMobilePhone': {'title': _('Mobile Phone')},
           'getFax': {'title': _('Fax')},
          }
    review_states = [
                {'title': 'All', 'id':'all',
                 'columns': ['getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone',
                             'getFax']},
                ]

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Contacts"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {'getFullname': items[x]['url'] + "/edit"}

        return items
