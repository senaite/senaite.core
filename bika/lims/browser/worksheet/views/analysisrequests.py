# coding=utf-8
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referencesample import ReferenceSamplesView
from bika.lims.exportimport import instruments
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import to_utf8
from bika.lims.utils import getUsers, isActive, tmpID
from DateTime import DateTime
from DocumentTemplate import sequence
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time
from bika.lims.utils import to_utf8 as _c

import plone
import plone.protect
import json


class WorksheetARsView(BikaListingView):
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
