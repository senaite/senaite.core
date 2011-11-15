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
                                       'depth':1}}
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
            'DueDate': {'title': _('Due date')},
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
        self.title = _("")
        self.description = _("")
        self.contentFilter = {}
        self.content_add_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
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
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        for x in self.context.getReferenceResults():
            service = rc.lookupObject(x['uid'])
            path = "/".join(self.context.getPhysicalPath())
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
                'path': path,
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

class ajaxGetReferenceDefinitionInfo():
    """ Returns a JSON encoded copy of the ReferenceResults field for a ReferenceDefinition,
        and a list of category UIDS that contain services with results.
        Also returns the 'blank' boolean, to select the checkbox on the edit form if required.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('uid', None)
        if not uid:
            return json.dumps({'errors':["No UID specified in request.",]})
        rc = getToolByName(self.context, REFERENCE_CATALOG)

        # first grab the reference results themselves
        ref_def = rc.lookupObject(uid)
        if not ref_def:
            return json.dumps({'errors':["Reference Definition %s does not exist."%uid,]})
        results = ref_def.getReferenceResults()
        if not results:
            return json.dumps({'errors':["The reference definition does not define any values.",]})

        # we return a list of category uids so the javascript knows which ones to expand
        categories = []
        for result in results:
            service = rc.lookupObject(result['uid'])
            cat_uid = service.getCategory().UID()
            if cat_uid not in categories: categories.append(cat_uid)

        return json.dumps({'results':results,
                           'categories':categories,
                           'blank':ref_def.getBlank(),
                           'hazardous':ref_def.getHazardous()})


class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """
    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.title = _("Reference Samples")
        self.icon = "++resource++bika.lims.images/referencesample_big.png"
        self.description = _("")
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path':{"query": ["/"], "level" : 0 }, }
        self.content_add_actions = {}
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
            {'title': _('All'), 'id':'all',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate',
                         'state_title']},
            {'title': _('Current'), 'id':'current',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'title': _('Expired'), 'id':'expired',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'title': _('Disposed'), 'id':'disposed',
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
##            items[x]['Manufacturer'] = obj.getReferenceManufacturer() and \
##                 obj.getReferenceManufacturer().Title() or ''
##            items[x]['LotNumber'] = obj.getLotNumber()
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
