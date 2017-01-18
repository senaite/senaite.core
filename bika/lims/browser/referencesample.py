# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import getSecurityManager
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive
from bika.lims.browser.analyses import AnalysesView
from datetime import datetime
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATContentTypes.utils import DT2dt
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements
import json, plone

class ViewView(BrowserView):
    """ Reference Sample View
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/referencesample_view.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/referencesample_big.png"

    def __call__(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        self.results = {} # {category_title: listofdicts}
        for r in self.context.getReferenceResults():
            service = rc.lookupObject(r['uid'])
            cat = service.getCategoryTitle()
            if cat not in self.results:
                self.results[cat] = []
            r['service'] = service
            self.results[cat].append(r)
        self.categories = self.results.keys()
        self.categories.sort()
        return self.template()


class ReferenceAnalysesViewView(BrowserView):
    """ View of Reference Analyses linked to the Reference Sample.
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/referencesample_analyses.pt")

    def __init__(self, context, request):
        super(ReferenceAnalysesViewView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/referencesample_big.png"
        self.title = self.context.translate(_("Reference Analyses"))
        self.description = ""
        self._analysesview = None

    def __call__(self):
        return self.template()

    def get_analyses_table(self):
        """ Returns the table of Reference Analyses
        """
        return self.get_analyses_view().contents_table()

    def get_analyses_view(self):
        if not self._analysesview:
            # Creates the Analyses View if not exists yet
            self._analysesview = ReferenceAnalysesView(self.context,
                                    self.request)
            self._analysesview.allow_edit = False
            self._analysesview.show_select_column = False
            self._analysesview.show_workflow_action_buttons = False
            self._analysesview.form_id = "%s_qcanalyses" % self.context.UID()
            self._analysesview.review_states[0]['transitions'] = [{}]
        return self._analysesview

    def getReferenceSampleId(self):
        return self.context.id;

    def get_analyses_json(self):
        return self.get_analyses_view().get_analyses_json()

class ReferenceAnalysesView(AnalysesView):
    """ Reference Analyses on this sample
    """
    implements(IViewView)

    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'portal_type':'ReferenceAnalysis',
                              'path': {'query':"/".join(self.context.getPhysicalPath()),
                                       'level':0}}
        self.show_select_row = False
        self.show_sort_column = False
        self.show_select_column = False
        self.allow_edit = False

        self.columns = {
            'id': {'title': _('ID'), 'toggle':False},
            'getReferenceAnalysesGroupID': {'title': _('QC Sample ID'), 'toggle': True},
            'Category': {'title': _('Category'), 'toggle': True},
            'Service': {'title': _('Service'), 'toggle':True},
            'Worksheet': {'title': _('Worksheet'), 'toggle':True},
            'Method': {
                'title': _('Method'),
                'sortable': False,
                'toggle': True},
            'Instrument': {
                'title': _('Instrument'),
                'sortable': False,
                'toggle': True},
            'Result': {'title': _('Result'), 'toggle':True},
            'Captured': {'title': _('Captured'), 'toggle':True},
            'Uncertainty': {'title': _('+-'), 'toggle':True},
            'DueDate': {'title': _('Due Date'),
                        'index': 'getDueDate',
                        'toggle':True},
            'retested': {'title': _('Retested'), 'type':'boolean', 'toggle':True},
            'state_title': {'title': _('State'), 'toggle':True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['id',
                        'getReferenceAnalysesGroupID',
                        'Category',
                        'Service',
                        'Worksheet',
                        'Method',
                        'Instrument',
                        'Result',
                        'Captured',
                        'Uncertainty',
                        'DueDate',
                        'state_title'],
             },
        ]
        self.anjson = {}

    def isItemAllowed(self, obj):
        allowed = super(ReferenceAnalysesView, self).isItemAllowed(obj)
        return allowed if not allowed else obj.getResult() != ''

    def folderitem(self, obj, item, index):
        item = super(ReferenceAnalysesView, self).folderitem(obj, item, index)
        if not item:
            return None
        service = obj.getService()
        item['Category'] = service.getCategoryTitle()
        item['Service'] = service.Title()
        item['Captured'] = self.ulocalized_time(obj.getResultCaptureDate())
        brefs = obj.getBackReferences("WorksheetAnalysis")
        item['Worksheet'] = brefs and brefs[0].Title() or ''

        self.addToJSON(obj, service, item)

    def addToJSON(self, analysis, service, item):
        """ Adds an analysis item to the self.anjson dict that will be used
            after the page is rendered to generate a QC Chart
        """
        parent = analysis.aq_parent
        qcid = parent.id
        serviceref = "%s (%s)" % (item['Service'], item['Keyword'])
        trows = self.anjson.get(serviceref, {})
        anrows = trows.get(qcid, [])
        anid = '%s.%s' % (item['getReferenceAnalysesGroupID'], item['id'])
        rr = parent.getResultsRangeDict()
        uid = service.UID()
        if uid in rr:
            specs = rr.get(uid, None)
            try:
                smin = float(specs.get('min', 0))
                smax = float(specs.get('max', 0))
                error = float(specs.get('error', 0))
                target = float(specs.get('result', 0))
                result = float(item['Result'])
                error_amount = ((target / 100) * error) if target > 0 else 0
                upper = smax + error_amount
                lower = smin - error_amount

                anrow = {'date': item['CaptureDate'],
                         'min': smin,
                         'max': smax,
                         'target': target,
                         'error': error,
                         'erroramount': error_amount,
                         'upper': upper,
                         'lower': lower,
                         'result': result,
                         'unit': item['Unit'],
                         'id': item['uid']}
                anrows.append(anrow)
                trows[qcid] = anrows
                self.anjson[serviceref] = trows
            except:
                pass

    def get_analyses_json(self):
        return json.dumps(self.anjson)


