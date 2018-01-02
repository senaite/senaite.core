# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import getUsers
from bika.lims.utils import to_utf8 as _c
from bika.lims.utils import user_fullname, get_display_list
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


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

        self.allowed_department_filtering = \
            self.context.bika_setup.getAllowDepartmentFiltering()

        self.columns = {
            'Title': {'title': _('Worksheet'),
                      'index': 'getId'},
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
             'contentFilter': {'review_state': ['open',
                                                'to_be_verified', 'verified'],
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
             'contentFilter': {'review_state':['open', 'to_be_verified',
                                               'verified', 'rejected'],
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

    def _get_worksheet_templates_brains(self):
        """
        Returns available Worksheet Templates as brains. Only active Worksheet
        Templates are considered
        :return: list of brains
        """
        catalog = api.get_tool('bika_setup_catalog')
        brains = catalog(portal_type='WorksheetTemplate',
                         inactive_state='active')
        return brains

    def _get_instruments_brains(self):
        """
        Returns available Instruments as brains. Only active Instruments
        are considered
        :return: list of brains
        """
        catalog = api.get_tool('bika_setup_catalog')
        brains = catalog(portal_type='Instrument',
                         inactive_state='active')
        return brains

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
        if (self.selected_state == 'mine' or self.restrict_results) \
            and obj.getAnalyst != _c(self.member.getId()):
            # Check if the current WS is assigned to the current user
            return False

        if not self.allowed_department_filtering:
            # Filtering by department is disabled. Return True
            return True

        # Department filtering is enabled. Check if at least one of the
        # analyses associated to this worksheet belongs to at least one
        # of the departments currently selected.
        cdepuids = self.request.get('filter_by_department_info', '')
        cdepuids = cdepuids.split(',') if cdepuids else []
        deps = obj.getDepartmentUIDs
        allowed = [d for d in obj.getDepartmentUIDs if d in cdepuids]
        return len(allowed) > 0

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
                    self.review_states[x]['custom_transitions'] = [{'id': 'reassign',
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
        """
        Returns a DisplayList with available Worksheet Templates, sorted by
        title ascending. Only active Worksheet Templates are considered
        :return: DisplayList of worksheet templates (uid, title)
        :rtype: DisplayList
        """
        brains = self._get_worksheet_templates_brains()
        return get_display_list(brains)

    def getInstruments(self):
        """
        Returns a DisplayList with available Instruments, sorted by title
        ascending. Only active Instruments are considered
        :return: DisplayList of worksheet templates (uid, title)
        :rtype: DisplayList
        """
        brains = self._get_instruments_brains()
        return get_display_list(brains)

    def getTemplateInstruments(self):
        """ Distionary of instruments per template
            Used in bika_listing.pt
        """
        items = dict()
        templates = self._get_worksheet_templates_brains()
        for template in templates:
            template_obj = api.get_object(template)
            uid_template = api.get_uid(template_obj)
            instrument = template_obj.getInstrument()
            uid_instrument = ''
            if instrument:
                uid_instrument = api.get_uid(instrument)
            items[uid_template] = uid_instrument

        return json.dumps(items)
