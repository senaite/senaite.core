from Acquisition import aq_inner, aq_parent
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json

class LogView(BikaListingView):
    """ Show log entries, workflow history and revision history details
    for an object
    """
    implements(IViewView)

    template = ViewPageTemplateFile("templates/log.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        translate = context.translation_service.translate

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 1000

        self.icon = "++resource++bika.lims.images/%s_big.png" % \
            context.portal_type.lower()
        self.title = "%s %s" % (self.context.Title(),
                                translate(_("Log")))
        self.description = ""

        self.columns = {
            'Version': {'title': _('Version')},
            'Date': {'title': _('Date')},
            'User': {'title': _('User')},
            'Action': {'title': _('Action')},
            'Description': {'title': _('Description')},
        }
        self.review_states = [
            {'id':'all',
             'title': 'All',
             'columns': ['Version',
                         'Date',
                         'User',
                         'Action',
                         'Description']},
        ]

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        bsc = bsc = getToolByName(self.context, 'bika_setup_catalog')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, 'portal_workflow')
        pr = getToolByName(self.context, 'portal_repository')

        isVersionable = pr.isVersionable(aq_inner(self.context))
        review_history = wf.getInfoFor(self.context, 'review_history')
        review_history.reverse()
        items = []
        for entry in review_history:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': self.context,
                'id': self.context.id,
                'uid': self.context.UID(),
                'title': self.context.title_or_id(),
                'type_class': '',
                'url': self.context.absolute_url(),
                'relative_url': self.context.absolute_url(),
                'view_url': self.context.absolute_url(),
                'path': "/".join(self.context.getPhysicalPath()),
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': '',
                'allow_edit': [],

                'Version': isVersionable and self.context.get('version_id', '') or '0',
                'Date': TimeOrDate(self.context, entry.get('time'), long_format=1),
                'sortable_date': entry.get('time'),
                'User': entry.get('actor'),
                'Action': entry.get('action') and entry.get('action') or 'Create',
                'Description': "review_state: %s" % entry.get('review_state'),
            }
            items.append(item)
        items = sorted(items, key = itemgetter('sortable_date'))
        items.reverse()

        return items