class ReferenceResultsView(BikaListingView):
    """
    """
    def __init__(self, context, request):
        super(ReferenceResultsView, self).__init__(context, request)
        bsc = getToolByName(context, 'bika_setup_catalog')
        self.title = self.context.translate(_("Reference Values"))
        self.description = self.context.translate(_(
                             "Click on Analysis Categories (against shaded background) "
                             "to see Analysis Services in each category. Enter minimum "
                             "and maximum values to indicate a valid results range. "
                             "Any result outside this range will raise an alert. "
                             "The % Error field allows for an % uncertainty to be "
                             "considered when evaluating results against minimum and "
                             "maximum values. A result out of range but still in range "
                             "if the % error is taken into consideration, will raise a "
                             "less severe alert."))
        self.contentFilter = {}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_workflow_action_buttons = False
        self.show_select_column = False
        self.pagesize = 999999

        self.columns = {
            'Service': {'title': _('Service')},
            'result': {'title': _('Result')},
            'min': {'title': _('Min')},
            'max': {'title': _('Max')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Service',
                         'result',
                         'min',
                         'max']},
        ]

    def folderitems(self):
        items = []
        uc = getToolByName(self.context, 'uid_catalog')
        # not using <self.contentsMethod=bsc>
        for x in self.context.getReferenceResults():
            service = uc(UID=x['uid'])[0].getObject()
            item = {
                'obj': self.context,
                'id': x['uid'],
                'uid': x['uid'],
                'result': x['result'],
                'min': x['min'],
                'max': x['max'],
                'title': service.Title(),
                'Service': service.Title(),
                'type_class': 'contenttype-ReferenceResult',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': self.context.absolute_url() + "/results",
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
            }
            item['replace']['Service'] = "<a href='%s'>%s</a>" % \
                (service.absolute_url(), service.Title())
            items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        return items

class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """
    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        self.icon = self.portal_url + "/++resource++bika.lims.images/referencesample_big.png"
        self.title = self.context.translate(_("Reference Samples"))
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path':{"query": ["/"], "level" : 0 }, }
        self.context_actions = {}
        self.show_select_column = True
        request.set('disable_border', 1)

        self.columns = {
            'ID': {
                'title': _('ID'),
                'index': 'id'},
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title',
                'toggle':True},
            'Supplier': {
                'title': _('Supplier'),
                'toggle':True,
                'attr': 'aq_parent.Title',
                'replace_url': 'aq_parent.absolute_url'},
            'Manufacturer': {
                'title': _('Manufacturer'),
                'toggle': True,
                'attr': 'getManufacturer.Title',
                'replace_url': 'getManufacturer.absolute_url'},
            'Definition': {
                'title': _('Reference Definition'),
                'toggle':True,
                'attr': 'getReferenceDefinition.Title',
                'replace_url': 'getReferenceDefinition.absolute_url'},
            'DateSampled': {
                'title': _('Date Sampled'),
                'index': 'getDateSampled',
                'toggle':True},
            'DateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived',
                'toggle':True},
            'DateOpened': {
                'title': _('Date Opened'),
                'toggle':True},
            'ExpiryDate': {
                'title': _('Expiry Date'),
                'index': 'getExpiryDate',
                'toggle':True},
            'state_title': {
                'title': _('State'),
                'toggle':True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Current'),
             'contentFilter':{'review_state':'current'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'expired',
             'title': _('Expired'),
             'contentFilter':{'review_state':'expired'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'disposed',
             'title': _('Disposed'),
             'contentFilter':{'review_state':'disposed'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate',
                         'state_title']},
        ]

    def folderitem(self, obj, item, index):
        if item.get('review_state', 'current') == 'current':
            # Check expiry date
            exdate = obj.getExpiryDate()
            if exdate:
                expirydate = DT2dt(exdate).replace(tzinfo=None)
                if (datetime.today() > expirydate):
                    # Trigger expiration
                    workflow.doActionFor(obj, 'expire')
                    item['review_state'] = 'expired'
                    item['obj'] = obj

        if self.contentFilter.get('review_state', '') \
           and item.get('review_state', '') == 'expired':
            # This item must be omitted from the list
            return None

        item['ID'] = obj.id
        item['DateSampled'] = self.ulocalized_time(obj.getDateSampled(), long_format=True)
        item['DateReceived'] = self.ulocalized_time(obj.getDateReceived())
        item['DateOpened'] = self.ulocalized_time(obj.getDateOpened())
        item['ExpiryDate'] = self.ulocalized_time(obj.getExpiryDate())

        after_icons = ''
        if obj.getBlank():
            after_icons += "<img\
            src='%s/++resource++bika.lims.images/blank.png' \
            title='%s'>" % (self.portal_url, t(_('Blank')))
        if obj.getHazardous():
            after_icons += "<img\
            src='%s/++resource++bika.lims.images/hazardous.png' \
            title='%s'>" % (self.portal_url, t(_('Hazardous')))
        item['replace']['ID'] = "<a href='%s/base_view'>%s</a>&nbsp;%s" % \
            (item['url'], item['ID'], after_icons)
        return item
