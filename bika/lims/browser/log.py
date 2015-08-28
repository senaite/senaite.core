from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_inner, aq_parent
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import to_utf8
from DateTime import DateTime
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.content import ContentHistoryView, ContentHistoryViewlet
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.publisher.browser import TestRequest
import json


class LogView(BikaListingView):

    """ Show log entries, workflow history and revision history details
    for an object
    """
    implements(IViewView)

    template = ViewPageTemplateFile("templates/log.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 999999

        self.icon = self.portal_url + "/++resource++bika.lims.images/%s_big.png" % \
            context.portal_type.lower()
        self.title = to_utf8(self.context.Title()) + " " + t(_("Log"))
        self.description = ""

        self.columns = {
            'Version': {'title': _('Version'), 'sortable': False},
            'Date': {'title': _('Date'), 'sortable': False},
            'User': {'title': _('User'), 'sortable': False},
            'Action': {'title': _('Action'), 'sortable': False},
            'Description': {'title': _('Description'), 'sortable': False},
        }
        self.review_states = [
            {'id': 'default',
             'title': 'All',
             'contentFilter': {},
             'columns': ['Version',
                         'Date',
                         'User',
                         'Action',
                         'Description']},
        ]

    def folderitems(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, 'portal_workflow')
        pr = getToolByName(self.context, 'portal_repository')

        isVersionable = pr.isVersionable(aq_inner(self.context))
        try:
            review_history = wf.getInfoFor(self.context, 'review_history')
            review_history = list(review_history)
            review_history.reverse()
        except WorkflowException:
            review_history = []
        items = []
        for entry in review_history:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            review_state = entry.get('review_state')
            state_title = wf.getTitleForStateOnType(review_state, self.context.portal_type)
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
                'choices': {},
                'class': {},
                'state_class': '',
                'allow_edit': [],
                'required': [],
                'Version': isVersionable and self.context.get('version_id', '') or '0',
                'Date': self.ulocalized_time(entry.get('time')),
                'sortable_date': entry.get('time'),
                'User': entry.get('actor'),
                'Action': entry.get('action') and entry.get('action') or 'Create',
                'Description': "review state: %s" % state_title,
            }
            items.append(item)

        if isVersionable:
            request = TestRequest()
            chv = ContentHistoryViewlet(self.context, request, None, None)
            chv.navigation_root_url = chv.site_url = 'http://localhost:8080/bikas'
            version_history = chv.revisionHistory()
        else:
            version_history = []

        for entry in version_history:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            # disregard the first entry of version history, as it is
            # represented by the first entry in review_history
            if not entry.get('version_id'):
                continue
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
                'choices': {},
                'class': {},
                'state_class': '',
                'allow_edit': [],
                'required': [],
                'Version': entry.get('version_id'),
                'Date': self.ulocalized_time(DateTime(entry.get('time'))),
                'sortable_date': entry.get('time'),
                'User': entry.get('actor').get('fullname'),
                'Action': entry.get('action') and entry.get('action') or 'Create',
                'Description': entry.get('comments'),
            }
            items.append(item)

        items = sorted(items, key=itemgetter('sortable_date'))
        items.reverse()

        return items
