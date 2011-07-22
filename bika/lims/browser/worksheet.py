from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IWorksheet
from bika.lims.browser.analysisrequest import AnalysisRequestAnalysesView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
import plone, json

class WorksheetAnalysesView(AnalysisRequestAnalysesView):
    columns = {
        'Service': {'title': _('Analysis')},
        'Pos': {'title': _('Pos')},
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'DueDate': {'title': _('Due Date')},
        'Category': {'title': _('Category')},
        'ServiceTitle': {'title': _('Analysis')},
        'Result': {'title': _('Result')},
        'Uncertainty': {'title': _('+-')},
        'retested': {'title': _('Retested'), 'type':'boolean'},
        'Attachments': {'title': _('Attachments')},
        'state_title': {'title': _('State')},
    }

    def __init__(self, context, request, allow_edit = False, **kwargs):
        super(WorksheetAnalysesView, self).__init__(context, request)
        self.contentsMethod = self.context.getAllAnalyses
        self.allow_edit = allow_edit

    def folderitems(self):
        # get worksheet analyses as a UID keyed dictionary
        analyses = {}
        for analysis in super(WorksheetAnalysesView, self).folderitems():
            # brain is object, not brain. :(
            analyses[analysis['brain'].UID()] = analysis

        # re-order items and add WS specific fields
        items = []
        for slot in self.context.getWorksheetLayout():
            item = analyses[slot['uid']]
            item['UID'] = slot['uid']
            item['Pos'] = slot['pos']
            item['Client'] = item['brain'].aq_parent.aq_parent.Title()
            item['Order'] = hasattr(item['brain'].aq_parent, 'getClientOrderNumber') and\
                            item['brain'].aq_parent.getClientOrderNumber() or \
                            ''
            item['ServiceTitle'] = item['brain'].getService().Title()
            items.append(item)
        return items


class WorksheetFolderView(BikaListingView):
    contentFilter = {'portal_type': 'Worksheet'}
    content_add_actions = {_('Worksheet'): "worksheet_add"}
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
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
                            'state_title']},
                {'title': _('Worksheet Open'), 'id':'open',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title']},
                {'title': _('To Be Verified'), 'id':'to_be_verified',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title']},
                {'title': _('Verified'), 'id':'verified',
                 'columns':['getNumber',
                            'getOwnerUserID',
                            'CreationDate',
                            'getLinkedWorksheet',
                            'state_title']},
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
            items[x]['links'] = {'getNumber': items[x]['url'] + "/manage_results"}

        return items

class WorksheetAddView(BrowserView):
    """ This creates a new Worksheet and redirects to it.
        If a template was selected, the worksheet is pre-populated here.
    """
    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, "reference_catalog")
        pc = getToolByName(self.context, "portal_catalog")
        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]
        ws.edit(Number = ws_id)

        analyses = []
        analysis_uids = []
        if form.has_key('wstemplate'):
            if not form['wstemplate'] == 'None':
                wst = rc.lookupObject(form['wstemplate'])

                rows = wst.getRow()
                services = wst.getService()
                service_uids = [s.UID() for s in services]

                count_a = 0
                count_b = 0
                count_c = 0
                count_d = 0
                for row in rows:
                    if row['type'] == 'a': count_a = count_a + 1
                    if row['type'] == 'b': count_b = count_b + 1
                    if row['type'] == 'c': count_c = count_c + 1
                    if row['type'] == 'd': count_d = count_d + 1

                selected = {}
                ars = []
                analysis_services = []
                # get the oldest analyses first
                for a in pc(portal_type = 'Analysis',
                            getServiceUID = service_uids,
                            review_state = 'sample_received',
                            sort_on = 'getDueDate'):
                    analysis = a.getObject()
                    ar = analysis.aq_parent
                    if not selected.has_key(ar.id):
                        if len(selected) < count_a:
                            selected[ar.id] = {}
                            selected[ar.id]['analyses'] = []
                            selected[ar.id]['services'] = []
                            selected[ar.id]['uid'] = ar.UID()
                            ars.append(ar.id)
                        else:
                            continue
                    selected[ar.id]['analyses'].append(analysis.UID())
                    selected[ar.id]['services'].append(analysis.getServiceUID())

                used_ars = {}
                for row in rows:
                    position = int(row['pos'])
                    if row['type'] == 'a':
                        if ars:
                            ar = ars.pop(0)
                            used_ars[position] = {}
                            used_ars[position]['ar'] = selected[ar]['uid']
                            used_ars[position]['serv'] = selected[ar]['services']
                            for analysis in selected[ar]['analyses']:
                                analyses.append((position, analysis))
                    if row['type'] in ['b', 'c']:
                        sampletype_uid = row['sub']
                        references = {}
                        reference_found = False
                        for s in pc(portal_type = 'ReferenceSample',
                                    review_state = 'current',
                                    getReferenceDefinitionUID = sampletype_uid):
                            reference = s.getObject()
                            reference_uid = reference.UID()
                            references[reference_uid] = {}
                            references[reference_uid]['services'] = []
                            references[reference_uid]['count'] = 0
                            specs = reference.getResultsRangeDict()
                            for service_uid in service_uids:
                                if specs.has_key(service_uid):
                                    references[reference_uid]['services'].append(service_uid)
                                    references[reference_uid]['count'] += 1
                            if references[reference_uid]['count'] == len(service_uids):
                                # this reference has all the services
                                reference_found = True
                                break
                        if reference_found:
                            ws.assignReference(Reference = reference_uid,
                                               Position = position,
                                               Type = row['type'],
                                               Service = service_uids)
                        else:
                            # find the reference with the most services
                            these_services = service_uids
                            reference_keys = references.keys()
                            no_of_services = 0
                            mostest = None
                            for key in reference_keys:
                                if references[key]['count'] > no_of_services:
                                    no_of_services = references[key]['count']
                                    mostest = key
                            if mostest:
                                ws.assignReference(Reference = mostest,
                                                   Position = position,
                                                   Type = row['type'],
                                                   Service = references[mostest]['services'])

                if analyses:
                    ws.assignNumberedAnalyses(Analyses = analyses)

                if count_d:
                    for row in rows:
                        if row['type'] == 'd':
                            position = int(row['pos'])
                            dup_pos = int(row['dup'])
                            if used_ars.has_key(dup_pos):
                                ws.assignDuplicate(AR = used_ars[dup_pos]['ar'],
                                                   Position = position,
                                                   Service = used_ars[dup_pos]['serv'])

                ws.setMaxPositions(len(rows))

        ws.reindexObject()

        dest = ws.absolute_url()
        self.request.RESPONSE.redirect(dest)

