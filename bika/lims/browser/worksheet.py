from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
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
    """ This creates a new WS and redirects to it.
    """
    def __call__(self):
        req = self.context.REQUEST.form
        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]
        ws.edit(
            Number = ws_id
            )

        analyses = []
        analysis_uids = []
        if req.has_key('WorksheetTemplate'):
            if not req['WorksheetTemplate'] == 'None':
                uid = req['WorksheetTemplate']
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
        self.context.REQUEST.RESPONSE.redirect(dest)


class WorksheetAnalysesView(BrowserView):
    template = ViewPageTemplateFile("templates/worksheet_analyses.pt")
    worksheet_search = ViewPageTemplateFile("templates/worksheet_search.pt")
    worksheet_analyses_columns = ViewPageTemplateFile("templates/worksheet_analyses_columns.pt")
    worksheet_analyses_rows = ViewPageTemplateFile("templates/worksheet_analyses_rows.pt")

    sequence = sequence
    def __call__(self):
        return self.template()

    def now(self):
        return DateTime()

    def sort_analyses_on_requestid(self, analyses):
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


    def group_analyses_by_request(self, batch):
        plone_view = self.context.restrictedTraverse('@@plone')
        any_titr_vol_reqd = False
        any_weight_calc_reqd = False

        r = {}
        for analysis in batch:
            ar = analysis.aq_parent
            ar_id = ar.getId()
            sample = ar.getSample()
            sampletype = sample.getSampleType()
            samplepoint = sample.getSamplePoint() and sample.getSamplePoint().Title()
            if not r.has_key(ar_id):
                date_received = ar.getDateReceived()
                date_published = ar.getDatePublished()
                if date_published:
                    date_published = plone_view.toLocalizedTime(date_published, long_format = 1)
                r[ar_id] = { 'id': ar_id,
                             'RequestID': ar.getRequestID(),
                             'absolute_url': ar.absolute_url(),
                             'Client': ar.aq_parent,
                             'SampleID': sample.getSampleID(),
                             'Hazardous': sampletype.getHazardous(),
                             'sample_absolute_url': sample.absolute_url(),
                             'SamplePoint': samplepoint,
                             'SampleType': sampletype.Title(),
                             'sampletype_obj': sampletype,
                             'ClientReference': sample.getClientReference(),
                             'ClientSampleID': sample.getClientSampleID(),
                             'DateRequested': plone_view.toLocalizedTime(
                                 ar.getDateRequested(), long_format = 1
                                 ),
                             'DateReceived': plone_view.toLocalizedTime(
                                 date_received, long_format = 1
                                 ),
                             'DatePublished': date_published,
                             'AnyTitrReqd': False,
                             'AnyWeightReqd': False,
                             'Analyses': {},
                             'AnalysisType':'A',
                           }

            d = r[ar_id]['Analyses']
            d[analysis.getId()] = analysis
            if analysis.getTitrationRequired():
                r[ar_id]['AnyTitrReqd'] = True
            if analysis.getWeightRequired():
                r[ar_id]['AnyWeightReqd'] = True

        l = r.keys()
        l.sort()
        result_set = {}
        result_set['results'] = [r[ar_id] for ar_id in l]
        result_set['titr_reqd'] = any_titr_vol_reqd
        result_set['weight_reqd'] = any_weight_calc_reqd
        return result_set

    def group_analyses_for_worksheet(self):
        def checkCalcType(calctype):
            cols = []
            if calctype in ['wl', 'rw']:
                cols.append('gm')
                cols.append('vm')
                cols.append('nm')
                return cols
            if calctype in ['wlt', 'rwt']:
                cols.append('vm')
                cols.append('sm')
                cols.append('nm')
                return cols
            if calctype in ['t', ]:
                cols.append('tv')
                cols.append('tf')
                return cols
            return cols

        plone_view = self.context.restrictedTraverse('@@plone')
        analyses = self.context.getAnalyses()
        sort_on = (('Title', 'nocase', 'asc'),)
        analyses = sequence.sort(analyses, sort_on)

        duplicates = self.context.objectValues('DuplicateAnalysis')
        standards_and_blanks = self.context.getStandardAnalyses()
        rejects = self.context.objectValues('RejectAnalysis')

        any_cols = []
        any_published = False

        seq = {}
        keys = {}
        for item in self.context.getWorksheetLayout():
            seq[item['uid']] = item['pos']
            keys[item['uid']] = item['key']

        results = {}
        sub_results = {}

        for analysis in duplicates:
            ws = analysis.aq_parent
            ar = analysis.getRequest()
            copy_analysis = ar[analysis.getService().getId()]
            due_date = copy_analysis.getDueDate()
            sample = ar.getSample()
            sampletype = sample.getSampleType()
            copy_id = '(%s)' % (ar.getId())
            pos = seq[analysis.UID()]
            calctype = analysis.getCalcType()
            cols = checkCalcType(calctype)
            if cols:
                any_cols.extend(cols)
            if len(cols) > 0 or calctype == 'dep':
                calcd = True
            else:
                calcd = False
            parent_link = "%s/base_edit" % (ar.aq_parent.absolute_url())
            sub_results = {
                         'RequestID': copy_id,
                         'OrderID': ar.getClientOrderNumber(),
                         'absolute_url': ar.absolute_url(),
                         'ParentTitle': ar.aq_parent.Title(),
                         'ParentLink': parent_link,
                         'ParentUID': ' ',
                         'sampletype_uid': sampletype.UID(),
                         'DueDate': plone_view.toLocalizedTime(
                             due_date, long_format = 1
                             ),
                         'DatePublished': '',
                         'Analysis': analysis,
                         'Cols': cols,
                         'Calcd': calcd,
                         'Type': 'd',
                         'Key': '',
                         'Pos': pos,
                       }
            if not results.has_key(pos):
                results[pos] = []
            results[pos].append(sub_results)

        for analysis in rejects:
            ws = analysis.aq_parent
            ar = analysis.getRequest()
            real_analysis = ar[analysis.getService().getId()]
            due_date = real_analysis.getDueDate()
            sample = ar.getSample()
            sampletype = sample.getSampleType()
            copy_id = '(%s)' % (ar.getId())
            pos = seq[analysis.UID()]
            calctype = analysis.getCalcType()
            cols = checkCalcType(calctype)
            if cols:
                any_cols.extend(cols)
            if len(cols) > 0 or calctype == 'dep':
                calcd = True
            else:
                calcd = False
            parent_link = "%s/base_edit" % (ar.aq_parent.absolute_url())
            sub_results = {
                         'RequestID': copy_id,
                         'OrderID': ar.getClientOrderNumber(),
                         'absolute_url': ar.absolute_url(),
                         'ParentTitle': ar.aq_parent.Title(),
                         'ParentLink': parent_link,
                         'ParentUID': ar.aq_parent.UID(),
                         'sampletype_uid': sampletype.UID(),
                         'DueDate': plone_view.toLocalizedTime(
                             due_date, long_format = 1
                             ),
                         'DatePublished': '',
                         'Analysis': analysis,
                         'Cols': cols,
                         'Calcd': calcd,
                         'Type': 'r',
                         'Key': '',
                         'Pos': pos,
                       }
            if not results.has_key(pos):
                results[pos] = []
            results[pos].append(sub_results)

        for analysis in standards_and_blanks:
            std_sample = analysis.aq_parent
            ss_id = std_sample.getId()
            stock = std_sample.getStandardStock()
            if stock:
                stock_uid = std_sample.getStandardStock().UID()
            else:
                stock_uid = None;
            pos = seq[analysis.UID()]
            calctype = analysis.getCalcType()
            cols = checkCalcType(calctype)
            if cols:
                any_cols.extend(cols)
            if len(cols) > 0 or calctype == 'dep':
                calcd = True
            else:
                calcd = False
            ss_id = analysis.aq_parent.getStandardID()
            parent_link = "%s/base_edit" % (std_sample.aq_parent.absolute_url())
            sub_results = {
                         'RequestID': analysis.aq_parent.getStandardID(),
                         'OrderID': '',
                         'absolute_url': std_sample.absolute_url(),
                         'ParentTitle': std_sample.aq_parent.Title(),
                         'ParentLink': parent_link,
                         'ParentUID': std_sample.aq_parent.UID(),
                         'sampletype_uid': stock_uid,
                         'DueDate': '',
                         'DatePublished': '',
                         'Analysis': analysis,
                         'Cols': cols,
                         'Calcd': calcd,
                         'Type': analysis.getStandardType(),
                         'Key': '',
                         'Pos': pos,
                       }
            if not results.has_key(pos):
                results[pos] = []
            results[pos].append(sub_results)

        for analysis in analyses:
            ar = analysis.aq_parent
            ar_id = ar.getId()
            sample = ar.getSample()
            sampletype = sample.getSampleType()
            due_date = analysis.getDueDate()
            date_published = analysis.getDateAnalysisPublished()
            if date_published:
                date_published = plone_view.toLocalizedTime(date_published, long_format = 1)
                any_published = True
            pos = seq[analysis.UID()]
            key = keys[analysis.UID()]
            calctype = analysis.getCalcType()
            cols = checkCalcType(calctype)
            if cols:
                any_cols.extend(cols)
            if len(cols) > 0 or calctype == 'dep':
                calcd = True
            else:
                calcd = False
            parent_link = "%s/base_edit" % (ar.aq_parent.absolute_url())
            sub_results = {
                         'RequestID': ar.getRequestID(),
                         'OrderID': ar.getClientOrderNumber(),
                         'absolute_url': ar.absolute_url(),
                         'ParentTitle': ar.aq_parent.Title(),
                         'ParentLink': parent_link,
                         'ParentUID': ar.aq_parent.UID(),
                         'sampletype_uid': sampletype.UID(),
                         'DueDate': plone_view.toLocalizedTime(
                             due_date, long_format = 1
                             ),
                         'DatePublished': date_published,
                         'Analysis': analysis,
                         'Cols': cols,
                         'Calcd': calcd,
                         'Type': 'a',
                         'Key': key,
                         'Pos': pos,
                       }
            if not results.has_key(pos):
                results[pos] = []
            results[pos].append(sub_results)

        l = results.keys()
        l.sort()
        result_set = {}
        all_results = []
        for pos in l:
            all_results = all_results + results[pos]
        any_cols.sort()
        final_cols = []
        for col in any_cols:
            if col not in final_cols: final_cols.append(col)

        result_set['results'] = all_results
        result_set['any_cols'] = final_cols
        result_set['published'] = any_published
        return result_set
