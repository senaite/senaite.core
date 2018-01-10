# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.browser import BrowserView
from bika.lims import EditSample
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import changeWorkflowState, tmpID
from bika.lims.utils import getUsers
from operator import itemgetter
import App


class SamplePartitionsView(BikaListingView):
    def __init__(self, context, request):
        super(SamplePartitionsView, self).__init__(context, request)
        self.context_actions = {}
        self.title = self.context.translate(_("Sample Partitions"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/samplepartition_big.png"
        self.description = ""
        self.allow_edit = True
        self.show_select_all_checkbox = False
        self.show_sort_column = False
        self.show_column_toggles = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 999999
        self.form_id = "partitions"

        self.columns = {
            'PartTitle': {'title': _('Partition'),
                          'sortable':False},
            'getContainer': {'title': _('Container'),
                             'sortable':False},
            'SecuritySealIntact': {'title': _('Security Seal Intact'),
                                   'type': "boolean",
                                   'allow_edit': True,
                                   'sortable': False},
            'getPreservation': {'title': _('Preservation'),
                                'sortable':False},
##            'getSampler': {'title': _('Sampler'),
##                           'sortable':False},
##            'getDateSampled': {'title': _('Date Sampled'),
##                               'input_class': 'datetimepicker',
##                               'input_width': '10',
##                               'sortable':False},
            'getPreserver': {'title': _('Preserver'),
                             'sortable':False},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10',
                                 'sortable':False}
        }
        if not self.context.absolute_url().endswith('partitions'):
            self.columns['getDisposalDate'] = {'title': _('Disposal Date'),
                                               'sortable':False}
        self.columns['state_title'] = {'title': _('State'), 'sortable':False}

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['PartTitle',
                         'getContainer',
                         'SecuritySealIntact',
                         'getPreservation',
##                         'getSampler',
##                         'getDateSampled',
                         'getPreserver',
                         'getDatePreserved',
                         'state_title'],
             'transitions': [ #{'id': 'sample'},
                             {'id': 'preserve'},
                             {'id': 'receive'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_transitions':[{'id': 'save_partitions_button',
                                'title': _('Save')}, ],
            },
        ]
        if not self.context.absolute_url().endswith('partitions'):
            self.columns['getDisposalDate'] = {'title': _('Disposal Date'),
                                               'sortable':False}

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if self.context.portal_type == 'AnalysisRequest':
            self.sample = self.context.getSample()
        else:
            self.sample = self.context
        if checkPermission(AddSamplePartition, self.sample):
            self.context_actions[_('Add')] = \
                {'url': self.sample.absolute_url() + '/createSamplePartition',
                 'icon': '++resource++bika.lims.images/add.png'}

        return super(SamplePartitionsView, self).__call__()

    def folderitems(self, full_objects = False):
        mtool = getToolByName(self.context, 'portal_membership')
        workflow = getToolByName(self.context, 'portal_workflow')
        checkPermission = mtool.checkPermission
        edit_states = ['sample_registered', 'to_be_sampled', 'sampled',
                       'to_be_preserved', 'sample_due', 'attachment_due',
                       'sample_received', 'to_be_verified']
        if self.context.portal_type == 'AnalysisRequest':
            self.sample = self.context.getSample()
        else:
            self.sample = self.context
        self.allow_edit = checkPermission(EditSamplePartition, self.sample) \
                    and workflow.getInfoFor(self.sample, 'review_state') in edit_states \
                    and workflow.getInfoFor(self.sample, 'cancellation_state') == 'active'
        self.show_select_column = self.allow_edit
        if self.allow_edit == False:
            self.review_states[0]['custom_transitions'] = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')

        containers = [({'ResultValue':o.UID,
                        'ResultText':o.title})
                      for o in bsc(portal_type="Container",
                                   inactive_state="active")]
        preservations = [({'ResultValue':o.UID,
                           'ResultText':o.title})
                         for o in bsc(portal_type="Preservation",
                                      inactive_state="active")]

        parts = [p for p in self.sample.objectValues()
                 if p.portal_type == 'SamplePartition']
        items = []
        for part in parts:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': part,
                'id': part.id,
                'uid': part.UID(),
                'title': part.Title(),
                'type_class': 'contenttype-SamplePartition',
                'url': part.aq_parent.absolute_url(),
                'relative_url': part.aq_parent.absolute_url(),
                'view_url': part.aq_parent.absolute_url(),
                'created': self.ulocalized_time(part.created()),
                'replace': {},
                'before': {},
                'after': {},
                'choices': {},
                'class': {},
                'allow_edit': [],
                'required': [],
            }

            state = workflow.getInfoFor(part, 'review_state')
            item['state_class'] = 'state-'+state
            item['state_title'] = _(state)

            item['PartTitle'] = part.getId()

            container = part.getContainer()
            if self.allow_edit:
                item['getContainer'] = container and container.UID() or ''
            else:
                item['getContainer'] = container and container.Title() or ''
            item['SecuritySealIntact'] = container.getSecuritySealIntact() if container else True
            preservation = part.getPreservation()
            if self.allow_edit:
                item['getPreservation'] = preservation and preservation.UID() or ''
            else:
                item['getPreservation'] = preservation and preservation.Title() or ''

