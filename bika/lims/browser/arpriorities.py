import csv
import plone
import time
from collective.progressbar.events import InitialiseProgressBar
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import UpdateProgressEvent
from collective.progressbar.events import ProgressState
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from bika.lims import PMF, logger, bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import tmpID
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from zope.event import notify

class GlobalARPrioritiesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(GlobalARPrioritiesView, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)
        request.set('disable_border', 1)

        self.catalog = "portal_catalog"
        self.contentFilter = {
                'portal_type': 'ARPriority',
                'path': {'query': '/'.join(context.getPhysicalPath())},
                'sort_on':'sortable_title',
                }
        self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=ARPriority',
                 'icon': self.portal.absolute_url() + \
                         '/++resource++bika.lims.images/add.png'}
        #self.context_actions = \
        #        {_('AR Priority'):
        #                   {'url': 'arpriority_add',
        #                    'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        self.form_id = "arpriorities"

        self.icon = \
            self.portal_url + "/++resource++bika.lims.images/arpriority_big.png"
        self.title = _("Analysis Request Priorities")
        self.description = ""


        self.columns = {
            'title': {'title': _('Import')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title',
                         'state_title']},
            {'id':'draft',
             'title': _('Draft'),
             'contentFilter':{'review_state':'draft'},
             'columns': ['title',
                         ]},
            {'id':'published',
             'title': _('Published'),
             'contentFilter':{'review_state':'published'},
             'columns': ['title',
                         ]},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])

        return items



class GlobalARPriorityAddView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile('templates/arpriority_add_form.pt')

    def __call__(self):
        import pdb; pdb.set_trace()
        if self.context.absolute_url() == \
                self.portal.arpriorities.absolute_url():
            self.request.set('disable_border', 1)
        if self.context.absolute_url() == \
                self.portal.arpriorities.absolute_url() \
        and self.portal_membership.checkPermission(
                ManageARPriority, self.portal.arpriorities):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=ARPriority',
                 'icon': self.portal.absolute_url() + \
                         '/++resource++bika.lims.images/add.png'}
        return super(GlobalARPriorityAddView, self).__call__()