class WorksheetManageResultsView(BrowserView):
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")

    def __init__(self, context, request):
        super(WorksheetManageResultsView, self).__init__(context, request)
        self.sequence = sequence

    def __call__(self):
        self.AnalysesView = WorksheetAnalysesView(self.context,
                                                  self.request,
                                                  allow_edit = True)
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

    def WorksheetLayout(self):
        return self.context.getWorksheetLayout()

    def sort_analyses_on_requestid(self, analyses):
        ## Script (Python) "sort_analyses_on_requestid"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=analyses
        ##title=
        ##
        r = {}
        for a in analyses:
            ar_id = a.aq_parent.getRequestID()
            l = r.get(ar_id, [])
            l.append(a)
            r[ar_id] = l
        k = r.keys()
        k.sort()
        result = []
        for ar_id in k:
            result += r[ar_id]
        return result

class WorksheetAddAnalysisView(BikaListingView):
    content_add_actions = {}
    contentFilter = {'portal_type': 'Analysis',
                     'review_state':'sample_received',
                     'path':{'query': '/', 'depth':10}, # XXX path should not be needed?
						# XXX limit resultset
                     }
    show_editable_border = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    pagesize = 20

    columns = {
        'getClientName': {'title': _('Client')},
        'getClientOrderNumber': {'title': _('Order')},
        'getRequestID': {'title': _('Request ID')},
        'getCategoryName': {'title': _('Category')},
        'getTitle': {'title': _('Analysis')},
        'getDateReceived': {'title': _('Date Received')},
        'getDueDate': {'title': _('Due Date')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'transitions': ['assign'],
         'columns':['getClientName',
                    'getClientOrderNumber',
                    'getRequestID',
                    'getCategoryName',
                    'getTitle',
                    'getDateReceived',
                    'getDueDate'],
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['getDateReceived'] = self.context.toLocalizedTime(items[x]['getDateReceived'], long_format = 0)
            items[x]['getDueDate'] = self.context.toLocalizedTime(items[x]['getDueDate'], long_format = 0)
        return items

    def form_submit(self, form):
        # the analyses have been set to 'assigned' before this function is invoked.
        # here, we just want to add the affected analyses to our worksheet
        pc = getToolByName(self.context, 'portal_catalog')
        for path in form['paths']:
            # get selected analysis object from catalog
            item_id = path.split("/")[-1]
            item_path = path.replace("/"+item_id, '')
            analysis = pc(id=item_id, path={'query':item_path, 'depth':1})[0].getObject()
            # add this item to worksheet Analyses reference field
            analyses = self.context.getAnalyses()
            analyses.append(analysis)
            self.context.setAnalyses(analyses)
            # add this item to WorksheetLayout field in the next available slot
            layout = self.context.getWorksheetLayout()
            layout.append({'uid':analysis.UID(), 'type':'a', 'pos':len(layout), 'key':analysis.getKeyword()})
            self.context.setWorksheetLayout(layout)
        self.request.RESPONSE.redirect(self.context.absolute_url() + "/worksheet_manage_results")

class WorksheetAddBlankView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    pagesize = 20

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
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    pagesize = 20

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
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
    pagesize = 20

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

class AJAXGetWorksheetTemplates():
    """ Return Worksheet Template IDs for add worksheet dropdown """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        pc = getToolByName(self.context, "portal_catalog")
        templates = []
        for t in pc(portal_type="WorksheetTemplate"):
            templates.append((t.UID, t.Title))
        return json.dumps(templates)

