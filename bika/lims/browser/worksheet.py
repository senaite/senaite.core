from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.interfaces import IWorksheet
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.analyses import AnalysesView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import implements
import plone, json

class WorksheetWorkflowAction(WorkflowAction):
    """ Workflow actions taken in Worksheets
        This function is called to do the worflow actions
        that apply to analyses in worksheets
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
        # only "activate" workflow_action is allowed on Worksheets which are
        # inactive. any action on inactive Worksheet's children is also ignored.
        if action and \
           'bika_inactive_workflow' in workflow.getChainFor(self.context) and \
           workflow.getInfoFor(self.context, 'inactive_review_state', '') == 'inactive' and \
           action != 'activate':
            message = self.context.translate(
                'message_item_is_inactive',
                default='${item} is inactive.',
                mapping={'item': self.context.Title()},
                domain="bika")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return

        # assign selected analyses to this worksheet
        if action == 'assign':
            analyses = []
            if 'paths' in form:
                for path in form['paths']:
                    # get selected analysis object from catalog
                    item_id = path.split("/")[-1]
                    item_path = path.replace("/"+item_id, '')
                    analysis = pc(id=item_id, path={'query':item_path,
                                                    'depth':1})[0].getObject()
                    analyses.append(analysis)
                # add this item to worksheet Analyses field
                ws_analyses = self.context.getAnalyses()
                #ws_layout = self.context.getWorksheetLayout()
                #pos_max = max([p['pos'] for p in ws_layout.values()])
                for analysis in analyses:
                    ws_analyses.append(analysis)
                #    ws_layout.append({'uid':analysis.UID(),
                #                   'type':'a',
                #                   'pos':len(ws_layout),
                #                   'key':analysis.getKeyword()})
                self.context.setAnalyses(ws_analyses)
                #self.context.setWorksheetLayout(ws_layout)
                for analysis in analyses:
                    workflow.doActionFor(analysis, 'assign')

            if len(analyses) > 1:
                message = _('message_items_assigned',
                    default = "${items} analyses were assigned.",
                    mapping = {'items': len(analyses)})
            elif len(analyses) == 1:
                message = _('message_item_assigned',
                    default = "1 analysis was assigned.")
            else:
                message = _("No action taken.")
                self.context.plone_utils.addPortalMessage(message, 'info')
                return self.request.RESPONSE.redirect(originating_url)
            self.context.plone_utils.addPortalMessage(message, 'info')
            return self.request.RESPONSE.redirect(self.context.absolute_url() + "/manage_results")

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(),
                                              long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and \
                 ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

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
            if form['wstemplate'] != '':
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
                                ws.assignReference(
                                    Reference = mostest,
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
                                ws.assignDuplicate(
                                    AR = used_ars[dup_pos]['ar'],
                                    Position = position,
                                    Service = used_ars[dup_pos]['serv'])

                ws.setMaxPositions(len(rows))

        ws.reindexObject()

        dest = ws.absolute_url()
        self.request.RESPONSE.redirect(dest)

class WorksheetManageResultsView(AnalysesView):

    def __init__(self, context, request, allow_edit = False, **kwargs):
        super(WorksheetManageResultsView, self).__init__(context, request)
        self.show_select_row = True
        self.show_sort_column = True
        self.allow_edit = True

        # dodge catalog acquisition
        self.has_bika_inactive_workflow = True

        self.columns = {
            'Pos': {'title': _('Pos')},
            'Client': {'title': _('Client')},
            'Order': {'title': _('Order')},
            'RequestID': {'title': _('Reqest ID')},
            'DueDate': {'title': _('Due Date')},
            'Category': {'title': _('Category')},
            'Service': {'title': _('Analysis')},
            'Result': {'title': _('Result')},
            'Uncertainty': {'title': _('+-')},
            'retested': {'title': _('Retested'), 'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns':['Pos',
                        'Client',
                        'Order',
                        'RequestID',
                        'DueDate',
                        'Category',
                        'Service',
                        'Result',
                        'Attachments',
                        'state_title'],
             },
        ]

    def folderitems(self):
        self.contentsMethod = self.context.getFolderContents
        items = AnalysesView.folderitems(self)
        pos = 0
        for x, item in enumerate(items):
            obj = item['obj']
            pos += 1
            items[x]['Pos'] = pos
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            items[x]['RequestID'] = obj.aq_parent.Title()
            items[x]['Client'] = obj.aq_parent.aq_parent.Title()
            items[x]['DueDate'] = hasattr(obj, 'DueDate') and \
                self.context.toLocalizedTime(obj.DueDate, long_format=0) or ''
            items[x]['Order'] = hasattr(obj.aq_parent, 'getClientOrderNumber') \
                 and obj.aq_parent.getClientOrderNumber() or ''
            if obj.portal_type == 'DuplicateAnalysis':
                items[x]['after']['Pos'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/duplicate.png"/>'%\
                    (self.context.absolute_url())
            elif obj.portal_type == 'ReferenceAnalysis':
                if obj.ReferenceType == 'b':
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/>'%\
                        (self.context.absolute_url())
                else:
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/>'%\
                        (self.context.absolute_url())

        return items

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

class WorksheetAddAnalysisView(AnalysesView):
    def __init__(self, context, request):
        super(WorksheetAddAnalysisView, self).__init__(context, request)
        self.content_add_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received'}
        self.show_editable_border = True
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url  + "/add_analysis"
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.show_filters = True
        self.pagesize = 50

        self.columns = {
            'ClientName': {'title': _('Client')},
            'getClientOrderNumber': {'title': _('Order')},
            'getRequestID': {'title': _('Request ID')},
            'CategoryName': {'title': _('Category')},
            'Title': {'title': _('Analysis')},
            'getDateReceived': {'title': _('Date Received')},
            'getDueDate': {'title': _('Due Date')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': ['assign'],
             'columns':['ClientName',
                        'getClientOrderNumber',
                        'getRequestID',
                        'CategoryName',
                        'Title',
                        'getDateReceived',
                        'getDueDate'],
            },
        ]

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        self.contentsMethod = pc
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            service = obj.getService()
            client = obj.aq_parent.aq_parent
            items[x]['getDateReceived'] = self.context.toLocalizedTime(
                items[x]['getDateReceived'], long_format = 0)
            items[x]['getDueDate'] = self.context.toLocalizedTime(
                items[x]['getDueDate'], long_format = 0)
            items[x]['CategoryName'] = service.getCategory().Title()
            items[x]['ClientName'] = client.Title()
        return items

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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(
                     obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and \
                 ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

        return items

class WorksheetAddControlView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis',
                     'review_state':'sample_received'}
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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and \
                 ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['getLinkedWorksheet'] = obj.getLinkedWorksheet() and \
                 ",".join(obj.getLinkedWorksheet()) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

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
