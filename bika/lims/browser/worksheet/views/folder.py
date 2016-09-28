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

from bika.lims import bikaMessageFactory as _
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import getUsers, tmpID, t
from bika.lims.utils import to_utf8 as _c

import logging
import plone
import json
import zope

class FolderView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    template = ViewPageTemplateFile("../templates/worksheets.pt")

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {
            'portal_type': 'Worksheet',
            'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
            'sort_on':'id',
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
        self.pagesize = 25
        self.restrict_results = False

        request.set('disable_border', 1)

        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = self.context.translate(_("Worksheets"))
        self.description = ""

        pm = getToolByName(context, "portal_membership")
        # this is a property of self, because self.getAnalysts returns it
        self.analysts = getUsers(self, ['Manager', 'LabManager', 'Analyst'])
        self.analysts = self.analysts.sortedByKey()

        bsc = getToolByName(context, 'bika_setup_catalog')
        templates = [t for t in bsc(portal_type = 'WorksheetTemplate',
                                    inactive_state = 'active')]

        self.templates = [(t.UID, t.Title) for t in templates]
        self.templates.sort(lambda x, y: cmp(x[1], y[1]))

        self.instruments = [(i.UID, i.Title) for i in
                            bsc(portal_type = 'Instrument',
                                inactive_state = 'active')]
        self.instruments.sort(lambda x, y: cmp(x[1], y[1]))

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
            'Priority': {'title': _('Priority'),
                        'index':'Priority',
                        'toggle': True},
            'Analyst': {'title': _('Analyst'),
                        'index':'getAnalyst',
                        'toggle': True},
            'Template': {'title': _('Template'),
                         'toggle': True},
            'Services': {'title': _('Services'),
                         'sortable':False,
                         'toggle': False},
            'SampleTypes': {'title': _('Sample Types'),
                            'sortable':False,
                            'toggle': False},
            'Instrument': {'title': _('Instrument'),
                            'sortable':False,
                            'toggle': False},
            'QC': {'title': _('QC'),
                   'sortable':False,
                   'toggle': False},
            'QCTotals': {'title': _('QC Samples (Analyses)'),
                   'sortable':False,
                   'toggle': False},
            'RoutineTotals': {'title': _('Routine Samples (Analyses)'),
                   'sortable':False,
                   'toggle': False},
            'CreationDate': {'title': PMF('Date Created'),
                             'toggle': True,
                             'index': 'created'},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified',],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Priority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'QCTotals',
                        'RoutineTotals',
                        'CreationDate',
                        'state_title']},
            # getAuthenticatedMember does not work in __init__
            # so 'mine' is configured further in 'folderitems' below.
            {'id':'mine',
             'title': _('Mine'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Priority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'QCTotals',
                        'RoutineTotals',
                        'CreationDate',
                        'state_title']},
            {'id':'open',
             'title': _('Open'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'open',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Priority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'QCTotals',
                        'RoutineTotals',
                        'CreationDate',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'to_be_verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'Priority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'QCTotals',
                        'RoutineTotals',
                        'CreationDate',
                        'state_title']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Priority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'QCTotals',
                        'RoutineTotals',
                        'CreationDate',
                        'state_title']},
        ]

    def __call__(self):
        self.wf = getToolByName(self, 'portal_workflow')
        self.rc = getToolByName(self, REFERENCE_CATALOG)
        self.pm = getToolByName(self.context, "portal_membership")

        if not self.isManagementAllowed():
            # The current has no prvileges to manage WS.
            # Remove the add button
            self.context_actions = {}

        self.member = self.pm.getAuthenticatedMember()
        roles = self.member.getRoles()
        self.restrict_results = 'Manager' not in roles \
                and 'LabManager' not in roles \
                and 'LabClerk' not in roles \
                and 'RegulatoryInspector' not in roles \
                and self.context.bika_setup.getRestrictWorksheetUsersAccess()
        if self.restrict_results == True:
            # Remove 'Mine' button and hide 'Analyst' column
            del self.review_states[1] # Mine
            self.columns['Analyst']['toggle'] = False

        self.can_manage = self.pm.checkPermission(ManageWorksheets, self.context)
        self.selected_state = self.request.get("%s_review_state"%self.form_id,
                                                'default')

        self.analyst_choices = []
        for a in self.analysts:
            self.analyst_choices.append({'ResultValue': a,
                                         'ResultText': self.analysts.getValue(a)})

        self.allow_edit = self.isEditionAllowed()

        # Default value for this attr
        self.can_reassign = False

        return super(FolderView, self).__call__()

    def isManagementAllowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(ManageWorksheets, self.context)

    def isEditionAllowed(self):
        pm = getToolByName(self.context, "portal_membership")
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    def isItemAllowed(self, obj):
        # Only show "my" worksheets
        # this cannot be setup in contentFilter,
        # because AuthenticatedMember is not available in __init__
        if self.selected_state == 'mine' or self.restrict_results == True:
            analyst = obj.getAnalyst().strip()
            if analyst != _c(self.member.getId()):
                return False
        return BikaListingView.isItemAllowed(self, obj)

    def folderitem(self, obj, item, index):
        # Additional info from Worksheet to be added in the item generated by
        # default by bikalisting.

        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        if not item:
            return None

        item['CreationDate'] = self.ulocalized_time(obj.creation_date)
        item['Analyst'] = obj.getAnalyst().strip()
        item['Priority'] = ''
        item['getPriority'] = ''

        instrument = obj.getInstrument()
        item['Instrument'] = instrument.Title() if instrument else ''

        wst = obj.getWorksheetTemplate()
        item['Template'] = wst.Title() if wst else ''
        if wst:
            item['replace']['Template'] = "<a href='%s'>%s</a>" % \
                (wst.absolute_url(), wst.Title())

        if len(obj.getAnalyses()) == 0:
            item['table_row_class'] = 'state-empty-worksheet'

        layout = obj.getLayout()
        item['Title'] = obj.Title()
        turl = "manage_results" if len(layout) > 0 else "add_analyses"
        item['replace']['Title'] = "<a href='%s/%s'>%s</a>" % \
            (item['url'], turl, item['Title'])

        # Set services
        ws_services = {}
        for slot in [s for s in layout if s['type'] == 'a']:
            analysis = self.rc.lookupObject(slot['analysis_uid'])
            if not analysis:
                error = "Analysis with uid '%s' NOT FOUND in Reference Catalog.\n Worksheet: '%s'. Layout: '%s'" % \
                        (slot['analysis_uid'], obj, layout)
                logging.info(error)
                continue
            service = analysis.getService()
            title = service.Title()
            if title not in ws_services:
                ws_services[title] = "<a href='%s'>%s</a>" % \
                    (service.absolute_url(), title)
        keys = list(ws_services.keys())
        keys.sort()
        services = [ws_services[k] for k in keys]
        item['Services'] = ""
        item['replace']['Services'] = ", ".join(services)

        pos_parent = {}
        for slot in layout:
            # compensate for bad data caused by a stupid bug.
            if type(slot['position']) in (list, tuple):
                slot['position'] = slot['position'][0]
            if slot['position'] == 'new':
                continue
            if slot['position'] in pos_parent:
                continue
            pos_parent[slot['position']] = self.rc.lookupObject(slot['container_uid'])

        # Set Sample Types and QC Samples
        sampletypes = []
        qcsamples = []
        for container in pos_parent.values():
            if container.portal_type == 'AnalysisRequest':
                sampletype = "<a href='%s'>%s</a>" % \
                           (container.getSample().getSampleType().absolute_url(),
                            container.getSample().getSampleType().Title())
                sampletypes.append(sampletype)
            if container.portal_type == 'ReferenceSample':
                qcsample = "<a href='%s'>%s</a>" % \
                        (container.absolute_url(),
                         container.Title())
                qcsamples.append(qcsample)

        sampletypes = list(set(sampletypes))
        sampletypes.sort()
        item['SampleTypes'] = ""
        item['replace']['SampleTypes'] = ", ".join(sampletypes)
        qcsamples = list(set(qcsamples))
        qcsamples.sort()
        item['QC'] = ""
        item['replace']['QC'] = ", ".join(qcsamples)
        item['QCTotals'] = ''

        # Total QC Samples (Total Routine Analyses)
        analyses = obj.getAnalyses()
        totalQCAnalyses = [a for a in analyses
                               if a.portal_type == 'ReferenceAnalysis'
                               or a.portal_type == 'DuplicateAnalysis']
        totalQCSamples = [a.getSample().UID() for a in totalQCAnalyses]
        totalQCSamples = list(set(totalQCSamples))
        item['QCTotals'] = str(len(totalQCSamples)) + ' (' + str(len(totalQCAnalyses)) + ')'

        # Total Routine Samples (Total Routine Analyses)
        totalRoutineAnalyses = [a for a in analyses if a not in totalQCAnalyses]
        totalRoutineSamples = [a.getSample().UID() for a in totalRoutineAnalyses]
        totalRoutineSamples = list(set(totalRoutineSamples))
        item['RoutineTotals'] = str(len(totalRoutineSamples)) + ' (' + str(len(totalRoutineAnalyses)) + ')'

        if item['review_state'] == 'open' \
            and self.allow_edit \
            and self.restrict_results == False \
            and self.can_manage == True:
            item['allow_edit'] = ['Analyst', ]
            item['required'] = ['Analyst', ]
            item['choices'] = {'Analyst': self.analyst_choices}
            self.can_reassign = True

        return item

    def folderitems(self):
        items = BikaListingView.folderitems(self)

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
