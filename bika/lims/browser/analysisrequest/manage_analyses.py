from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.sample import SamplePartitionsView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.permissions import *
from bika.lims.utils import logged_in_client
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales
from zope.interface import implements

import json
import plone

class AnalysisRequestAnalysesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    template = ViewPageTemplateFile("templates/analysisrequest_analyses.pt")

    def __init__(self, context, request):
        super(AnalysisRequestAnalysesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active', }
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.title = self.context.Title()
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.table_only = True
        self.show_select_all_checkbox = False
        self.pagesize = 999999

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False, },
            'Hidden': {'title': _('Hidden'),
                       'sortable': False,
                       'type': 'boolean', },
            'Price': {'title': _('Price'),
                      'sortable': False, },
            'Priority': {'title': _('Priority'),
                         'sortable': False,
                         'index': 'Priority',
                         'toggle': True },
            'Partition': {'title': _('Partition'),
                          'sortable': False, },
            'min': {'title': _('Min')},
            'max': {'title': _('Max')},
            'error': {'title': _('Permitted Error %')},
        }

        columns = ['Title', 'Hidden', ]
        ShowPrices = self.context.bika_setup.getShowPrices()
        if ShowPrices:
            columns.append('Price')
            columns.append('Priority')
        ShowPartitions = self.context.bika_setup.getShowPartitions()
        if ShowPartitions:
            columns.append('Partition')
        EnableARSpecs = self.context.bika_setup.getEnableARSpecs()
        if EnableARSpecs:
            columns.append('min')
            columns.append('max')
            columns.append('error')

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': columns,
             'transitions': [{'id': 'empty'}, ],  # none
             'custom_actions': [{'id': 'save_analyses_button',
                                 'title': _('Save')}, ],
             },
        ]

        # Create Partitions View for this ARs sample
        sample = self.context.getSample()
        p = SamplePartitionsView(sample, self.request)
        p.table_only = True
        p.allow_edit = False
        p.form_id = "parts"
        p.show_select_column = False
        p.show_table_footer = False
        p.review_states[0]['transitions'] = [{'id': 'empty'}, ]  # none
        p.review_states[0]['custom_actions'] = []
        p.review_states[0]['columns'] = ['PartTitle',
                                         'getContainer',
                                         'getPreservation',
                                         'state_title']

        self.parts = p.contents_table()

    def getResultsRange(self):
        """Return the AR Specs sorted by Service UID, so that the JS can
        work easily with the values.
        """
        bsc = self.bika_setup_catalog
        rr_dict_by_service_uid = {}
        rr = self.context.getResultsRange()
        for r in rr:
            keyword = r['keyword']
            try:
                service_uid = bsc(portal_type='AnalysisService',
                                  getKeyword=keyword)[0].UID
                rr_dict_by_service_uid[service_uid] = r
            except IndexError:
                from bika.lims import logger
                error = "No Analysis Service found for Keyword '%s'. "\
                        "Related: LIMS-1614"
                logger.exception(error, keyword)

        return json.dumps(rr_dict_by_service_uid)

    def get_spec_from_ar(self, ar, keyword):
        empty = {'min': '', 'max': '', 'error': '', 'keyword':keyword}
        spec = ar.getResultsRange()
        if spec:
            return dicts_to_dict(spec, 'keyword').get(keyword, empty)
        return empty

    def folderitems(self):
        self.categories = []

        analyses = self.context.getAnalyses(full_objects=True)
        self.analyses = dict([(a.getServiceUID(), a) for a in analyses])
        self.selected = self.analyses.keys()
        self.show_categories = \
            self.context.bika_setup.getCategoriseAnalysisServices()
        self.expand_all_categories = False

        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')

        self.allow_edit = mtool.checkPermission('Modify portal content',
                                                self.context)

        items = BikaListingView.folderitems(self)
        analyses = self.context.getAnalyses(full_objects=True)

        parts = self.context.getSample().objectValues('SamplePartition')
        partitions = [{'ResultValue': o.Title(),
                       'ResultText': o.getId()}
                      for o in parts
                      if wf.getInfoFor(o, 'cancellation_state', '') == 'active']
        for x in range(len(items)):
            if not 'obj' in items[x]:
                continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            items[x]['selected'] = items[x]['uid'] in self.selected

            items[x]['class']['Title'] = 'service_title'

            # js checks in row_data if an analysis may be removed.
            row_data = {}
            # keyword = obj.getKeyword()
            # if keyword in review_states.keys() \
            #    and review_states[keyword] not in ['sample_due',
            #                                       'to_be_sampled',
            #                                       'to_be_preserved',
            #                                       'sample_received',
            #                                       ]:
            #     row_data['disabled'] = True
            items[x]['row_data'] = json.dumps(row_data)

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['before']['Price'] = symbol
            items[x]['Price'] = obj.getPrice()
            items[x]['class']['Price'] = 'nowrap'
            items[x]['Priority'] = ''

            if items[x]['selected']:
                items[x]['allow_edit'] = ['Partition', 'min', 'max', 'error']
                if not logged_in_client(self.context):
                    items[x]['allow_edit'].append('Price')

            items[x]['required'].append('Partition')
            items[x]['choices']['Partition'] = partitions

            if obj.UID() in self.analyses:
                analysis = self.analyses[obj.UID()]
                part = analysis.getSamplePartition()
                part = part and part or obj
                items[x]['Partition'] = part.Title()
                spec = self.get_spec_from_ar(self.context,
                                             analysis.getService().getKeyword())
                items[x]["min"] = spec["min"]
                items[x]["max"] = spec["max"]
                items[x]["error"] = spec["error"]
                # Add priority premium
                items[x]['Price'] = analysis.getPrice()
                priority = analysis.getPriority()
                items[x]['Priority'] = priority and priority.Title() or ''
            else:
                items[x]['Partition'] = ''
                items[x]["min"] = ''
                items[x]["max"] = ''
                items[x]["error"] = ''
                items[x]["Priority"] = ''

            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>" % (
                    self.portal_url,
                    t(_("Accredited"))
                )
            if obj.getReportDryMatter():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/dry.png'\
                title='%s'>" % (
                    self.portal_url,
                    t(_("Can be reported as dry matter"))
                )
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>" % (
                    self.portal_url,
                    t(_("Attachment required"))
                )
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>" % (
                    self.portal_url,
                    t(_('Attachment not permitted'))
                )
            if after_icons:
                items[x]['after']['Title'] = after_icons


            # Display analyses for this Analysis Service in results?
            ser = self.context.getAnalysisServiceSettings(obj.UID())
            items[x]['allow_edit'] = ['Hidden', ]
            items[x]['Hidden'] = ser.get('hidden', obj.getHidden())

        self.categories.sort()
        return items
