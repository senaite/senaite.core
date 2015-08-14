# coding=utf-8
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class AnalysisRequestsView(BikaListingView):
    ## This table displays a list of ARs referenced by this worksheet.
    ## used in add_duplicate view.
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.context.absolute_url() + "/add_duplicate"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False

        self.columns = {
            'Position': {'title': _('Position')},
            'RequestID': {'title': _('Request ID')},
            'Client': {'title': _('Client')},
            'created': {'title': _('Date Requested')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['Position', 'RequestID', 'Client', 'created'],
            },
        ]

    def folderitems(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        ars = {}
        for slot in self.context.getLayout():
            if slot['type'] != 'a':
                continue
            ar = slot['container_uid']
            if not ars.has_key(ar):
                ars[ar] = slot['position']
        items = []
        for ar, pos in ars.items():
            ar = rc.lookupObject(ar)
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': ar,
                'id': ar.id,
                'uid': ar.UID(),
                'title': ar.Title(),
                'type_class': 'contenttype-AnalysisService',
                'url': ar.absolute_url(),
                'relative_url': ar.absolute_url(),
                'view_url': ar.absolute_url(),
                'Position': pos,
                'RequestID': ar.id,
                'Client': ar.aq_parent.Title(),
                'created': self.ulocalized_time(ar.created()),
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
                'required': [],
            }
            items.append(item)
        items = sorted(items, key = itemgetter('Position'))

        return items
