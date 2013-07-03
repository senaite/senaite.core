# coding=utf-8
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.permissions import *
from bika.lims.utils import isActive
from zope.component import getMultiAdapter
from zope.interface import implements
import json
import plone
from bika.lims.interfaces import IAnalysisRangeAlerts
from operator import itemgetter


class AnalysesView(BikaListingView):
    implements(IAnalysisRangeAlerts)
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to bika_analysis_catalog.
    """
    def __init__(self, context, request, **kwargs):
        self.catalog = "bika_analysis_catalog"
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.contentFilter['sort_on'] = 'sortable_title'
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 1000
        self.form_id = 'analyses_form'

        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

        request.set('disable_plone.rightcolumn', 1);

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = {
            'Service': {'title': _('Analysis'),
                        'sortable': False},
            'Partition': {'title': _("Partition"),
                          'sortable':False},
            'Method': {'title': _('Method'),
                       'sortable': False},
            'state_title': {'title': _('Status'),
                            'sortable': False},
            'Result': {'title': _('Result'),
                       'input_width': '6',
                       'input_class': 'ajax_calculate numeric',
                       'sortable': False},
            'ResultDM': {'title': _('Dry'),
                         'sortable': False},
            'Uncertainty': {'title': _('+-'),
                            'sortable': False},
            'retested': {'title': "<img title='%s' src='%s/++resource++bika.lims.images/retested.png'/>"%\
                         (context.translate(_('Retested')), self.portal_url),
                         'type':'boolean',
                         'sortable': False},
            'Attachments': {'title': _('Attachments'),
                            'sortable': False},
            'CaptureDate': {'title': _('Captured'),
                            'index': 'getResultCaptureDate',
                            'sortable':False},
            'DueDate': {'title': _('Due Date'),
                        'index': 'getDueDate',
                        'sortable':False},
        }

        self.review_states = [
            {'id': 'default',
             'title':  _('All'),
             'contentFilter': {},
             'columns': ['Service',
                         'Partition',
                         'Method',
                         'Result',
                         'Uncertainty',
                         'CaptureDate',
                         'DueDate',
                         'state_title',
                         'Attachments'],
             },
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

        self.chosen_spec = request.get('specification', 'lab')
        super(AnalysesView, self).__init__(context,
                                           request,
                                           show_categories=context.bika_setup.getCategoriseAnalysisServices(),
                                           expand_all_categories=True)

    def folderitems(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if not self.allow_edit:
            can_edit_analyses = False
        else:
            if self.contentFilter.get('getPointOfCapture', '') == 'field':
                can_edit_analyses = checkPermission(EditFieldResults, self.context)
            else:
                can_edit_analyses = checkPermission(EditResults, self.context)
            self.allow_edit = can_edit_analyses
        self.show_select_column = self.allow_edit
        context_active = isActive(self.context)

        items = super(AnalysesView, self).folderitems(full_objects = True)

        # manually skim retracted analyses from the list
        new_items = []
        for i,item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'retracted' \
                and not checkPermission(ViewRetractedAnalyses, self.context):
                continue
            new_items.append(item)
        items = new_items

        self.interim_fields = {}
        self.interim_columns = {}
        self.specs = {}
        for i, item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'retracted' \
                and not checkPermission(ViewRetractedAnalyses, self.context):
                continue

            result = obj.getResult()
            service = obj.getService()
            calculation = service.getCalculation()
            unit = service.getUnit()
            keyword = service.getKeyword()
            precision = service.getPrecision()

            if self.show_categories:
                cat = obj.getService().getCategoryTitle()
                items[i]['category'] = cat
                if cat not in self.categories:
                    self.categories.append(cat)

            # Check for InterimFields attribute on our object,
            interim_fields = hasattr(obj, 'getInterimFields') \
                and obj.getInterimFields() or []
            self.interim_fields[obj.UID()] = interim_fields

            items[i]['Service'] = service.Title()
            items[i]['Keyword'] = keyword
            items[i]['Unit'] = unit and unit or ''
            items[i]['Result'] = ''
            items[i]['formatted_result'] = ''
            items[i]['interim_fields'] = interim_fields
            items[i]['Remarks'] = obj.getRemarks()
            items[i]['Uncertainty'] = ''
            items[i]['retested'] = obj.getRetested()
            items[i]['class']['retested'] = 'center'
            items[i]['result_captured'] = self.ulocalized_time(
                obj.getResultCaptureDate(), long_format=0)
            items[i]['calculation'] = calculation and True or False
            try:
                items[i]['Partition'] = obj.getSamplePartition().getId()
            except AttributeError:
                items[i]['Partition'] = ''
            if obj.portal_type == "ReferenceAnalysis":
                items[i]['DueDate'] = self.ulocalized_time(obj.aq_parent.getExpiryDate(), long_format=0)
            else:
                items[i]['DueDate'] = self.ulocalized_time(obj.getDueDate(), long_format=1)
            cd = obj.getResultCaptureDate()
            items[i]['CaptureDate'] = cd and self.ulocalized_time(cd, long_format=1) or ''
            items[i]['Attachments'] = ''

            # calculate specs
            if obj.portal_type == 'ReferenceAnalysis':
                items[i]['st_uid'] = obj.aq_parent.UID()
            elif obj.portal_type == 'DuplicateAnalysis' and \
                obj.getAnalysis().portal_type == 'ReferenceAnalysis':
                items[i]['st_uid'] = obj.aq_parent.UID()
            else:
                if self.context.portal_type == 'AnalysisRequest':
                    sample = self.context.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                elif self.context.portal_type == "Worksheet":
                    if obj.portal_type == "DuplicateAnalysis":
                        sample = obj.getAnalysis().getSample()
                    else:
                        sample = obj.aq_parent.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                elif self.context.portal_type == 'Sample':
                    st_uid = self.context.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                else:
                    proxies = []
                if st_uid not in self.specs:
                    for spec in (p.getObject() for p in proxies):
                        client_or_lab = ""
                        if spec.getClientUID() == obj.getClientUID():
                            client_or_lab = 'client'
                        elif spec.getClientUID() == self.context.bika_setup.bika_analysisspecs.UID():
                            client_or_lab = 'lab'
                        else:
                            continue
                        for keyword, results_range in \
                            spec.getResultsRangeDict().items():
                            # hidden form field 'specs' keyed by sampletype uid:
                            # {st_uid: {'lab/client':{keyword:{min,max,error}}}}
                            if st_uid in self.specs:
                                if client_or_lab in self.specs[st_uid]:
                                    self.specs[st_uid][client_or_lab][keyword] = results_range
                                else:
                                    self.specs[st_uid][client_or_lab] = {keyword: results_range}
                            else:
                                self.specs[st_uid] = {client_or_lab: {keyword: results_range}}

            method = service.getMethod()
            items[i]['Method'] = method and method.Title() or ''
            if method:
                items[i]['replace']['Method'] = "<a href='%s'>%s</a>" % \
                    (method.absolute_url(), method.Title())

            if checkPermission(ManageBika, self.context):
                service_uid = service.UID()
                latest = rc.lookupObject(service_uid).version_id
                items[i]['Service'] = service.Title()
                items[i]['class']['Service'] = "service_title"

            # Show version number of out-of-date objects
            # No: This should be done in another column, if at all.
            # The (vX) value confuses some more fragile forms.
            #     if hasattr(obj, 'reference_versions') and \
            #        service_uid in obj.reference_versions and \
            #        latest != obj.reference_versions[service_uid]:
            #         items[i]['after']['Service'] = "(v%s)" % \
            #              (obj.reference_versions[service_uid])

            # choices defined on Service apply to result fields.
            choices = service.getResultOptions()
            if choices:
                items[i]['choices'] = {'Result': choices}

            # permission to view this item's results
            can_view_result = \
                getSecurityManager().checkPermission(ViewResults, obj)

            # permission to edit this item's results
            # Editing Field Results is possible while in Sample Due.
            poc = self.contentFilter.get("getPointOfCapture", 'lab')
            can_edit_analysis = self.allow_edit and context_active and \
                ( (poc == 'field' and getSecurityManager().checkPermission(EditFieldResults, obj))
                  or
                  (poc != 'field' and getSecurityManager().checkPermission(EditResults, obj)) )

            if can_edit_analysis:
                items[i]['allow_edit'] = ['Result', 'Remarks', ]
                # if the Result field is editable, our interim fields are too
                for f in self.interim_fields[obj.UID()]:
                    items[i]['allow_edit'].append(f['keyword'])

                # if there isn't a calculation then result must be re-testable,
                # and if there are interim fields, they too must be re-testable.
                if not items[i]['calculation'] or \
                   (items[i]['calculation'] and self.interim_fields[obj.UID()]):
                    items[i]['allow_edit'].append('retested')

            # Only display data bearing fields if we have ViewResults
            # permission, otherwise just put an icon in Result column.
            if can_view_result:
                items[i]['Result'] = result
                items[i]['formatted_result'] = result
                if result != '':
                    if 'Result' in items[i]['choices'] and items[i]['choices']['Result']:
                        items[i]['formatted_result'] = \
                            [r['ResultText'] for r in items[i]['choices']['Result'] \
                                              if str(r['ResultValue']) == str(result)][0]
                    else:
                        try:
                            items[i]['formatted_result'] = precision and \
                                str("%%.%sf" % precision) % float(result) or result
                        except:
                            items[i]['formatted_result'] = result
                            indet = self.context.translate(_('Indet'))
                            if result == indet:
                                # 'Indeterminate' results flag a specific error
                                Indet = self.context.translate(_("Indeterminate result"))
                                items[i]['after']['Result'] = \
                                    '<img width="16" height="16" title="%s"' % Indet + \
                                    'src="%s/++resource++bika.lims.images/exclamation.png"/>' % \
                                    (self.portal_url)
                            # result being unfloatable is no longer an error.
                            # else:
                            #     # result being un-floatable, is an error.
                            #     msg = self.context.translate(_("Invalid result"))
                            #     items[i]['after']['Result'] = \
                            #         '<img width="16" height="16" title="%s"' % msg + \
                            #         'src="%s/++resource++bika.lims.images/exclamation.png"/>' % \
                            #         (self.portal_url)
                items[i]['Uncertainty'] = obj.getUncertainty(result)

                attachments = ""
                if hasattr(obj, 'getAttachment'):
                    for attachment in obj.getAttachment():
                        af = attachment.getAttachmentFile()
                        icon = af.getBestIcon()
                        attachments += "<span class='attachment' attachment_uid='%s'>" % (attachment.UID())
                        if icon: attachments += "<img src='%s/%s'/>" % (self.portal_url, icon)
                        attachments += '<a href="%s/at_download/AttachmentFile"/>%s</a>' % (attachment.absolute_url(), af.filename)
                        attachments += "<img class='deleteAttachmentButton' attachment_uid='%s' src='%s'/>" % (attachment.UID(), "++resource++bika.lims.images/delete.png")
                        attachments += "</br></span>"
                items[i]['replace']['Attachments'] = attachments[:-12] + "</span>"

                if hasattr(obj, 'result_in_range'):
                    items[i]['result_in_range'] = obj.result_in_range(result, self.chosen_spec)
                else:
                    items[i]['result_in_range'] = (True, None)

            if not can_view_result or \
               (not items[i]['Result'] and not can_edit_analysis):
                if 'Result' in items[i]['allow_edit']:
                    items[i]['allow_edit'].remove('Result')
                items[i]['before']['Result'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/to_follow.png"/>' % \
                    (self.portal_url)

            # Add this analysis' interim fields to the interim_columns list
            for f in self.interim_fields[obj.UID()]:
                if f['keyword'] not in self.interim_columns and not f.get('hidden', False):
                    self.interim_columns[f['keyword']] = f['title']
                # and to the item itself
                items[i][f['keyword']] = f
                items[i]['class'][f['keyword']] = 'interim'

            # check if this analysis is late/overdue
            if items[i]['obj'].portal_type != "DuplicateAnalysis":

                if (not calculation  or (calculation \
                        and not calculation.getDependentServices())):

                    resultdate = obj.aq_parent.getDateSampled() \
                        if obj.portal_type == 'ReferenceAnalysis' \
                        else obj.getResultCaptureDate()

                    duedate = obj.aq_parent.getExpiryDate() \
                        if obj.portal_type == 'ReferenceAnalysis' \
                        else obj.getDueDate()

                    items[i]['replace']['DueDate'] = \
                        self.ulocalized_time(duedate, long_format=1)

                    if items[i]['review_state'] not in ['to_be_sampled',
                                                        'to_be_preserved',
                                                        'sample_due',
                                                        'published']:

                        if (resultdate and resultdate > duedate) \
                            or (not resultdate and DateTime() > duedate):

                            items[i]['replace']['DueDate'] = '%s <img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                                (self.ulocalized_time(duedate, long_format=1),
                                 self.portal_url,
                                 self.context.translate(_("Late Analysis")))

                elif calculation:
                    items[i]['DueDate'] = ''

            # Submitting user may not verify results (admin can though)
            if items[i]['review_state'] == 'to_be_verified' and \
               not checkPermission(VerifyOwnResults, obj):
                user_id = getSecurityManager().getUser().getId()
                self_submitted = False
                review_history = list(workflow.getInfoFor(obj, 'review_history'))
                review_history.reverse()
                for event in review_history:
                    if event.get('action') == 'submit':
                        if event.get('actor') == user_id:
                            self_submitted = True
                        break
                if self_submitted:
                    items[i]['table_row_class'] = "state-submitted-by-current-user"

            # add icon for assigned analyses in AR views
            if self.context.portal_type == 'AnalysisRequest':
                obj = items[i]['obj']
                if obj.portal_type in ['ReferenceAnalysis',
                                       'DuplicateAnalysis'] or \
                   workflow.getInfoFor(obj, 'worksheetanalysis_review_state') == 'assigned':
                    br = obj.getBackReferences('WorksheetAnalysis')
                    if len(br) > 0:
                        ws = br[0]
                        items[i]['after']['state_title'] = \
                             "<a href='%s'><img src='++resource++bika.lims.images/worksheet.png' title='%s'/></a>" % \
                             (ws.absolute_url(), self.context.translate(
                                 _("Assigned to: ${worksheet_id}",
                                   mapping={'worksheet_id':ws.id})))


        # the TAL requires values for all interim fields on all
        # items, so we set blank values in unused cells
        for item in items:
            for field in self.interim_columns:
                if field not in item:
                    item[field] = ''

        # XXX order the list of interim columns
        interim_keys = self.interim_columns.keys()
        interim_keys.reverse()

        # add InterimFields keys to columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {'title': self.interim_columns[col_id],
                                        'input_width': '6',
                                        'input_class': 'ajax_calculate numeric',
                                        'sortable': False}

        if can_edit_analyses:
            new_states = []
            for state in self.review_states:
                # InterimFields are displayed in review_state
                # They are anyway available through View.columns though.
                # In case of hidden fields, the calcs.py should check calcs/services
                # for additional InterimFields!!
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Result') or len(state['columns'])
                for col_id in interim_keys:
                    if col_id not in state['columns']:
                        state['columns'].insert(pos, col_id)
                # retested column is added after Result.
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Uncertainty') + 1 or len(state['columns'])
                state['columns'].insert(pos, 'retested')
                new_states.append(state)
            self.review_states = new_states
            # Allow selecting individual analyses
            self.show_select_column = True

        # Dry Matter.
        # The Dry Matter column is never enabled for reference sample contexts
        # and refers to getReportDryMatter in ARs.
        if items and \
            (hasattr(self.context, 'getReportDryMatter') and \
             self.context.getReportDryMatter()):

            # look through all items
            # if the item's Service supports ReportDryMatter, add getResultDM().
            for item in items:
                if item['obj'].getService().getReportDryMatter():
                    item['ResultDM'] = item['obj'].getResultDM()
                else:
                    item['ResultDM'] = ''
                if item['ResultDM']:
                    item['after']['ResultDM'] = "<em class='discreet'>%</em>"

            # modify the review_states list to include the ResultDM column
            new_states = []
            for state in self.review_states:
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Uncertainty') + 1 or len(state['columns'])
                state['columns'].insert(pos, 'ResultDM')
                new_states.append(state)
            self.review_states = new_states

        self.json_specs = json.dumps(self.specs)
        self.json_interim_fields = json.dumps(self.interim_fields)
        self.items = items

        return items

    def getOutOfRangeAlerts(self):
        """ Declared by bika.lims.interfaces.IAnalysisRangeAlerts
            Returns a dictionary: the keys are the Analysis UIDs and the
            values are another dictionary with the keys 'result', 'icon', 'msg'
        """
        if not self.items:
            self.items = self.folderitems()

        alerts = {}
        for item in self.items:
            obj = item['obj']
            if hasattr(obj, 'isOutOfRange') and obj.isOutOfRange():
                outofrange, acceptable, spec = obj.isOutOfRange()
                if outofrange:
                    rngstr = _("min") + " " + str(spec['min']) + ", " + \
                             _("max") + " " + str(spec['max'])

                    if acceptable:
                        message = _('Result in shoulder range') + " (%s)" % rngstr
                    else:
                        message = _('Result out of range') + ' (%s)' % rngstr

                    alerts[obj.UID()] = {'result': obj.getResult(),
                                         'icon': acceptable and 'warning' or \
                                                'exclamation',
                                         'msg': message}
        return alerts


class QCAnalysesView(AnalysesView):
    """ Renders the table of QC Analyses performed related to an AR. Different
        AR analyses can be achieved inside different worksheets, and each one
        of these can have different QC Analyses. This table only lists the QC
        Analyses performed in those worksheets in which the current AR has, at
        least, one analysis assigned and if the QC analysis services match with
        those from the current AR.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)
        self.columns['getReferenceAnalysesGroupID'] = {'title': _('QC Sample ID'),
                                                       'sortable': False}
        self.columns['Worksheet'] = {'title': _('Worksheet'),
                                                'sortable': False}
        self.review_states[0]['columns'] = ['Service',
                                            'Worksheet',
                                            'getReferenceAnalysesGroupID',
                                            'Partition',
                                            'Method',
                                            'Result',
                                            'Uncertainty',
                                            'CaptureDate',
                                            'DueDate',
                                            'state_title']

        qcanalyses = context.getQCAnalyses()
        asuids = [an.UID() for an in qcanalyses]
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'UID': asuids,
                              'sort_on': 'sortable_title'}
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/referencesample.png"

    def folderitems(self):
        items = AnalysesView.folderitems(self)
        # Group items by RefSample - Worksheet - Position
        for i in range(len(items)):
            obj = items[i]['obj']
            wss = obj.getBackReferences('WorksheetAnalysis')
            wsid = wss[0].id if wss and len(wss) > 0 else ''
            wshref = wss[0].absolute_url() if wss and len(wss) > 0 else None
            if wshref:
                items[i]['replace']['Worksheet'] = "<a href='%s'>%s</a>" % (wshref, wsid)

            imgtype = ""
            if obj.portal_type == 'ReferenceAnalysis':
                antype = QCANALYSIS_TYPES.getValue(obj.getReferenceType())
                if obj.getReferenceType() == 'c':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/control.png'/>&nbsp;" % (antype, self.context.absolute_url())
                if obj.getReferenceType() == 'b':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/blank.png'/>&nbsp;" % (antype, self.context.absolute_url())
                items[i]['replace']['Partition'] = "<a href='%s'>%s</a>" % (obj.aq_parent.absolute_url(), obj.aq_parent.id)
            elif obj.portal_type == 'DuplicateAnalysis':
                antype = QCANALYSIS_TYPES.getValue('d')
                imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>&nbsp;" % (antype, self.context.absolute_url())                
                items[i]['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getService().getKeyword())

            items[i]['before']['Service'] = imgtype
            items[i]['sortcode'] = '%s_%s' % (obj.getReferenceAnalysesGroupID(),
                                              obj.getService().getKeyword())

        # Sort items
        items = sorted(items, key = itemgetter('sortcode'))
        return items
