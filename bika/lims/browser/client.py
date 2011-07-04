from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

class ClientAnalysisRequestsView(BikaListingView):
    contentFilter = {'portal_type': 'AnalysisRequest'}
    content_add_actions = {_('Analysis Request'): "analysisrequest_add"}
    show_editable_border = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 10

    columns = {
           'getRequestID': {'title': _('Request ID')},
           'getClientOrderNumber': {'title': _('Client Order')},
           'getClientReference': {'title': _('Client Ref')},
           'getClientSampleID': {'title': _('Client Sample')},
           'getSampleTypeTitle': {'title': _('Sample Type')},
           'getSamplePointTitle': {'title': _('Sample Point')},
           'getDateReceived': {'title': _('Date Received')},
           'getDatePublished': {'title': _('Date Published')},
           'state_title': {'title': _('State'), },
    }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived',
                            'getDatePublished',
                            'state_title']},
                {'title': _('Sample due'), 'id':'sample_due',
                 'transitions': ['cancel', 'receive'],
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle']},
                {'title': _('Sample received'), 'id':'sample_received',
                 'transitions': ['cancel'],
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Assigned to Worksheet'), 'id':'assigned',
                 'transitions': ['cancel'],
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('To be verified'), 'id':'to_be_verified',
                 'transitions': ['cancel', 'verify'],
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Verified'), 'id':'verified',
                 'transitions': ['cancel', 'publish'],
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Published'), 'id':'published',
                 'columns':['getRequestID',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
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
            items[x]['getDateReceived'] = items[x]['getDateReceived'] and \
                self.context.toLocalizedTime(items[x]['getDateReceived'], long_format = 0) or ''
            items[x]['links'] = {'getRequestID': items[x]['url']}
        return items

class ClientSamplesView(BikaListingView):
    contentFilter = {'portal_type': 'Sample'}
    content_add_actions = {}
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
           'getSampleTypeTitle': {'title': _('Sample Type')},
           'getSamplePointTitle': {'title': _('Sample Point')},
           'getDateReceived': {'title': _('Date Received')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'getSampleTypeTitle',
                             'getSamplePointTitle',
                             'getDateReceived',
                             'state_title']},
                {'title': _('Due'), 'id':'due',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'getSampleTypeTitle',
                             'getSamplePointTitle']},
                {'title': _('Received'), 'id':'received',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'getSampleTypeTitle',
                             'getSamplePointTitle',
                             'getDateReceived']},
                {'title': _('Expired'), 'id':'expired',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'getSampleTypeTitle',
                             'getSamplePointTitle',
                             'getDateReceived']},
                {'title': _('Disposed'), 'id':'disposed',
                 'columns': ['getSampleID',
                             'Requests',
                             'getClientReference',
                             'getClientSampleID',
                             'getSampleTypeTitle',
                             'getSamplePointTitle',
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
            items[x]['getDateReceived'] = items[x]['getDateReceived'] and \
                 self.context.toLocalizedTime(items[x]['getDateReceived'], long_format = 0) or ''
            items[x]['links'] = {'getSampleID': items[x]['url']}

        return items

class ClientARImportsView(BikaListingView):
    contentFilter = {'portal_type': 'ARImport'}
    content_add_actions = {_('AR Import'): "createObject?type_name=ARImport"}
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
    contentFilter = {'portal_type': 'ARProfile'}
    content_add_actions = {_('AR Profile'): "createObject?type_name=ARProfile"}
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
    contentFilter = {'portal_type': 'AnalysisSpec'}
    content_add_actions = {_('Analysis Spec'): "createObject?type_name=AnalysisSpec"}
    show_editable_border = True
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
           'getSampleType': {'title': _('Sample  Type')},
          }
    review_states = [
                     {'title': _('All'), 'id':'all',
                      'columns': ['getSampleType'],
                      'buttons':[{'cssclass': 'context',
                                  'title': _('Delete'),
                                  'url': 'folder_delete:method'},
                                 {'cssclass':'context',
                                  'title': _('Duplicate'),
                                  'url': 'duplicate_analysisspec:method',
                                 }
                                ],
                     },
                    ]

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Specifications"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getSampleType'] = obj.getSampleType() and obj.getSampleType().Title()
            items[x]['links'] = {'getSampleType': items[x]['url'] + "/edit"}

        return items



class ClientAttachmentsView(BikaListingView):
    contentFilter = {'portal_type': 'Attachment'}
    content_add_actions = {_('Attachment'): "createObject?type_name=Attachment"}
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
    contentFilter = {'portal_type': 'Order'}
    content_add_actions = {_('Order'): "createObject?type_name=Order"}
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
    contentFilter = {'portal_type': 'Contact'}
    content_add_actions = {_('Contact'): "createObject?type_name=Contact"}
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
