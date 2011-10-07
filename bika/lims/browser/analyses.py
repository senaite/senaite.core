# coding=utf-8
from AccessControl import getSecurityManager, Unauthorized
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
from zope.app.component.hooks import getSite
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
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
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
                        'state_title',
                        'Attachments'],
             },
        ]
        super(AnalysesView, self).__init__(context, request)

    def folderitems(self):
        rc = getToolByName(self.context, 'reference_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')
        portal = getSite()

        can_edit_analyses = self.allow_edit and \
            getSecurityManager().checkPermission(ManageResults, self.context)

        context_active = True
        if not isActive(self.context):
            context_active = False

        items = super(AnalysesView, self).folderitems(full_objects = True)

        self.interim_fields = {}
        for i, item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']

            # calculate specs - they are stored in an attribute on each row
            # so that selecting lab/client ranges can re-calculate in javascript
            # calculate specs for every analysis, since they may
            # all be for different sample types (worksheet manage results)
            specs = {'client':{}, 'lab':{}}
            if obj.portal_type != 'ReferenceAnalysis':
                if self.context.portal_type == 'AnalysisRequest':
                    sample = self.context.getSample()
                    proxies = pc(portal_type = 'AnalysisSpec',
                        getSampleTypeUID = sample.getSampleType().UID())
                elif self.context.portal_type == "Worksheet":
                    if obj.portal_type == "DuplicateAnalysis":
                        sample = obj.getAnalysis().getSample()
                    else:
                        sample = obj.aq_parent.getSample()
                    proxies = pc(portal_type = 'AnalysisSpec',
                        getSampleTypeUID = sample.getSampleType().UID())
                else:
                    proxies = []
                brains = (p.getObject() for p in proxies)
                for spec in brains:
                    client_or_lab = ""
                    if spec.getClientUID() == obj.aq_parent.UID():
                        client_or_lab = 'client'
                    elif spec.getClientUID() == None:
                        client_or_lab = 'lab'
                    else:
                        continue
                    for keyword, results_range in \
                        spec.getResultsRangeDict().items():
                        specs[client_or_lab][keyword] = results_range

            result = obj.getResult()
            service = obj.getService()
            keyword = service.getKeyword()
            precision = service.getPrecision()
            items[i]['specs'] = json.dumps(
                {'client': specs['client'].has_key(keyword) and \
                 specs['client'][keyword] or [],
                 'lab': specs['lab'].has_key(keyword) and \
                 specs['lab'][keyword] or [],
                 }
            )
            items[i]['interim_fields'] = obj.getInterimFields()
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
            items[i]['Keyword'] = keyword
            unit = service.getUnit()
            items[i]['Unit'] = unit and unit or ''
            items[i]['Result'] = ''
            items[i]['formatted_result'] = ''
            items[i]['Uncertainty'] = ''
            items[i]['retested'] = obj.getRetested()
            items[i]['class']['retested'] = 'center'
            calculation = service.getCalculation()
            items[i]['calculation'] = calculation and True or False
            items[i]['DueDate'] = obj.getDueDate()
            items[i]['Attachments'] = ''
            items[i]['item_data'] = json.dumps(item['interim_fields'])
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
                for f in items[i]['interim_fields']:
                    items[i]['allow_edit'].append(f['keyword'])

                # if there isn't a calculation then result must be re-testable,
                # and if there are interim fields, they too must be re-testable.
                if not items[i]['calculation'] or \
                   (items[i]['calculation'] and items[i]['interim_fields']):
                    items[i]['allow_edit'].append('retested')

            # Only display data bearing fields if we have ViewResults
            # permission, otherwise just put an icon in Result column.
            if can_view_result:
                items[i]['Result'] = result
                items[i]['formatted_result'] = precision and result and \
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
                    items[i]['result_in_range'] = obj.result_in_range(result)
                else:
                     items[i]['result_in_range'] = True


            if not can_view_result or \
               (not items[i]['Result'] and not can_edit_analysis):
                if 'Result' in items[i]['allow_edit']:
                    items[i]['allow_edit'].remove('Result')
                items[i]['before']['Result'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/to_follow.png"/>' % \
                    (portal.absolute_url())

            # Add this analysis' interim fields to the list
            for f in items[i]['interim_fields']:
                if f['keyword'] not in self.interim_fields.keys():
                    self.interim_fields[f['keyword']] = f['title']
                # and to the item itself
                items[i][f['keyword']] = f

            # check if this analysis is late/overdue
            if items[i]['obj'].portal_type != "DuplicateAnalysis":
                if (not calculation or (calculation and not calculation.getDependentServices())) and \
                   items[i]['review_state'] not in ['sample_due', 'published'] and \
                   items[i]['DueDate'] < DateTime():
                    DueDate = TimeOrDate(self.context, item['DueDate'], long_format = 1)
                    items[i]['after']['DueDate'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                        (portal.absolute_url(), _("Due Date: ") + DueDate)
                else:
                    items[i]['DueDate'] = TimeOrDate(self.context, item['DueDate'])
            # add icon for assigned analyses in AR views
            if self.context.portal_type == 'AnalysisRequest' and \
               workflow.getInfoFor(items[i]['obj'], 'worksheetanalysis_review_state') == 'assigned':
                ws = items[i]['obj'].getBackReferences('WorksheetAnalysis')[0]
                items[i]['after']['state_title'] = \
                     "<a href='%s'><img src='++resource++bika.lims.images/worksheet.png' title='Assigned to worksheet: %s'/></a>" % \
                     (ws.absolute_url(), ws.id)

        # the TAL is lazy, it requires blank values for
        # all interim fields on all items, so we loop
        # through the list and fill in the blanks
        for item in items:
            for field in self.interim_fields:
                if field not in item:
                    item[field] = ''

        items = sorted(items, key = itemgetter('Service'))

        # XXX order the list of interim columns
        interim_keys = self.interim_fields.keys()
        interim_keys.reverse()

        # add InterimFields keys to columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {'title': self.interim_fields[col_id]}

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

        # re-do the pretty css odd/even classes
        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "draggable even" or "draggable odd"

        return items
