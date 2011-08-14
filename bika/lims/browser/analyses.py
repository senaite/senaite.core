from AccessControl import getSecurityManager, Unauthorized
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import EditAnalyses, ViewResults
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import POINTS_OF_CAPTURE
from decimal import Decimal
from operator import itemgetter
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import implements,	alsoProvides, implementsOnly
import json
import plone

class AnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        All InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to portal_catalog.
    """
    def __init__(self, context, request, **kwargs):
        super(AnalysesView, self).__init__(context, request)
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.content_add_actions = {}
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False
        self.pagesize = 1000

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

    def folderitems(self):
        analyses = super(AnalysesView, self).folderitems(full_objects = True)

        portal = getSite()

        pc = getToolByName(self.context, 'portal_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')

        can_edit_analyses = self.allow_edit and \
            getSecurityManager().checkPermission(EditAnalyses, self.context)

        items = []
        self.interim_fields = {}
        for i, item in enumerate(analyses):
            if not item.has_key('obj'): continue
            # self.contentsMethod may return brains or objects.
            if hasattr(item['obj'], 'getObject'):
                obj = item['obj'].getObject()
            else:
                obj = item['obj']

            # calculate specs - they are stored in an attribute on each row
            # so that selecting lab/client ranges can re-calculate in javascript
            # calculate specs for every analysis, since they may
            # all be for different sample types
             # worksheet.  XXX Should be like a generalized review_state_filter
            specs = {'client':{}, 'lab':{}}
            if obj.portal_type != 'ReferenceAnalysis':
                if self.context.portal_type == 'AnalysisRequest':
                    sample = self.context.getSample()
                    proxies = pc(portal_type = 'AnalysisSpec',
                        getSampleTypeUID = sample.getSampleType().UID())
                else:
                    sample = obj.aq_parent.getSample()
                    proxies = pc(portal_type = 'AnalysisSpec',
                        getSampleTypeUID = sample.getSampleType().UID())
                for spec in proxies:
                    spec = spec.getObject()
                    client_or_lab = ""
                    if spec.getClientUID() == self.context.getClientUID():
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
            item['specs'] = json.dumps(
                {'client': specs['client'].has_key(keyword) and \
                           specs['client'][keyword] or [],
                 'lab': specs['lab'].has_key(keyword) and \
                        specs['lab'][keyword] or [],
                 }
            )
            item['interim_fields'] = obj.getInterimFields()
            item['Service'] = service.Title()
            item['Keyword'] = keyword
            item['Unit'] = obj.getUnit()
            item['Result'] = ''
            item['formatted_result'] = ''
            item['Uncertainty'] = ''
            item['retested'] = obj.getRetested()
            item['class']['retested'] = 'center'
            calculation = service.getCalculation()
            item['calculation'] = calculation and True or False
            item['DueDate'] = obj.getDueDate()
            item['Attachments'] = ''
            item['item_data'] = json.dumps(item['interim_fields'])
            # choices defined on Service apply result fields.
            choices = service.getResultOptions()
            if choices:
                item['choices']['Result'] = choices
            # Results can only be edited in certain states.
            can_view_result = \
                getSecurityManager().checkPermission(ViewResults, obj)
            can_edit_analysis = self.allow_edit and \
                getSecurityManager().checkPermission(EditAnalyses, obj) and \
                item['review_state'] in ('sample_received', 'assigned')
            if can_edit_analysis:
                item['allow_edit'] = ['Result',]
                # if the Result field is editable, our interim fields are too
                for f in item['interim_fields']:
                    item['allow_edit'].append(f['id'])

                # if there isn't a calculation then result must be re-testable,
                # and if there are interim fields, they too must be re-testable.
                if not item['calculation'] or \
                   (item['calculation'] and item['interim_fields']):
                    item['allow_edit'].append('retested')

            # Only display data bearing fields if we have ViewResults
            # permission, otherwise just put an icon in Result column.
            if can_view_result:
                item['Result'] = result
                item['formatted_result'] = precision and result and \
                    str("%%.%sf" % precision) % float(result) or result
                item['Uncertainty'] = obj.getUncertainty(result)

                attachments = ""
                if hasattr(obj, 'getAttachment'):
                    for attachment in obj.getAttachment():
                        af = attachment.getAttachmentFile()
                        icon = af.getBestIcon()
                        if icon:
                            attachments += "<img src='%s/%s'/>"%\
                                        (portal.absolute_url(), icon)
                        attachments += \
                            '<a href="%s/at_download/AttachmentFile"/>%s</a>'%\
                            (attachment.absolute_url(), af.filename)
                item['replace']['Attachments'] = attachments

                item['result_in_range'] = hasattr(obj, 'result_in_range') and \
                    obj.result_in_range(result) or True

            if not can_view_result or \
               (not item['Result'] and not can_edit_analysis):
                if 'Result' in item['allow_edit']:
                    item['allow_edit'].remove('Result')
                item['before']['Result'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/to_follow.png"/>'% \
                    (portal.absolute_url())

            # Add this analysis' interim fields to the list
            for f in item['interim_fields']:
                if f['id'] not in self.interim_fields.keys():
                    self.interim_fields[f['id']] = f['title']
                # and to the item itself
                item[f['id']] = f

            # check if this analysis is late/overdue
            if (not calculation or (calculation and not calculation.getDependentServices())) and \
               item['review_state'] not in ['sample_due', 'published'] and \
               item['DueDate'] < DateTime():
                DueDate = self.context.toLocalizedTime(
                    item['DueDate'], long_format = 1)
                item['after']['Service'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/late.png" title="%s"/>'% \
                    (portal.absolute_url(), _("Due Date: ") + DueDate)

            items.append(item)

        # the TAL is lazy, it requires blank values for
        # all interim fields on all items, so we loop
        # through the list and fill in the blanks
        for item in items:
            for field in self.interim_fields:
                if field not in item:
                    item[field] = ''

        items = sorted(items, key=itemgetter('Service'))

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
                    state['columns'].index('Result')+1 or len(state['columns'])
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
