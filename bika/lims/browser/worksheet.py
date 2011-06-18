from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IWorksheet
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
from zope.publisher.browser import BrowserView

class WorksheetFolderView(BikaListingView):
    contentFilter = {'portal_type': 'Worksheet'}
    content_add_buttons = {_('Worksheet'): "worksheet_add"}
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 50

    columns = {
           'getNumber': {'title': _('Worksheet Number')},
           'getOwnerUserID': {'title': _('Username')},
           'CreationDate': {'title': _('Creation Date')},
           'getLinkedWorksheet': {'title': _('Linked Worksheets')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Worksheet Open'), 'id':'open',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('To Be Verified'), 'id':'to_be_verified',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Verified'), 'id':'verified',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]},
                {'title': _('Rejected'), 'id':'rejected',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title'],
                 'buttons':[{'cssclass': 'context',
                             'title': _('Delete'),
                             'url': 'folder_delete:method'}]}
                  ]
    def __init__(self, context, request):
        super(WorksheetFolderView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Requests"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['links'] = {'getNumber': items[x]['url']}

        return items

class WorksheetAddView(BrowserView):
    """ This creates a new Worksheet and redirects to it.
        If a template was selected, the worksheet is pre-populated here.
    """
    def __call__(self):
        form = self.request.form
        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]
        ws.edit(Number = ws_id)

        analyses = []
        analysis_uids = []
        if form.has_key('WorksheetTemplate'):
            if not form['WorksheetTemplate'] == 'None':
                uid = form['WorksheetTemplate']
                rc = self.context.reference_catalog
                wst = rc.lookupObject(uid)
                rows = wst.getRow()
                count_a = 0
                count_b = 0
                count_c = 0
                count_d = 0
                for row in rows:
                    if row['type'] == 'a': count_a = count_a + 1
                    if row['type'] == 'b': count_b = count_b + 1
                    if row['type'] == 'c': count_c = count_c + 1
                    if row['type'] == 'd': count_d = count_d + 1
                services = wst.getService()
                service_uids = [s.UID() for s in services]
                selected = {}
                ars = []
                analysis_services = []
                # get the oldest analyses first
                for a in self.context.portal_catalog(
                                portal_type = 'Analysis',
                                review_state = 'sample_received',
                                getServiceUID = service_uids,
                                sort_on = 'getDueDate'):
                    analysis = a.getObject()
                    ar_id = analysis.getRequestID()
                    ar_uid = analysis.aq_parent.UID()
                    if selected.has_key(ar_id):
                        a_uids = selected[ar_id]['a']
                        s_uids = selected[ar_id]['c']
                    else:
                        if len(selected) < count_a:
                            selected[ar_id] = {}
                            selected[ar_id]['a'] = []
                            selected[ar_id]['c'] = []
                            selected[ar_id]['uid'] = ar_uid
                            a_uids = []
                            s_uids = []
                            ars.append(ar_id)
                        else:
                            continue
                    a_uids.append(analysis.UID())
                    s_uids.append(analysis.getServiceUID())
                    selected[ar_id]['a'] = a_uids
                    selected[ar_id]['c'] = s_uids

                used_ars = {}
                for row in rows:
                    position = int(row['pos'])
                    if row['type'] == 'a':
                        if ars:
                            ar = ars.pop(0)
                            used_ars[position] = {}
                            used_ars[position]['ar'] = selected[ar]['uid']
                            used_ars[position]['serv'] = selected[ar]['c']
                            for analysis in selected[ar]['a']:
                                analyses.append((position, analysis))
                    if row['type'] in ['b', 'c']:
                        sampletype_uid = row['sub']
                        standards = {}
                        standard_found = False
                        for s in self.context.portal_catalog(
                                portal_type = 'StandardSample',
                                review_state = 'current',
                                getStandardStockUID = sampletype_uid):
                            standard = s.getObject()
                            standard_uid = standard.UID()
                            standards[standard_uid] = {}
                            standards[standard_uid]['services'] = []
                            standards[standard_uid]['count'] = 0
                            specs = standard.getResultsRangeDict()
                            for service_uid in service_uids:
                                if specs.has_key(service_uid):
                                    standards[standard_uid]['services'].append(service_uid)
                                    count = standards[standard_uid]['count']
                                    count += 1
                                    standards[standard_uid]['count'] = count
                            if standards[standard_uid]['count'] == len(service_uids):
                                # this standard has all the services
                                standard_found = True
                                break
                        if standard_found:
                            ws.assignStandard(Standard = standard_uid, Position = position, Type = row['type'], Service = service_uids)
                        else:
                            # find the standard with the most services
                            these_services = service_uids
                            standard_keys = standards.keys()
                            no_of_services = 0
                            mostest = None
                            for key in standard_keys:
                                if standards[key]['count'] > no_of_services:
                                    no_of_services = standards[key]['count']
                                    mostest = key
                            if mostest:
                                ws.assignStandard(Standard = mostest, Position = position, Type = row['type'], Service = standards[mostest]['services'])

                if analyses:
                    ws.assignNumberedAnalyses(Analyses = analyses)

                if count_d:
                    for row in rows:
                        if row['type'] == 'd':
                            position = int(row['pos'])
                            dup_pos = int(row['sub'])
                            if used_ars.has_key(dup_pos):
                                ws.assignDuplicate(AR = used_ars[dup_pos]['ar'], Position = position, Service = used_ars[dup_pos]['serv'])

                ws.setMaxPositions(len(rows))

        ws.reindexObject()

        dest = ws.absolute_url()
        self.request.RESPONSE.redirect(dest)

class WorksheetView(BrowserView):
    template = ViewPageTemplateFile("templates/worksheet.pt")

    def __call__(self):
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

class WorksheetManageResultsView(BrowserView):
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")

    def __call__(self):
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

class WorksheetAddAnalysisView(BikaListingView):
    content_add_buttons = {}
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    batch = True
    pagesize = 50

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['links'] = {'getNumber': items[x]['url']}

        return items

class WorksheetAddBlankView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_buttons = {}
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    batch = True
    pagesize = 50

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['links'] = {'getNumber': items[x]['url']}

        return items

class WorksheetAddControlView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_buttons = {}
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    batch = True
    pagesize = 50

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['links'] = {'getNumber': items[x]['url']}

        return items

class WorksheetAddDuplicateView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_buttons = {}
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    batch = True
    pagesize = 50

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['links'] = {'getNumber': items[x]['url']}

        return items


