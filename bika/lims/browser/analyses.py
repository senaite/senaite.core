# coding=utf-8
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import ManageResults, ViewResults, EditResults
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive, TimeOrDate
from bika.lims.config import POINTS_OF_CAPTURE
from decimal import Decimal
from operator import itemgetter
from zope.component import getMultiAdapter
from zope.interface import implements, 	alsoProvides, implementsOnly
import json
import plone
 
class AnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        All InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to portal_catalog.
    """
    def __init__(self, context, request, **kwargs):
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.content_add_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        request.set('disable_plone.rightcolumn',1);
        self.pagesize = 1000

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = {
            'Service': {'title': _('Analysis')},
            'state_title': {'title': _('Status')},
            'Result': {'title': _('Result')},
            'Uncertainty': {'title': _('+-')},
            'retested': {'title': _('retested'),
                         'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'DueDate': {'title': _('Due Date')},
        }

        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns':['Service',
                        'Result',
                        'Uncertainty',
                        'DueDate',
                        'state_title',
                        'Attachments'],
             },
        ]
        self.chosen_spec = request.get('specification', 'lab')
        super(AnalysesView, self).__init__(context, request)

    def folderitems(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        pc = getToolByName(self.context, 'portal_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()

        can_edit_analyses = self.allow_edit and \
            getSecurityManager().checkPermission(ManageResults, self.context)

        context_active = True
        if not isActive(self.context):
            context_active = False

        items = super(AnalysesView, self).folderitems(full_objects = True)

        self.interim_fields = {}
        self.interim_columns = {}
        self.specs = {}
        for i, item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']

            result = obj.getResult()
            service = obj.getService()
            calculation = service.getCalculation()
            unit = service.getUnit()
            keyword = service.getKeyword()
            precision = service.getPrecision()

            items[i]['Keyword'] = keyword
            items[i]['Unit'] = unit and unit or ''
            items[i]['Result'] = ''
            items[i]['formatted_result'] = ''
            items[i]['Uncertainty'] = ''
            items[i]['retested'] = obj.getRetested()
            items[i]['class']['retested'] = 'center'
            items[i]['calculation'] = calculation and True or False
            items[i]['DueDate'] = obj.getDueDate()
            items[i]['Attachments'] = ''

            self.interim_fields[obj.UID()] = obj.getInterimFields()

            # calculate specs
            if obj.portal_type == 'ReferenceAnalysis':
                items[i]['st_uid'] = obj.aq_parent.UID()
            else:
                if self.context.portal_type == 'AnalysisRequest':
                    sample = self.context.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = pc(portal_type = 'AnalysisSpec',
                                     getSampleTypeUID = st_uid)
                elif self.context.portal_type == "Worksheet":
                    if obj.portal_type == "DuplicateAnalysis":
                        sample = obj.getAnalysis().getSample()
                    else:
                        sample = obj.aq_parent.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = pc(portal_type = 'AnalysisSpec',
                                     getSampleTypeUID = st_uid)
                else:
                    proxies = []
                if st_uid not in self.specs:
                    for spec in (p.getObject() for p in proxies):
                        client_or_lab = ""
                        if spec.getClientUID() == obj.aq_parent.UID():
                            client_or_lab = 'client'
                        elif spec.getClientUID() == None:
                            client_or_lab = 'lab'
                        else:
                            continue
                        for keyword, results_range in \
                            spec.getResultsRangeDict().items():
                            # hidden form field 'specs' keyed by sampletype uid:
                            # {st_uid: {'lab/client':{keyword:{min,max,error}}}}
                            if st_uid in self.specs and \
                               client_or_lab in self.specs[st_uid]:
                                    self.specs[st_uid][client_or_lab][keyword] = results_range
                            else:
                                self.specs[st_uid] = {client_or_lab: {keyword: results_range}}

            # if the reference version is older than the object itself,
            # insert the version number of referenced service after Title
            service_uid = service.UID()
            latest_service = rc.lookupObject(service_uid)
            items[i]['Service'] = service.Title()
            if hasattr(obj, 'reference_versions') and \
               service_uid in obj.reference_versions and \
               latest_service.version_id != obj.reference_versions[service_uid]:
                items[i]['after']['Service'] = "(v%s)" % \
                     (obj.reference_versions[service_uid])

            # choices defined on Service apply to result fields.
            choices = service.getResultOptions()
            if choices:
                items[i]['choices'] = {'Result': choices}

            # permission to view this item's results
            can_view_result = \
                getSecurityManager().checkPermission(ViewResults, obj)

            # permission to edit this item's results
            can_edit_analysis = self.allow_edit and context_active and \
                getSecurityManager().checkPermission(EditResults, obj)

            if can_edit_analysis:
                items[i]['allow_edit'] = ['Result', ]
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
                                              if r['ResultValue'] == result][0]
                    else:
                        items[i]['formatted_result'] = precision and \
                            str("%%.%sf" % precision) % float(result) or result
                items[i]['Uncertainty'] = obj.getUncertainty(result)

                attachments = ""
                if hasattr(obj, 'getAttachment'):
                    for attachment in obj.getAttachment():
                        af = attachment.getAttachmentFile()
                        icon = af.getBestIcon()
                        attachments += "<span class='attachment' id='%s'>" % (attachment.id)
                        if icon: attachments += "<img src='%s/%s'/>" % (portal.absolute_url(), icon)
                        attachments += '<a href="%s/at_download/AttachmentFile"/>%s</a>' % (attachment.absolute_url(), af.filename)
                        attachments += "<img class='deleteAttachmentButton' attachment_id='%s' src='%s'/>" % (attachment.id, "++resource++bika.lims.images/delete.png")
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
                    (portal.absolute_url())

            # Add this analysis' interim fields to the interim_columns list
            for f in self.interim_fields[obj.UID()]:
                if f['keyword'] not in self.interim_columns:
                    self.interim_columns[f['keyword']] = f['title']
                # and to the item itself
                items[i][f['keyword']] = f
                items[i]['class'][f['keyword']] = 'interim'

            # check if this analysis is late/overdue
            if items[i]['obj'].portal_type != "DuplicateAnalysis":
                if (not calculation or (calculation and not calculation.getDependentServices())) and \
                   items[i]['review_state'] not in ['sample_due', 'published'] and \
                   items[i]['DueDate'] < DateTime():
                    DueDate = TimeOrDate(self.context, item['DueDate'], long_format = 1)
                    if self.context.portal_type == 'AnalysisRequest':
                        items[i]['replace']['DueDate'] = '%s <img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                            (DueDate, portal.absolute_url(), _("Due Date: ") + DueDate)
                    else:
                        items[i]['replace']['DueDate'] = '%s <img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                            (DueDate, portal.absolute_url(), _("Late analysis"))
                else:
                    items[i]['replace']['DueDate'] = TimeOrDate(self.context, item['DueDate'])

            # add icon for assigned analyses in AR views
            if self.context.portal_type == 'AnalysisRequest' and \
               workflow.getInfoFor(items[i]['obj'], 'worksheetanalysis_review_state') == 'assigned':
                ws = items[i]['obj'].getBackReferences('WorksheetAnalysis')[0]
                items[i]['after']['state_title'] = \
                     "<a href='%s'><img src='++resource++bika.lims.images/worksheet.png' title='Assigned: %s'/></a>" % \
                     (ws.absolute_url(), ws.id)

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
                self.columns[col_id] = {'title': self.interim_columns[col_id]}

        if can_edit_analyses:
            new_states = []
            for state in self.review_states:
                # InterimFields are displayed in review_state
                # They are anyway available through View.columns though.
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Result') or len(state['columns'])
                for col_id in interim_keys:
                    if col_id not in state['columns']:
                        state['columns'].insert(pos, col_id)
                # retested column is added after Result.
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Result') + 1 or len(state['columns'])
                state['columns'].insert(pos, 'retested')
                new_states.append(state)
            self.review_states = new_states
            # Allow selecting individual analyses
            self.show_select_column = True

        items = sorted(items, key = itemgetter('Service'))
        self.json_specs = json.dumps(self.specs)
        self.json_interim_fields = json.dumps(self.interim_fields)

        return items
