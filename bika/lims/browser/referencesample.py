from AccessControl import getSecurityManager
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive, TimeOrDate
from operator import itemgetter
from bika.lims.browser.analyses import AnalysesView
from plone.app.layout.globals.interfaces import IViewView
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
        self.icon = "++resource++bika.lims.images/referencesample_big.png"
        self.TimeOrDate = TimeOrDate
        rc = getToolByName(context, REFERENCE_CATALOG)

        self.results = {} # {category_title: listofdicts}
        for r in context.getReferenceResults():
            service = rc.lookupObject(r['uid'])
            cat = service.getCategory().Title()
            if cat not in self.results:
                self.results[cat] = []
            r['service'] = service
            self.results[cat].append(r)
        self.categories = self.results.keys()
        self.categories.sort()

    def __call__(self):
        return self.template()

class ReferenceAnalysesView(AnalysesView):
    """ Reference Analyses on this sample
    """
    implements(IViewView)

    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.contentFilter = {'portal_type':'ReferenceAnalysis',
                              'path': {'query':"/".join(self.context.getPhysicalPath()),
                                       'level':0}}
        self.show_select_row = False
        self.show_sort_column = False
        self.show_select_column = False
        self.allow_edit = False

        self.columns = {
            'id': {'title': _('ID')},
            'Category': {'title': _('Category')},
            'Service': {'title': _('Service')},
            'Worksheet': {'title': _('Worksheet')},
            'Result': {'title': _('Result')},
            'Uncertainty': {'title': _('+-')},
            'DueDate': {'title': _('Due Date')},
            'retested': {'title': _('Retested'), 'type':'boolean'},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': [],
             'columns':['id',
                        'Category',
                        'Service',
                        'Worksheet',
                        'Result',
                        'Uncertainty',
                        'DueDate',
                        'state_title'],
             },
        ]

    def folderitems(self):
        self.contentsMethod = getToolByName(self.context, 'portal_catalog')
        items = super(ReferenceAnalysesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            service = obj.getService()
            items[x]['id'] = obj.getId()
            items[x]['Category'] = service.getCategory().Title()
            items[x]['Service'] = service.Title()
            brefs = obj.getBackReferences("WorksheetAnalysis")
            items[x]['Worksheet'] = brefs and brefs[0].Title() or ''
        return items

class ReferenceResultsView(BikaListingView):
    """
    """
    def __init__(self, context, request):
        super(ReferenceResultsView, self).__init__(context, request)
        bsc = getToolByName(context, 'bika_setup_catalog')
        self.contentsMethod = bsc
        self.title = _("Reference Results")
        self.description = _("Click on Analysis Categories (against shaded background) "
                             "to see Analysis Services in each category. Enter minimum "
                             "and maximum values to indicate a valid results range. "
                             "Any result outside this range will raise an alert. "
                             "The % Error field allows for an % uncertainty to be "
                             "considered when evaluating results against minimum and "
                             "maximum values. A result out of range but still in range "
                             "if the % error is taken into consideration, will raise a "
                             "less severe alert.")
        self.contentFilter = {}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_workflow_action_buttons = False
        self.show_select_column = False
        self.pagesize = 1000

        self.columns = {
            'Service': {'title': _('Service')},
            'result': {'title': _('Result')},
            'min': {'title': _('Min')},
            'max': {'title': _('Max')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
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
            service = uc(UID=x['uid'])[0]
            item = {
                'obj': self.context,
                'id': x['uid'],
                'uid': x['uid'],
                'result': x['result'],
                'min': x['min'],
                'max': x['max'],
                'title': service.Title,
                'Service': service.Title,
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
                (service.absolute_url(), service.Title)
            items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        return items

class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """
    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        self.icon = "++resource++bika.lims.images/referencesample_big.png"
        self.title = _("Reference Samples")
        self.description = _("All reference samples in the system are displayed here.")
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
            'ID': {'title': _('ID')},
            'Title': {'title': _('Title')},
            'Supplier': {'title': _('Supplier')},
            'Definition': {'title': _('Reference Definition')},
            'DateSampled': {'title': _('Date Sampled')},
            'DateReceived': {'title': _('Date Received')},
            'ExpiryDate': {'title': _('Expiry Date')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate',
                         'state_title']},
            {'id':'current',
             'title': _('Current'),
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'id':'expired',
             'title': _('Expired'),
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'id':'disposed',
             'title': _('Disposed'),
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
        ]

    def folderitems(self):
        items = super(ReferenceSamplesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ID'] = obj.id
            items[x]['replace']['Supplier'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            if obj.getReferenceDefinition():
                items[x]['replace']['Definition'] = "<a href='%s'>%s</a>" % \
                 (obj.getReferenceDefinition().absolute_url(), obj.getReferenceDefinition().Title())
            else:
                items[x]['Definition'] = ' '

            items[x]['DateSampled'] = \
                 TimeOrDate(self.context, obj.getDateSampled(), long_format=0)
            items[x]['DateReceived'] = \
                 TimeOrDate(self.context, obj.getDateReceived(), long_format=0)
            items[x]['ExpiryDate'] = \
                 TimeOrDate(self.context, obj.getExpiryDate(), long_format=0)

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous.png' title='Hazardous'>"
            items[x]['replace']['ID'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)

        return items
