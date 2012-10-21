from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from AccessControl import getSecurityManager
from bika.lims.permissions import AddBatch
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IBatchFolder
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.browser import BrowserView
from zope.interface import implements
from Products.CMFCore import permissions
import plone
import json

class BatchFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type':'Batch'}
        self.context_actions = {}
        self.icon = "++resource++bika.lims.images/batch_big.png"
        self.title = _("Batches")
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 25
        request.set('disable_border', 1)

        self.columns = {
            'BatchID': {'title': _('Batch ID')},
            'Description':  {'title': _('Description')},
            'Requests':  {'title': _('Analysis Requests')},
            'state_title': {'title': _('State'), 'sortable':False},
        }

        self.review_states = [ # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'cancellation_state':'active',
                               'review_state': 'open'},
             'title': _('Open'),
             'columns':['BatchID',
                        'Description',
                        'Requests',
                        'state_title', ]
             },
            {'id':'closed',
             'contentFilter': {'review_state': 'closed'},
             'title': _('Closed'),
             'columns':['BatchID',
                        'Description',
                        'Requests',
                        'state_title', ]
             },
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns':['BatchID',
                        'Description',
                        'Requests',
                        'state_title', ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns':['BatchID',
                        'Description',
                        'Requests',
                        'state_title', ]
             },
        ]

#    def __call__(self):
#        return super(BatchFolderContentsView, self).__call__()

    def folderitems(self):
        self.filter_indexes = None

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            items[x]['replace']['BatchID'] = "<a href='%s'>%s</a>" % (items[x]['url'], obj.getBatchID())
            items[x]['Requests'] = len(self.context.getBackReferences("AnalysisRequestBatch"))

        return items

class ajaxGetBatches(BrowserView):
    """ Vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm']
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        wf = getToolByName(self.context, 'portal_workflow')

        rows = [{'BatchID': b.Title or '',
                 'Description': b.Description,
                 'BatchUID': b.UID} for b in self.bika_catalog(portal_type='Batch')
                if b.Title.find(searchTerm) > -1
                or b.Description.find(searchTerm) > -1]

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'BatchID'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)
