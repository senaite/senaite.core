# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
from datetime import datetime

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.chart.analyses import EvolutionChart
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from plone.memoize import view
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATContentTypes.utils import DT2dt
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class ViewView(BrowserView):
    """ Reference Sample View
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/referencesample_view.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url +\
            "/++resource++bika.lims.images/referencesample_big.png"

    def __call__(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        self.results = {}  # {category_title: listofdicts}
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
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/referencesample_big.png"
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
            self._analysesview = ReferenceAnalysesView(
                self.context, self.request)
            self._analysesview.allow_edit = False
            self._analysesview.show_select_column = False
            self._analysesview.show_workflow_action_buttons = False
            self._analysesview.form_id = "%s_qcanalyses" % self.context.UID()
            self._analysesview.review_states[0]['transitions'] = [{}]
        return self._analysesview

    def getReferenceSampleId(self):
        return self.context.id

    def get_analyses_json(self):
        return self.get_analyses_view().chart.get_json()


class ReferenceAnalysesView(AnalysesView):
    """ Reference Analyses on this sample
    """
    implements(IViewView)

    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.contentFilter = {
            'portal_type': 'ReferenceAnalysis',
            'path': {'query': "/".join(self.context.getPhysicalPath()),
                     'level': 0}}
        self.columns = {
            'id': {'title': _('ID'), 'toggle': False},
            'getReferenceAnalysesGroupID': {
                'title': _('QC Sample ID'), 'toggle': True},
            'Category': {'title': _('Category'), 'toggle': True},
            'Service': {'title': _('Service'), 'toggle': True},
            'Worksheet': {'title': _('Worksheet'), 'toggle': True},
            'Method': {
                'title': _('Method'),
                'sortable': False,
                'toggle': True},
            'Instrument': {
                'title': _('Instrument'),
                'sortable': False,
                'toggle': True},
            'Result': {'title': _('Result'), 'toggle': True},
            'CaptureDate': {
                'title': _('Captured'),
                'index': 'getResultCaptureDate',
                'toggle': True},
            'Uncertainty': {'title': _('+-'), 'toggle': True},
            'DueDate': {'title': _('Due Date'),
                        'index': 'getDueDate',
                        'toggle': True},
            'retested': {'title': _('Retested'),
                         'type': 'boolean', 'toggle': True},
            'state_title': {'title': _('State'), 'toggle': True},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [],
             'columns':['id',
                        'getReferenceAnalysesGroupID',
                        'Category',
                        'Service',
                        'Worksheet',
                        'Method',
                        'Instrument',
                        'Result',
                        'CaptureDate',
                        'Uncertainty',
                        'DueDate',
                        'state_title'],
             },
        ]
        self.chart = EvolutionChart()

    def isItemAllowed(self, obj):
        """
        :obj: it is a brain
        """
        allowed = super(ReferenceAnalysesView, self).isItemAllowed(obj)
        return allowed if not allowed else obj.getResult != ''

    def folderitem(self, obj, item, index):
        """
        :obj: it is a brain
        """
        item = super(ReferenceAnalysesView, self).folderitem(obj, item, index)
        if not item:
            return None
        item['Category'] = obj.getCategoryTitle
        ref_analysis = api.get_object(obj)
        ws = ref_analysis.getWorksheet()
        if not ws:
            logger.warn(
                'No Worksheet found for ReferenceAnalysis {}'
                .format(obj.getId))
        else:
            item['Worksheet'] = ws.Title()
            anchor = '<a href="%s">%s</a>' % (ws.absolute_url(), ws.Title())
            item['replace']['Worksheet'] = anchor

        # Add the analysis to the QC Chart
        self.chart.add_analysis(obj)
        return item


class ReferenceResultsView(BikaListingView):
    """Listing of all reference results
    """

    def __init__(self, context, request):
        super(ReferenceResultsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "UID": self.get_reference_results().keys(),
            "inactive_state": "active",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Reference Values"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/referencesample_big.png"
        )

        self.show_select_row = False
        self.show_workflow_action_buttons = False
        self.show_select_column = False
        self.pagesize = 999999
        self.show_search = False

        # Categories
        if self.show_categories_enabled():
            self.categories = []
            self.show_categories = True
            self.expand_all_categories = True
            self.category_index = "getCategoryTitle"

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Analysis Service"),
                "sortable": False}),
            ("result", {
                "title": _("Expected Result"),
                "sortable": False}),
            ("error", {
                "title": _("Permitted Error %"),
                "sortable": False}),
            ("min", {
                "title": _("Min"),
                "sortable": False}),
            ("max", {
                "title": _("Max"),
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys()
            }
        ]

    def update(self):
        """Update hook
        """
        super(ReferenceResultsView, self).update()
        self.categories.sort()

    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        return self.context.bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def get_reference_results(self):
        """Return a mapping of Analysis Service -> Reference Results
        """
        referenceresults = self.context.getReferenceResults()
        return dict(map(lambda rr: (rr.get("uid"), rr), referenceresults))

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        uid = api.get_uid(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if category not in self.categories:
                self.categories.append(category)
            item["category"] = category

        ref_results = self.get_reference_results()
        ref_result = ref_results.get(uid)

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["result"] = ref_result.get("result")
        item["min"] = ref_result.get("min")
        item["max"] = ref_result.get("max")

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=_("Accredited"))
        if obj.getAttachmentOption() == "r":
            after_icons += get_image(
                "attach_reqd.png", title=_("Attachment required"))
        if obj.getAttachmentOption() == "n":
            after_icons += get_image(
                "attach_no.png", title=_("Attachment not permitted"))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item


class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """
    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/referencesample_big.png"
        self.title = self.context.translate(_("Reference Samples"))
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on': 'id',
                              'sort_order': 'reverse',
                              'path': {"query": ["/"], "level": 0}, }
        self.context_actions = {}
        self.show_select_column = True

        self.columns = {
            'ID': {
                'title': _('ID'),
                'index': 'id'},
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title',
                'toggle': True},
            'Supplier': {
                'title': _('Supplier'),
                'toggle': True,
                'attr': 'aq_parent.Title',
                'replace_url': 'aq_parent.absolute_url'},
            'Manufacturer': {
                'title': _('Manufacturer'),
                'toggle': True,
                'attr': 'getManufacturer.Title',
                'replace_url': 'getManufacturer.absolute_url'},
            'Definition': {
                'title': _('Reference Definition'),
                'toggle': True,
                'attr': 'getReferenceDefinition.Title',
                'replace_url': 'getReferenceDefinition.absolute_url'},
            'DateSampled': {
                'title': _('Date Sampled'),
                'index': 'getDateSampled',
                'toggle': True},
            'DateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived',
                'toggle': True},
            'DateOpened': {
                'title': _('Date Opened'),
                'toggle': True},
            'ExpiryDate': {
                'title': _('Expiry Date'),
                'index': 'getExpiryDate',
                'toggle': True},
            'state_title': {
                'title': _('State'),
                'toggle': True},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Current'),
             'contentFilter': {'review_state': 'current'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id': 'expired',
             'title': _('Expired'),
             'contentFilter': {'review_state': 'expired'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id': 'disposed',
             'title': _('Disposed'),
             'contentFilter': {'review_state': 'disposed'},
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
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
                    self.workflow.doActionFor(obj, 'expire')
                    item['review_state'] = 'expired'
                    item['obj'] = obj

        if self.contentFilter.get('review_state', '') \
           and item.get('review_state', '') == 'expired':
            # This item must be omitted from the list
            return None

        item['ID'] = obj.id
        item['DateSampled'] = self.ulocalized_time(
            obj.getDateSampled(), long_format=True)
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
