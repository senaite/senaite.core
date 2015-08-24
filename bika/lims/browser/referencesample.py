from AccessControl import getSecurityManager
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive
from operator import itemgetter
from bika.lims.browser.analyses import AnalysesView
from plone.app.layout.globals.interfaces import IViewView
from zope.component import getMultiAdapter
from zope.interface import implements
import json, plone
from operator import itemgetter

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
            'Category': {'title': _('Category'), 'toggle':True},
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

    def folderitems(self):
        items = super(ReferenceAnalysesView, self).folderitems()
        items.sort(key=itemgetter('CaptureDate'), reverse=True)
        outitems = []
        for x in range(len(items)):
            if not items[x].has_key('obj') or items[x]['Result'] == '':
                continue
            obj = items[x]['obj']
            service = obj.getService()
            items[x]['id'] = obj.getId()
            items[x]['Category'] = service.getCategoryTitle()
            items[x]['Service'] = service.Title()
            items[x]['Captured'] = self.ulocalized_time(obj.getResultCaptureDate())
            brefs = obj.getBackReferences("WorksheetAnalysis")
            items[x]['Worksheet'] = brefs and brefs[0].Title() or ''

            # Create json
            qcid = obj.aq_parent.id;
            serviceref = "%s (%s)" % (items[x]['Service'], items[x]['Keyword'])
            trows = self.anjson.get(serviceref, {});
            anrows = trows.get(qcid, []);
            anid = '%s.%s' % (items[x]['getReferenceAnalysesGroupID'],
                              items[x]['id'])
            rr = obj.aq_parent.getResultsRangeDict()
            uid = service.UID()
            if uid in rr:
                specs = rr[uid];
                try:
                    smin  = float(specs.get('min', 0))
                    smax = float(specs.get('max', 0))
                    error  = float(specs.get('error', 0))
                    target = float(specs.get('result', 0))
                    result = float(items[x]['Result'])
                    error_amount = ((target / 100) * error) if target > 0 else 0
                    upper  = smax + error_amount
                    lower   = smin - error_amount

                    anrow = { 'date': items[x]['CaptureDate'],
                              'min': smin,
                              'max': smax,
                              'target': target,
                              'error': error,
                              'erroramount': error_amount,
                              'upper': upper,
                              'lower': lower,
                              'result': result,
                              'unit': items[x]['Unit'],
                              'id': items[x]['uid'] }
                    anrows.append(anrow);
                    trows[qcid] = anrows;
                    self.anjson[serviceref] = trows
                except:
                    pass
            outitems.append(items[x])
        return outitems

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
        self.description = self.context.translate(_("All reference samples in the system are displayed here."))
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path':{"query": ["/"], "level" : 0 }, }
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

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
                'toggle':True},
            'Definition': {
                'title': _('Reference Definition'),
                'toggle':True},
            'DateSampled': {
                'title': _('Date Sampled'),
                'index': 'getDateSampled',
                'toggle':True},
            'DateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived',
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
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'id':'expired',
             'title': _('Expired'),
             'contentFilter':{'review_state':'expired'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'id':'disposed',
             'title': _('Disposed'),
             'contentFilter':{'review_state':'disposed'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate',
                         'state_title']},
        ]

    def folderitems(self):
        items = super(ReferenceSamplesView, self).folderitems()
        outitems = []
        workflow = getToolByName(self.context, 'portal_workflow')
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'current':
                # Check expiry date
                from Products.ATContentTypes.utils import DT2dt
                from datetime import datetime
                expirydate = DT2dt(obj.getExpiryDate()).replace(tzinfo=None)
                if (datetime.today() > expirydate):
                    workflow.doActionFor(obj, 'expire')
                    items[x]['review_state'] = 'expired'
                    items[x]['obj'] = obj
                    if 'review_state' in self.contentFilter \
                        and self.contentFilter['review_state'] == 'current':
                        continue

            items[x]['ID'] = obj.id
            items[x]['replace']['Supplier'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            if obj.getReferenceDefinition():
                items[x]['replace']['Definition'] = "<a href='%s'>%s</a>" % \
                 (obj.getReferenceDefinition().absolute_url(), obj.getReferenceDefinition().Title())
            else:
                items[x]['Definition'] = ' '

            items[x]['DateSampled'] = self.ulocalized_time(obj.getDateSampled())
            items[x]['DateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['ExpiryDate'] = self.ulocalized_time(obj.getExpiryDate())

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous.png' title='Hazardous'>"
            items[x]['replace']['ID'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)
            outitems.append(items[x])
        return outitems
