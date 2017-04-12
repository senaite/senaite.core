# coding=utf-8

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime import DateTime
from DocumentTemplate import sequence
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.utils import user_fullname
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import getUsers, tmpID, t
from bika.lims.utils import to_utf8 as _c
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
import logging
import plone
import json
import zope


class FolderView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    template = ViewPageTemplateFile("../templates/worksheets.pt")

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)
        self.catalog = CATALOG_WORKSHEET_LISTING
        self.contentFilter = {
            'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
            'sort_on':'CreationDate',
            'sort_order': 'reverse'}
        self.context_actions = {_('Add'):
                                {'url': 'worksheet_add',
                                 'icon': '++resource++bika.lims.images/add.png',
                                 'class': 'worksheet_add'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = True
        self.show_select_column = True
        self.restrict_results = False
        self.wf = getToolByName(self, 'portal_workflow')
        self.rc = getToolByName(self, REFERENCE_CATALOG)
        self.pm = getToolByName(self.context, "portal_membership")
        request.set('disable_border', 1)

        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = self.context.translate(_("Worksheets"))
        self.description = ""

        # this is a property of self, because self.getAnalysts returns it
        self.analysts = getUsers(self, ['Manager', 'LabManager', 'Analyst'])
        self.analysts = self.analysts.sortedByKey()
        # TODO: To worksheet catalog
        bsc = getToolByName(context, 'bika_setup_catalog')
        templates = [t for t in bsc(portal_type = 'WorksheetTemplate',
                                    inactive_state = 'active')]

        self.templates = [(t.UID, t.Title) for t in templates]
        self.templates.sort(lambda x, y: cmp(x[1], y[1]))

        self.instruments = [(i.UID, i.Title) for i in
                            bsc(portal_type = 'Instrument',
                                inactive_state = 'active')]
        self.instruments.sort(lambda x, y: cmp(x[1], y[1]))
        self.allowed_department_filtering = \
            self.context.bika_setup.getAllowDepartmentFiltering()
        self.templateinstruments = {}
        for t in templates:
            i = t.getObject().getInstrument()
            if i:
                self.templateinstruments[t.UID] = i.UID()
            else:
                self.templateinstruments[t.UID] = ''

        self.columns = {
            'Title': {'title': _('Worksheet'),
                      'index': 'sortable_title'},
            'Analyst': {'title': _('Analyst'),
                        'index': 'getAnalyst', },
            'Template': {'title': _('Template'),
                         'attr': 'getWorksheetTemplateTitle',
                         'replace_url': 'getWorksheetTemplateURL', },
            'NumRegularSamples': {
                'title': _('Samples'),
                'sortable': False, },
            'NumQCAnalyses': {
                'title': _('QC Analyses'),
                'sortable': False, },
            'NumRegularAnalyses': {
                'title': _('Routine Analyses'),
                'sortable': False, },
            'CreationDate': {'title': PMF('Date Created'),
                             'index': 'created'},
            'state_title': {'title': _('State'),
                            'index': 'review_state',
                            'attr': 'state_title'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {'review_state':['open', 'to_be_verified',],
                               'sort_on':'CreationDate',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'NumRegularSamples',
                        'NumQCAnalyses',
                        'NumRegularAnalyses',
                        'CreationDate',
                        'state_title']},
            # getAuthenticatedMember does not work in __init__
            # so 'mine' is configured further in 'folderitems' below.
            {'id':'mine',
             'title': _('Mine'),
             'contentFilter': {'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'sort_on':'CreationDate',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'NumRegularSamples',
                        'NumQCAnalyses',
                        'NumRegularAnalyses',
                        'CreationDate',
                        'state_title']},
            {'id':'open',
             'title': _('Open'),
             'contentFilter': {'review_state':'open',
                               'sort_on':'CreationDate',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'NumRegularSamples',
                        'NumQCAnalyses',
                        'NumRegularAnalyses',
                        'CreationDate',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state':'to_be_verified',
                               'sort_on':'CreationDate',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'NumRegularSamples',
                        'NumQCAnalyses',
                        'NumRegularAnalyses',
                        'CreationDate',
                        'state_title']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state':'verified',
                               'sort_on':'CreationDate',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'NumRegularSamples',
                        'NumQCAnalyses',
                        'NumRegularAnalyses',
                        'CreationDate',
                        'state_title']},
        ]

    def before_render(self):
        """
        This function is called before the template is being rendered.
        """
        if not self.isManagementAllowed():
            # The current has no prvileges to manage WS.
            # Remove the add button
            self.context_actions = {}
        roles = self.member.getRoles()
        self.restrict_results = 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles \
            and 'RegulatoryInspector' not in roles \
            and self.context.bika_setup.getRestrictWorksheetUsersAccess()
        if self.restrict_results:
            # Remove 'Mine' button and hide 'Analyst' column
            del self.review_states[1]  # Mine
            self.columns['Analyst']['toggle'] = False

        self.can_manage = self.pm.\
            checkPermission(ManageWorksheets, self.context)
        self.selected_state = self.request\
            .get("%s_review_state" % self.form_id, 'default')

        self.analyst_choices = []
        for a in self.analysts:
            self.analyst_choices.append(
                {'ResultValue': a, 'ResultText': self.analysts.getValue(a)})

        self.allow_edit = self.isEditionAllowed()

        # Default value for this attr
        self.can_reassign = False

    def isManagementAllowed(self):
        return self.pm.checkPermission(ManageWorksheets, self.context)

    def isEditionAllowed(self):
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    def isItemAllowed(self, obj):
        """
        Only show "my" worksheets
        this cannot be setup in contentFilter,
        because AuthenticatedMember is not available in __init__
        It also checks if the worksheet can be added to the list depending
        on the department filter. It checks the department of each analysis
        service from each analysis belonguing to the given worksheet.
        If department filtering is disabled in bika_setup, will return True.
        :param obj: An object that represents a Worksheet
        :type obj: CatalogBrain
        :returns: True if the worksheet object meets with the criteria for
            being displayed
        :rtype: bool
        """
        if self.selected_state == 'mine' or self.restrict_results:
            analyst = obj.getAnalyst
            if analyst != _c(self.member.getId()):
                return False
        if not self.allowed_department_filtering:
            return True
        # Gettin the department from worksheet
        deps = obj.getDepartmentUIDs
        result = True
        if deps:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            deps_uids = set(deps)
            filter_uids = set(
                cookie_dep_uid.split(','))
            matches = deps_uids & filter_uids
            result = len(matches) > 0
        return result

    def folderitem(self, obj, item, index):
        """
        :obj: is a worksheet brain.
        """
        # Additional info from Worksheet to be added in the item generated by
        # default by bikalisting.

        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        item['CreationDate'] = self.ulocalized_time(obj.created)
        if len(obj.getAnalysesUIDs) == 0:
            item['table_row_class'] = 'state-empty-worksheet'

        layout = obj.getLayout
        item['Title'] = obj.Title
        turl = "manage_results" if len(layout) > 0 else "add_analyses"
        item['replace']['Title'] = "<a href='%s/%s'>%s</a>" % \
            (item['url'], turl, item['Title'])

        pos_parent = {}
        for slot in layout:
            # compensate for bad data caused by a stupid bug.
            if type(slot['position']) in (list, tuple):
                slot['position'] = slot['position'][0]
            if slot['position'] == 'new':
                continue
            if slot['position'] in pos_parent:
                continue
            pos_parent[slot['position']] =\
                self.rc.lookupObject(slot.get('container_uid'))

        # Total QC Analyses
        item['NumQCAnalyses'] = str(obj.getNumberOfQCAnalyses)
        # Total Routine Analyses
        item['NumRegularAnalyses'] = str(obj.getNumberOfRegularAnalyses)
        # Total Number of Samples
        item['NumRegularSamples'] = str(obj.getNumberOfRegularSamples)

        if item['review_state'] == 'open' \
            and self.allow_edit \
            and not self.restrict_results \
                and self.can_manage:
            item['Analyst'] = obj.getAnalyst
            item['allow_edit'] = ['Analyst', ]
            item['required'] = ['Analyst', ]
            item['choices'] = {'Analyst': self.analyst_choices}
            self.can_reassign = True
        else:
            item['Analyst'] = user_fullname(self.context, obj.getAnalyst)

        return item

    def folderitems(self):
        items = BikaListingView.folderitems(self, classic=False)

        # can_reassigned value is assigned in folderitem(obj,item,index) function
        if self.can_reassign:
            for x in range(len(self.review_states)):
                if self.review_states[x]['id'] in ['default', 'mine', 'open']:
                    self.review_states[x]['custom_actions'] = [{'id': 'reassign',
                                                                'title': _('Reassign')}, ]

        self.show_select_column = self.can_reassign
        self.show_workflow_action_buttons = self.can_reassign

        return items

    def getAnalysts(self):
        """ Present the LabManagers and Analysts as options for analyst
            Used in bika_listing.pt
        """
        return self.analysts

    def getWorksheetTemplates(self):
        """ List of templates
            Used in bika_listing.pt
        """
        return DisplayList(self.templates)

    def getInstruments(self):
        """ List of instruments
            Used in bika_listing.pt
        """
        return DisplayList(self.instruments)

    def getTemplateInstruments(self):
        """ Distionary of instruments per template
            Used in bika_listing.pt
        """
        return json.dumps(self.templateinstruments)
