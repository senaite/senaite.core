# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PRIORITIES
from bika.lims import bikaMessageFactory as _
from bika.lims import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.worksheet.tools import checkUserManage
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.utils import t
from bika.lims.vocabularies import CatalogVocabulary


class AddAnalysesView(BikaListingView):
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/add_analyses.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = self.context.translate(_("Add Analyses"))
        self.description = ""
        self.catalog = CATALOG_ANALYSIS_LISTING
        self.context_actions = {}
        # initial review state for first form display of the worksheet
        # add_analyses search view - first batch of analyses, latest first.
        self.sort_on = 'Priority'
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state':'unassigned',
                              'sort_on': 'getPrioritySortkey',
                              'cancellation_state':'active'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_analyses"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'Priority': {
                'title': '',
                'sortable': True,
                'index': 'getPrioritySortkey' },
            'Client': {
                'title': _('Client'),
                'attr': 'getClientTitle',
                'replace_url': 'getClientURL',
                'index':'getClientTitle'},
            'getClientOrderNumber': {
                'title': _('Order'),
                'index': 'getClientOrderNumber'},
            'getRequestID': {
                'title': _('Request ID'),
                'attr': 'getRequestID',
                'replace_url': 'getRequestURL',
                'index': 'getRequestID'},
            'CategoryTitle': {
                'title': _('Category'),
                'attr': 'getCategoryTitle',
                'sortable': False},
            'Title': {
                'title': _('Analysis'),
                'index':'getId'},
            'getDateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived'},
            'getDueDate': {
                'title': _('Due Date'),
                'index': 'getDueDate'},
        }
        self.filter_indexes = ['Title',]
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id':'assign'}, ],
             'columns':['Priority',
                        'Client',
                        'getClientOrderNumber',
                        'getRequestID',
                        'CategoryTitle',
                        'Title',
                        'getDateReceived',
                        'getDueDate'],
            },
        ]

    def __call__(self):
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        # Deny access to foreign analysts
        if checkUserManage(self.context, self.request) == False:
            return []

        showRejectionMessage(self.context)

        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        if 'submitted' in form:
            if 'getWorksheetTemplate' in form and form['getWorksheetTemplate']:
                layout = self.context.getLayout()
                wst = rc.lookupObject(form['getWorksheetTemplate'])
                self.request['context_uid'] = self.context.UID()
                self.context.applyWorksheetTemplate(wst)
                if len(self.context.getLayout()) != len(layout):
                    self.context.plone_utils.addPortalMessage(
                        PMF("Changes saved."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/manage_results")
                else:
                    self.context.plone_utils.addPortalMessage(
                        _("No analyses were added to this worksheet."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/add_analyses")


        # Always apply filter elements
        # Note that the name of those fields is '..Title', but we
        # are getting their UID.
        category = form.get('FilterByCategory', '')
        if category:
            self.contentFilter['getCategoryUID'] = category

        service = form.get('FilterByService', '')
        if service:
            self.contentFilter['getServiceUID'] = service

        client = form.get('FilterByClient', '')
        if client:
            self.contentFilter['getClientUID'] = client

        self.update()

        if self.request.get('table_only', '') == self.form_id or \
                self.request.get('rows_only', '') == self.form_id:
            return self.contents_table()
        else:
            return self.template()

    def GET_url(self, include_current=True, **kwargs):
        """Handler for the "Show More" Button
        """
        url = super(AddAnalysesView, self).GET_url(include_current=include_current, **kwargs)
        form = self.request.form

        # Remember the Client filtering when clicking show more...
        client = form.get('FilterByClient', '')
        if client:
            url += "&FilterByClient={}".format(client)

        category = form.get('FilterByCategory', '')
        if category:
            url += "&FilterByCategory={}".format(client)

        service = form.get('FilterByService', '')
        if service:
            url += "&FilterByService={}".format(client)

        return url

    def isItemAllowed(self, obj):
        """
        Checks if the passed in Analysis must be displayed in the list. If the
        'filtering by department' option is enabled in Bika Setup, this
        function checks if the Analysis Service associated to the Analysis
        is assigned to any of the currently selected departments (information
        stored in a cookie).
        If department filtering is disabled in bika_setup, returns True.
        If the obj is None or empty, returns False.
        If the obj has no department assined, returns True.

        :param obj: A single Analysis brain
        :type obj: CatalogBrain
        :returns: True if the item can be added to the list.
        :rtype: bool
        """
        if not obj:
            return False

        if not self.isAllowDepartmentFiltering:
            return True

        # Department filtering is enabled. Check if the Analysis Service
        # associated to this Analysis is assigned to at least one of the
        # departments currently selected.
        depuid = obj.getDepartmentUID
        deps = self.request.get('filter_by_department_info', '')
        return not depuid or depuid in deps.split(',')

    def folderitems(self):
        self.isAllowDepartmentFiltering =\
            self.context.bika_setup.getAllowDepartmentFiltering()
        # Check if mtool has been initialized
        self.mtool = self.mtool if self.mtool\
            else getToolByName(self.context, 'portal_membership')
        # Getting the current user
        self.member = self.member if self.member\
            else self.mtool.getAuthenticatedMember()
        self.roles = self.member.getRoles()
        self.hideclientlink = 'RegulatoryInspector' in self.roles \
            and 'Manager' not in self.roles \
            and 'LabManager' not in self.roles \
            and 'LabClerk' not in self.roles
        items = BikaListingView.folderitems(self, classic=False)
        return items

    def folderitem(self, obj, item, index):
        """
        :obj: is a brain
        """
        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        item['getDateReceived'] = self.ulocalized_time(obj.getDateReceived)
        DueDate = obj.getDueDate
        item['getDueDate'] = self.ulocalized_time(DueDate)
        if DueDate < DateTime():
            item['after']['DueDate'] = '<img width="16" height="16"'
            ' src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                (self.context.absolute_url(),
                 t(_("Late Analysis")))
        if self.hideclientlink:
            del item['replace']['Client']
        # Add Priority column
        priority_sort_key = obj.getPrioritySortkey
        if not priority_sort_key:
            # Default priority is Medium = 3.
            # The format of PrioritySortKey is <priority>.<created>
            priority_sort_key = '3.%s' % obj.created.ISO8601()
        priority = priority_sort_key.split('.')[0]
        priority_text = PRIORITIES.getValue(priority)
        priority_div = '<div class="priority-ico priority-%s"><span class="notext">%s</span><div>'
        item['replace']['Priority'] = priority_div % (priority, priority_text)
        return item

    def getServices(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        categoryUID = self.request.get('list_getCategoryUID', '')
        if categoryUID:
            return vocabulary(
                portal_type='AnalysisService',
                getCategoryUID=categoryUID,
                sort_on='sortable_title'
            )
        return vocabulary(
            portal_type='AnalysisService',
            sort_on='sortable_title'
        )

    def getClients(self):
        vocabulary = CatalogVocabulary(self)
        return vocabulary(portal_type='Client', sort_on='sortable_title')

    def getCategories(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(
            portal_type='AnalysisCategory',  sort_on='sortable_title')

    def getWorksheetTemplates(self):
        """ Return WS Templates """
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(
            portal_type='WorksheetTemplate', sort_on='sortable_title')
