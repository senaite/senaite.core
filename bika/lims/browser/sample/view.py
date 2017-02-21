# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import getUsers
from bika.lims.browser.bika_listing import BikaListingFilterBar\
    as BaseBikaListingFilterBar
from Products.Archetypes.public import DisplayList
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from . import SampleEdit
import json
from datetime import datetime, date
import plone
import App


class SampleView(SampleEdit):
    """
    The view of a single sample
    """
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)


class SamplesView(BikaListingView):
    """
    A list of samples view (folder view)
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'created',
                              'sort_order': 'reverse',
                              'path': {'query': "/",
                                       'level': 0 }
                              }
        # So far we will only print if the sampling workflow is activated
        if self.context.bika_setup.getSamplingWorkflowEnabled():
            self.context_actions = {
                _('Print sample sheets'): {
                    'url': 'print_sampling_sheets',
                    'icon': '++resource++bika.lims.images/print_32.png'}
                    }
        else:
                self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.allow_edit = True
        self.form_id = "samples"

        if self.view_url.find("/samples") > -1:
            self.request.set('disable_border', 1)
        else:
            self.view_url = self.view_url + "/samples"

        self.icon = self.portal_url + "/++resource++bika.lims.images/sample_big.png"
        self.title = self.context.translate(_("Samples"))
        self.description = ""
        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        user_is_preserver = 'Preserver' in member.getRoles()
        # Check if the filter bar functionality is activated or not
        self.filter_bar_enabled =\
            self.context.bika_setup.getSamplingBarEnabledSamples()
        # Defined in the __init__.py
        self.columns = {
            'getSampleID': {'title': _('Sample ID'),
                            'index':'getSampleID'},
            'Client': {'title': _("Client"),
                       'toggle': True,},
            'Creator': {'title': PMF('Creator'),
                        'index': 'Creator',
                        'toggle': True},
            'Created': {'title': PMF('Date Created'),
                        'index': 'created',
                        'toggle': False},
            'Requests': {'title': _('Requests'),
                         'sortable': False,
                         'toggle': False},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': True},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': True},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle'},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'getStorageLocation': {'title': _('Storage Location'),
                                    'toggle': False},
            'SamplingDeviation': {'title': _('Sampling Deviation'),
                                  'toggle': False},
            'AdHoc': {'title': _('Ad-Hoc'),
                      'toggle': False},
            'SamplingDate': {'title': _('Sampling Date'),
                                'index': 'getSamplingDate',
                                'input_class': 'datetimepicker_nofuture autosave',
                                'input_width': '10',
                                'toggle': True},
            'DateSampled': {'title': _('Date Sampled'),
                               'index':'getDateSampled',
                               'toggle': SamplingWorkflowEnabled,
                               'input_class': 'datetimepicker_nofuture autosave',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': SamplingWorkflowEnabled},
            'getScheduledSamplingSampler': {
                'title': _('Sampler for scheduled sampling'),
                'input_class': 'autosave',
                'toggle': self.context.bika_setup.getScheduleSamplingEnabled()
                },
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10'},
            'getPreserver': {'title': _('Preserver'),
                             'toggle': user_is_preserver},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle': False},
            'state_title': {'title': _('State'),
                            'index':'review_state'},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'cancellation_state': 'active',
                               'sort_on': 'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived',
                         'state_title']},
            {'id': 'to_be_sampled',
             'title': _('To be sampled'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'scheduled_sampling'),
                               'cancellation_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'state_title'],
             'transitions': [
                {'id': 'schedule_sampling'}, {'id': 'sample'}],
             },
            {'id': 'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_preserved',
                                                'sample_due'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'state_title']},
            {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state':'sample_received',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'contentFilter':{'review_state':'expired',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'contentFilter':{'review_state':'disposed',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'sort_order': 'reverse',
                               'sort_on':'created'},
             'transitions': [{'id':'reinstate'}, ],
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'SamplingDate',
                         'getScheduledSamplingSampler',
                         'DateReceived',
                         'DateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'state_title']},
            {'id': 'rejected',
             'title': _('Rejected'),
             'contentFilter': {'review_state': 'rejected',
                               'sort_order': 'reverse',
                               'sort_on': 'created'},
             'transitions': [],
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'DateReceived',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'state_title']},
        ]

    def folderitem(self, obj, item, index):
        workflow = getToolByName(self.context, "portal_workflow")
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        translate = self.context.translate
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles
        if not item.has_key('obj'):
            return item
        obj = item['obj']

        item['replace']['getSampleID'] = "<a href='%s'>%s</a>" % \
            (item['url'], obj.getSampleID())
        item['replace']['Requests'] = ",".join(
            ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
             for o in obj.getAnalysisRequests()])
        item['Client'] = obj.aq_parent.Title()
        if hideclientlink == False:
            item['replace']['Client'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
        item['Creator'] = self.user_fullname(obj.Creator())

        item['DateReceived'] = self.ulocalized_time(obj.getDateReceived())

        deviation = obj.getSamplingDeviation()
        item['SamplingDeviation'] = deviation and deviation.Title() or ''

        item['getStorageLocation'] = obj.getStorageLocation() and obj.getStorageLocation().Title() or ''
        item['AdHoc'] = obj.getAdHoc() and True or ''

        item['Created'] = self.ulocalized_time(obj.created())

        sd = obj.getSamplingDate()
        item['SamplingDate'] = \
            self.ulocalized_time(sd, long_format=1) if sd else ''

        after_icons = ''
        if obj.getSampleType().getHazardous():
            after_icons += "<img title='%s' " \
                "src='%s/++resource++bika.lims.images/hazardous.png'>" % \
                (t(_("Hazardous")),
                 self.portal_url)
        if sd and sd > DateTime():
            after_icons += "<img title='%s' " \
                "src='%s/++resource++bika.lims.images/calendar.png' >" % \
                (t(_("Future dated sample")),
                 self.portal_url)
        if after_icons:
            item['after']['getSampleID'] = after_icons

        SamplingWorkflowEnabled =\
            self.context.bika_setup.getSamplingWorkflowEnabled()

        if SamplingWorkflowEnabled and (not sd or not sd > DateTime()):
            datesampled = self.ulocalized_time(
                obj.getDateSampled(), long_format=True)
            if not datesampled:
                datesampled = self.ulocalized_time(
                    DateTime(), long_format=True)
                item['class']['DateSampled'] = 'provisional'
            sampler = obj.getSampler().strip()
            if sampler:
                item['replace']['getSampler'] = self.user_fullname(sampler)
            if 'Sampler' in member.getRoles() and not sampler:
                sampler = member.id
                item['class']['getSampler'] = 'provisional'
        else:
            datesampled = ''
            sampler = ''
        item['DateSampled'] = datesampled
        item['getSampler'] = sampler
        # sampling workflow - inline edits for Sampler, Date Sampled and
        # Scheduled Sampling Sampler
        checkPermission = self.context.portal_membership.checkPermission
        state = workflow.getInfoFor(obj, 'review_state')
        if state in ['to_be_sampled', 'scheduled_sampling']:
            item['required'] = []
            item['allow_edit'] = []
            item['choices'] = {}
            samplers = getUsers(obj, ['Sampler', 'LabManager', 'Manager'])
            users = [(
                {'ResultValue': u, 'ResultText': samplers.getValue(u)})
                for u in samplers]
            # both situations
            if checkPermission(SampleSample, obj) or\
                    self._schedule_sampling_permissions():
                item['required'].append('getSampler')
                item['allow_edit'].append('getSampler')
                item['choices']['getSampler'] = users
            # sampling permissions
            if checkPermission(SampleSample, obj):
                getAuthenticatedMember = self.context.\
                    portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                Sampler = sampler and sampler or \
                    (username in samplers.keys() and username) or ''
                item['required'].append('DateSampled')
                item['allow_edit'].append('DateSampled')
                item['getSampler'] = Sampler
            # coordinator permissions
            if self._schedule_sampling_permissions():
                item['required'].append('SamplingDate')
                item['allow_edit'].append('SamplingDate')
                item['required'].append('getScheduledSamplingSampler')
                item['allow_edit'].append(
                    'getScheduledSamplingSampler')
                item['choices']['getScheduledSamplingSampler'] = users
        # These don't exist on samples
        # the columns exist just to set "preserve" transition from lists.
        # XXX This should be a list of preservers...
        item['getPreserver'] = ''
        item['getDatePreserved'] = ''
        # Here we are defining the name of the content field represented by
        # the column
        item['field']['getSampler'] = 'Sampler'
        item['field']['getScheduledSamplingSampler'] =\
            'ScheduledSamplingSampler'
        # inline edits for Preserver and Date Preserved
        checkPermission = self.context.portal_membership.checkPermission
        if checkPermission(PreserveSample, obj):
            item['required'] = ['getPreserver', 'getDatePreserved']
            item['allow_edit'] = ['getPreserver', 'getDatePreserved']
            preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
            getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
            username = getAuthenticatedMember().getUserName()
            users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                     for u in preservers]
            item['choices'] = {'getPreserver': users}
            preserver = username in preservers.keys() and username or ''
            item['getPreserver'] = preserver
            item['getDatePreserved'] = self.ulocalized_time(DateTime())
            item['class']['getPreserver'] = 'provisional'
            item['class']['getDatePreserved'] = 'provisional'
        return item

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self, full_objects=False)
        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
        # Hide schedule_sampling if user has no rights
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i,state in enumerate(self.review_states):
            if state and self.review_state and state['id'] == self.review_state.get('id', ''):
                if 'getSampler' not in toggle_cols \
                   or 'DateSampled' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('sample')
                    else:
                        state['hide_transitions'] = ['sample',]
                if 'getPreserver' not in toggle_cols \
                   or 'getDatePreserved' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('preserve')
                    else:
                        state['hide_transitions'] = ['preserve',]
                # Check if the user has the rights to schedule samplings and
                # the check-box 'ScheduleSamplingEnabled' in bikasetup is set
                if self._schedule_sampling_permissions():
                    # Show the workflow transition button 'schedule_sampling'
                    pass
                else:
                    # Hiddes the button
                    state['hide_transitions'] = ['schedule_sampling', ]
            new_states.append(state)
        self.review_states = new_states
        return items

    def _schedule_sampling_permissions(self):
        """
        This function checks if all the 'schedule a sampling' conditions
        are met
        """
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        return self.context.bika_setup.getScheduleSamplingEnabled() and\
            ('SamplingCoordinator' in roles or 'Manager' in roles)

    def isItemAllowed(self, obj):
        """
        Checks the BikaLIMS conditions and also checks filter bar conditions
        @Obj: it is a sample object.
        @return: boolean
        """
        # TODO-performance:we are expecting for the sample object.
        # Should be only a brain
        if self.filter_bar_enabled and not self.filter_bar_check_item(obj):
            return False
        return super(SamplesView, self).isItemAllowed(obj)

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :return: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            BikaListingFilterBar(context=self.context, request=self.request)
        return self._advfilterbar


class BikaListingFilterBar(BaseBikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    # TODO-performance: Improve filter bar using catalogs
    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :return: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = [{
            'name': 'sample_condition',
            'label': _('Sample condition'),
            'type': 'select',
            'voc': self._getSampleConditionsVoc(),
        }, {
            'name': 'print_state',
            'label': _('Print state'),
            'type': 'select',
            'voc': self._getPrintStatesVoc(),
        }, {
            'name': 'sample_type',
            'label': _('Sample type'),
            'type': 'select',
            'voc': self._getSampleTypesVoc(),
        }, {
            'name': 'case',
            'label': _('Cases'),
            'type': 'autocomplete_text',
            'voc': json.dumps(self._getCasesVoc()),
        }, {
            'name': 'date_received',
            'label': _('Date received'),
            'type': 'date_range',
        },
        ]
        return fields_dict

    def _getSampleConditionsVoc(self):
        """
        Returns a DisplayList object with sample condtions.
        """
        cons = self.context.bika_setup.\
            bika_sampleconditions.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in cons])

    def _getPrintStatesVoc(self):
        """
        Returns a DisplayList object with print states.
        """
        return DisplayList([
            ('0', _('Never printed')),
            ('1', _('Printed after last publish')),
            ('2', _('Printed but republished afterwards')),
            ])

    def _getSampleTypesVoc(self):
        """
        Returns a DisplayList object with sample types.
        """
        types = self.context.bika_setup.bika_sampletypes.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in types])

    def _getCasesVoc(self):
        """
        Returns a list object with active cases ids.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog({
            'portal_type': 'Batch',
            'review_state': 'open',
        })
        return [brain.id for brain in brains]

    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a query accordingly.
        Only returns the once that can be added to contentFilter dictionary.
        in this case, the catalog is bika_catalog
        In this case the keys with index representation are:
        - date_received - getDateReceived
        - date_received - BatchUID
        :return: a dictionary to be added to contentFilter.
        """
        query_dict = {}
        filter_dict = self.get_filter_bar_dict()
        # Date received filter
        if filter_dict.get('date_received_0', '') or\
                filter_dict.get('date_received_1', ''):
            date_0 = filter_dict.get('date_received_0') \
                if filter_dict.get('date_received_0', '')\
                else '1900-01-01'
            date_1 = filter_dict.get('date_received_1')\
                if filter_dict.get('date_received_1', '')\
                else datetime.strftime(date.today(), "%Y-%m-%d")
            date_range_query = {
                'query':
                (date_0 + ' 00:00', date_1 + ' 23:59'), 'range': 'min:max'}
            query_dict['getDateReceived'] = date_range_query
        # Batch(case) filter
        if filter_dict.get('case', ''):
            # removing the empty and space values and gettin their UIDs
            clean_list_ids = [
                a.strip() for a in filter_dict.get('case', '').split(',')
                if a.strip()]
            # Now we have the case(batch) ids, lets get their UIDs
            catalog = getToolByName(self, 'bika_catalog')
            brains = catalog(
                portal_type='Batch',
                cancellation_state='active',
                review_state='open',
                id=clean_list_ids
                )
            query_dict['BatchUID'] = [a.UID for a in brains]
        # Sample type filter
        if filter_dict.get('sample_type', ''):
            query_dict['getSampleTypeUID'] = filter_dict.get('sample_type', '')
        return query_dict

    def filter_bar_check_item(self, item):
        """
        This functions receives a key-value items, and checks if it should be
        displayed.
        It is recomended to be used in isItemAllowed() method.
        This function should be only used for those fields without
        representation as an index in the catalog.
        :item: The item to check.
        :return: boolean.
        """
        dbar = self.get_filter_bar_dict()
        keys = dbar.keys()
        final_decision = 'True'
        for key in keys:
            if key == 'sample_condition' and dbar.get(key, '') != '':
                if not item.getSampleCondition() or\
                        dbar.get(key, '') != item.getSampleCondition().UID():
                    return False
            if key == 'print_state' and dbar.get(key, '') != '':
                status = [ar.getPrinted() for ar in item.getAnalysisRequests()]
                if dbar.get(key, '') not in status:
                    return False
        return True