##            sampler = part.getSampler().strip()
##            item['getSampler'] = \
##                sampler and self.user_fullname(sampler) or ''
##            datesampled = part.getDateSampled()
##            item['getDateSampled'] = \
##                datesampled and self.ulocalized_time(datesampled) or ''

            preserver = part.getPreserver().strip()
            item['getPreserver'] = \
                preserver and self.user_fullname(preserver) or ''
            datepreserved = part.getDatePreserved()
            item['getDatePreserved'] = \
                datepreserved and self.ulocalized_time(datepreserved, long_format=False) or ''

            disposaldate = part.getDisposalDate()
            item['getDisposalDate'] = \
                disposaldate and self.ulocalized_time(disposaldate, long_format=False) or ''

            # inline edits for Container and Preservation
            if self.allow_edit:
                item['allow_edit'] = ['getContainer', 'getPreservation', 'SecuritySealIntact']
            item['choices']['getPreservation'] = preservations
            item['choices']['getContainer'] = containers

            # inline edits for Sampler and Date Sampled
##            checkPermission = self.context.portal_membership.checkPermission
##            if checkPermission(SampleSample, part) \
##                and not samplingdate > DateTime():
##                item['required'] += ['getSampler', 'getDateSampled']
##                item['allow_edit'] += ['getSampler', 'getDateSampled']
##                samplers = getUsers(part, ['Sampler', 'LabManager', 'Manager'])
##                getAuthenticatedMember = part.portal_membership.getAuthenticatedMember
##                username = getAuthenticatedMember().getUserName()
##                users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
##                         for u in samplers]
##                item['choices']['getSampler'] = users
##                item['getSampler'] = sampler and sampler or \
##                    (username in samplers.keys() and username) or ''
##                item['getDateSampled'] = item['getDateSampled'] \
##                    or DateTime().strftime(self.date_format_short)
##                item['class']['getSampler'] = 'provisional'
##                item['class']['getDateSampled'] = 'provisional'

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, part):
                item['required'] += ['getPreserver', 'getDatePreserved']
                if self.allow_edit:
                    item['allow_edit'] += ['getPreserver', 'getDatePreserved']
                preservers = getUsers(part, ['Preserver', 'LabManager', 'Manager'])
                getAuthenticatedMember = part.portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                item['choices']['getPreserver'] = users
                item['getPreserver'] = preserver and preserver or \
                    (username in preservers.keys() and username) or ''
                item['getDatePreserved'] = item['getDatePreserved'] \
                    or DateTime().strftime(self.date_format_short)
                item['class']['getPreserver'] = 'provisional'
                item['class']['getDatePreserved'] = 'provisional'

            items.append(item)

        items = sorted(items, key=itemgetter('id'))

        return items


class createSamplePartition(BrowserView):
    """create a new Sample Partition without an edit form
    """
    def __call__(self):
        wf = getToolByName(self.context, 'portal_workflow')
        part = _createObjectByType("SamplePartition", self.context, tmpID())
        part.processForm()
        SamplingWorkflowEnabled = part.bika_setup.getSamplingWorkflowEnabled()
        ## We force the object to have the same state as the parent
        sample_state = wf.getInfoFor(self.context, 'review_state')
        changeWorkflowState(part, "bika_sample_workflow", sample_state)
        self.request.RESPONSE.redirect(self.context.absolute_url() +
                                       "/partitions")
        return
