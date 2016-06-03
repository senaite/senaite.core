from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from plone.resource.utils import iterDirectoriesOfType
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import EditSample
from bika.lims import PMF
from bika.lims.utils import to_utf8, createPdf
from bika.lims import logger
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import *
from bika.lims.utils import changeWorkflowState, tmpID
from bika.lims.utils import changeWorkflowState, to_unicode
from bika.lims.utils import getUsers
from bika.lims.utils import isActive
from bika.lims.utils import to_utf8, getHiddenAttributesForClass
from operator import itemgetter
from bika.lims.workflow import doActionFor
from plone.app.layout.globals.interfaces import IViewView
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implements
from Products.ZCTextIndex.ParseTree import ParseError
import json
import os
import glob
import plone
import urllib
import traceback
import App
import tempfile


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
##                               'input_class': 'datepicker_nofuture',
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
             'custom_actions':[{'id': 'save_partitions_button',
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
            self.review_states[0]['custom_actions'] = []

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

class SampleAnalysesView(AnalysesView):
    """ This renders the Field and Lab analyses tables for Samples
    """
    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request)
        self.show_select_column = False
        self.allow_edit = False
        self.show_workflow_action_buttons = False
        for k,v in kwargs.items():
            self.contentFilter[k] = v
        self.columns['Request'] = {'title': _("Request"),
                                   'sortable':False}
        self.columns['Priority'] = {'title': _("Priority"),
                                   'sortable':False}
        # Add Request and Priority columns
        pos = self.review_states[0]['columns'].index('Service') + 1
        self.review_states[0]['columns'].insert(pos, 'Request')
        pos += 1
        self.review_states[0]['columns'].insert(pos, 'Priority')

    def folderitems(self):
        self.contentsMethod = self.context.getAnalyses
        items = AnalysesView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            ar = obj.aq_parent
            items[x]['replace']['Request'] = \
                "<a href='%s'>%s</a>"%(ar.absolute_url(), ar.Title())
            items[x]['replace']['Priority'] = ' ' #TODO this space is required for it to work
        return items

class SampleEdit(BrowserView):
    """
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample.pt")
    header_table = ViewPageTemplateFile("templates/header_table.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/sample_big.png"
        self.allow_edit = True

    def now(self):
        return DateTime()

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember()
        member_groups = [pg.getGroupById(group.id).getGroupName() \
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    def __call__(self):

        if 'transition' in self.request.form:
            doActionFor(self.context, self.request.form['transition'])

        ## render header table
        self.header_table = HeaderTableView(self.context, self.request)

        ## Create Sample Partitions table
        parts_table = None
        if not self.allow_edit:
            p = SamplePartitionsView(self.context, self.request)
            p.allow_edit = self.allow_edit
            p.show_select_column = self.allow_edit
            p.show_workflow_action_buttons = self.allow_edit
            p.show_column_toggles = False
            p.show_select_all_checkbox = False
            p.review_states[0]['transitions'] = [{'id': 'empty'},] # none
            parts_table = p.contents_table()
        self.parts = parts_table

        ## Create Field and Lab Analyses tables
        self.tables = {}
        if not self.allow_edit:
            for poc in POINTS_OF_CAPTURE:
                if not self.context.getAnalyses({'getPointOfCapture': poc}):
                    continue
                t = SampleAnalysesView(self.context,
                                 self.request,
                                 getPointOfCapture = poc,
                                 sort_on = 'getServiceTitle')
                t.form_id = "sample_%s_analyses" % poc
                if poc == 'field':
                    t.review_states[0]['columns'].remove('DueDate')
                t.show_column_toggles = False
                t.review_states[0]['transitions'] = [{'id':'submit'},
                                                     {'id':'retract'},
                                                     {'id':'verify'}]
                self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()

        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

class SampleView(SampleEdit):
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)

class SamplesView(BikaListingView):
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
            'getSamplingDate': {'title': _('Sampling Date'),
                                'index':'getSamplingDate',
                                'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index':'getDateSampled',
                               'toggle': SamplingWorkflowEnabled,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': SamplingWorkflowEnabled},
            'getScheduledSamplingSampler': {
                'title': _('Sampler for scheduled sampling'),
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
            {'id':'default',
             'title': _('Active'),
             'contentFilter':{'cancellation_state':'active',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'state_title'],
             'transitions': [
                {'id': 'schedule_sampling'}, {'id': 'sample'}],
             },
            {'id':'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_preserved',
                                                'sample_due'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'state_title']},
            {'id':'sample_received',
             'title': _('Received'),
             'contentFilter':{'review_state':'sample_received',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
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
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'DateReceived',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'state_title']},
        ]

    def folderitems(self, full_objects = False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        translate = self.context.translate
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            items[x]['replace']['getSampleID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getSampleID())
            items[x]['replace']['Requests'] = ",".join(
                ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
                 for o in obj.getAnalysisRequests()])
            items[x]['Client'] = obj.aq_parent.Title()
            if hideclientlink == False:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            items[x]['Creator'] = self.user_fullname(obj.Creator())

            items[x]['DateReceived'] = self.ulocalized_time(obj.getDateReceived())

            deviation = obj.getSamplingDeviation()
            items[x]['SamplingDeviation'] = deviation and deviation.Title() or ''

            items[x]['getStorageLocation'] = obj.getStorageLocation() and obj.getStorageLocation().Title() or ''
            items[x]['AdHoc'] = obj.getAdHoc() and True or ''

            items[x]['Created'] = self.ulocalized_time(obj.created())

            samplingdate = obj.getSamplingDate()
            items[x]['getSamplingDate'] = self.ulocalized_time(samplingdate, long_format=1)

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='%s' " \
                    "src='%s/++resource++bika.lims.images/hazardous.png'>" % \
                    (t(_("Hazardous")),
                     self.portal_url)
            if obj.getSamplingDate() > DateTime():
                after_icons += "<img title='%s' " \
                    "src='%s/++resource++bika.lims.images/calendar.png' >" % \
                    (t(_("Future dated sample")),
                     self.portal_url)
            if after_icons:
                items[x]['after']['getSampleID'] = after_icons

            SamplingWorkflowEnabled =\
                self.context.bika_setup.getSamplingWorkflowEnabled()

            if not samplingdate > DateTime() \
                    and SamplingWorkflowEnabled:
                datesampled = self.ulocalized_time(obj.getDateSampled())
                if not datesampled:
                    datesampled = self.ulocalized_time(DateTime())
                    items[x]['class']['getDateSampled'] = 'provisional'
                sampler = obj.getSampler().strip()
                if sampler:
                    items[x]['replace']['getSampler'] = self.user_fullname(sampler)
                if 'Sampler' in member.getRoles() and not sampler:
                    sampler = member.id
                    items[x]['class']['getSampler'] = 'provisional'
            else:
                datesampled = ''
                sampler = ''
            items[x]['getDateSampled'] = datesampled
            items[x]['getSampler'] = sampler
            # sampling workflow - inline edits for Sampler, Date Sampled and
            # Scheduled Sampling Sampler
            checkPermission = self.context.portal_membership.checkPermission
            state = workflow.getInfoFor(obj, 'review_state')
            if state in ['to_be_sampled', 'scheduled_sampling']:
                items[x]['required'] = []
                items[x]['allow_edit'] = []
                items[x]['choices'] = {}
                samplers = getUsers(obj, ['Sampler', 'LabManager', 'Manager'])
                users = [(
                    {'ResultValue': u, 'ResultText': samplers.getValue(u)})
                    for u in samplers]
                # both situations
                if checkPermission(SampleSample, obj) or\
                        self._schedule_sampling_permissions():
                    items[x]['required'].append('getSampler')
                    items[x]['allow_edit'].append('getSampler')
                    items[x]['choices']['getSampler'] = users
                # sampling permissions
                if checkPermission(SampleSample, obj):
                    getAuthenticatedMember = self.context.\
                        portal_membership.getAuthenticatedMember
                    username = getAuthenticatedMember().getUserName()
                    Sampler = sampler and sampler or \
                        (username in samplers.keys() and username) or ''
                    items[x]['required'].append('getDateSampled')
                    items[x]['allow_edit'].append('getDateSampled')
                    items[x]['getSampler'] = Sampler
                # coordinator permissions
                if self._schedule_sampling_permissions():
                    items[x]['required'].append('getSamplingDate')
                    items[x]['allow_edit'].append('getSamplingDate')
                    items[x]['required'].append('getScheduledSamplingSampler')
                    items[x]['allow_edit'].append(
                        'getScheduledSamplingSampler')
                    items[x]['choices']['getScheduledSamplingSampler'] = users
            # These don't exist on samples
            # the columns exist just to set "preserve" transition from lists.
            # XXX This should be a list of preservers...
            items[x]['getPreserver'] = ''
            items[x]['getDatePreserved'] = ''

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                preserver = username in preservers.keys() and username or ''
                items[x]['getPreserver'] = preserver
                items[x]['getDatePreserved'] = self.ulocalized_time(DateTime())
                items[x]['class']['getPreserver'] = 'provisional'
                items[x]['class']['getDatePreserved'] = 'provisional'

        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
        # Hide schedule_sampling if user has no rights
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i,state in enumerate(self.review_states):
            if state['id'] == self.review_state.get('id', ''):
                if 'getSampler' not in toggle_cols \
                   or 'getDateSampled' not in toggle_cols:
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


class SamplesPrint(BrowserView):
    """
    This class manages all the logic needed to create a form which is going
    to be printed.
    The sampler will be able to print the form and take it to
    the defined sampling points.
    The class receives the samples selected in the SamplesView in order to
    generate the form.
    If no samples are selected, the system will get all the samples with the
    states 'to_be_sampled' or 'scheduled_sampling'.
    The system will gather field analysis services using the following pattern:

    Sampler_1 - Client_1 - Date_1 - SamplingPoint_1 - Field_AS_1.1
                                                    - Field_AS_1.2
                                  - SamplingPoint_2 - Field_AS_2.1
                         - Date_3 - SamplingPoint_1 - Field_AS_3.1
              - Client_2 - Date_1 - SamplingPoint_1 - Field_AS_4.1

    Sampler_2 - Client_1 - Date_1 - SamplingPoint_1 - Field_AS_5.1
    """
    template = ViewPageTemplateFile("templates/samples_print_form.pt")
    _DEFAULT_TEMPLATE = 'default_form.pt'
    _TEMPLATES_DIR = 'templates/samplesprint'
    _TEMPLATES_ADDON_DIR = 'samples'
    # selected samples
    _items = []

    def __call__(self):
        if self.context.portal_type == 'SamplesFolder':
            if self.request.get('items', ''):
                uids = self.request.get('items').split(',')
                uc = getToolByName(self.context, 'uid_catalog')
                self._items = [obj.getObject() for obj in uc(UID=uids)]
            else:
                catalog = getToolByName(self.context, 'portal_catalog')
                contentFilter = {
                    'portal_type': 'Sample',
                    'sort_on': 'created',
                    'sort_order': 'reverse',
                    'review_state': ['to_be_sampled', 'scheduled_sampling'],
                    'path': {'query': "/", 'level': 0}
                    }
                brains = catalog(contentFilter)
                self._items = [obj.getObject() for obj in brains]
        else:
            # Warn and redirect to referer
            logger.warning(
                'PrintView: type not allowed: %s \n' % self.context.portal_type)
            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())

        # Do print?
        if self.request.form.get('pdf', '0') == '1':
            response = self.request.response
            response.setHeader("Content-type", "application/pdf")
            response.setHeader("Content-Disposition", "inline")
            response.setHeader("filename", "temp.pdf")
            return self.pdfFromPOST()
        else:
            return self.template()

    def _rise_error(self):
        """
        Give the error missage
        """
        tbex = traceback.format_exc()
        logger.error(
            'An error occurred while rendering the view: %s' % tbex)
        self.destination_url = self.request.get_header(
            "referer", self.context.absolute_url())

    def getSortedFilteredSamples(self):
        """
        This function returns all the samples sorted and filtered
        This function returns a dictionary as:
        {
            sampler1:{
                info:{,},
                client1:{
                    info:{,},
                    date1:{
                        [sample_tables]
                    },
                    no_date:{
                        [sample_tables]
                    }
                }
            }
        }
        """
        samples = self._items
        result = {}
        for sample in samples:
            pc = getToolByName(self, 'portal_catalog')
            # Getting the filter keys
            sampler_id = sample.getScheduledSamplingSampler()
            sampler_brain = pc(
                portal_type='LabContact', getUsername=sampler_id)
            sampler_obj = sampler_brain[0].getObject()\
                if sampler_brain else None
            if sampler_obj:
                sampler_uid = sampler_obj.UID()
                sampler_name = sampler_obj.getFullname() if sampler_obj else 'No sampler'
            else:
                sampler_uid = 'no_sampler'
                sampler_name = ''
            client_uid = sample.getClientUID()
            date = \
                self.ulocalized_time(sample.getSamplingDate(), long_format=0)\
                if sample.getSamplingDate() else ''
            # Filling the dictionary
            if sampler_uid in result.keys():
                client_d = result[sampler_uid].get(client_uid, {})
                # Always write the info again.
                # Is it faster than doing a check every time?
                client_d['info'] = {'name': sample.getClientTitle()}
                if date:
                    c_l = client_d.get(date, [])
                    c_l.append(
                        self._sample_table_builder(sample))
                    client_d[date] = c_l
                else:
                    c_l = client_d.get('no_date', [])
                    c_l.append(
                        self._sample_table_builder(sample))
                    client_d[date] = c_l
            else:
                # This sampler isn't in the dict yet.
                # Write the client dict
                client_dict = {
                    'info': {
                        'name': sample.getClientTitle()
                        },
                    }
                # If the sample has a sampling date, build the dictionary
                # which emulates the table inside a list
                if date:
                    client_dict[date] = [
                        self._sample_table_builder(sample)]
                else:
                    client_dict['no_date'] = [
                        self._sample_table_builder(sample)]
                # Adding the client dict inside the sampler dict
                result[sampler_uid] = {
                    'info': {
                        'obj': sampler_obj,
                        'id': sampler_id,
                        'name': sampler_name
                        },
                    client_uid: client_dict
                    }
        return result

    def _sample_table_builder(self, sample):
        """
        This function returns a list of dictionaries sorted by Sample
        Partition/Container. It emulates the columns/rows of a table.
        [{'requests and partition info'}, ...]
        """
        # rows will contain the data for each html row
        rows = []
        # columns will be used to sort and define the columns
        columns = {
            'column_order': [
                'sample_id',
                'sample_type',
                'sampling_point',
                'sampling_date',
                'partition',
                'container',
                'analyses',
                ],
            'titles': {
                'sample_id': _('Sample ID'),
                'sample_type': _('Sample Type'),
                'sampling_point': _('Sampling Point'),
                'sampling_date': _('Sampling Date'),
                'partition': _('Partition'),
                'container': _('Container'),
                'analyses': _('Analysis'),
            }
        }
        ars = sample.getAnalysisRequests()
        for ar in ars:
            arcell = False
            numans = len(ar.getAnalyses())
            for part in ar.getPartitions():
                partcell = False
                container = part.getContainer().title \
                    if part.getContainer() else ''
                partans = part.getAnalyses()
                numpartans = len(partans)
                for analysis in partans:
                    service = analysis.getService()
                    if service.getPointOfCapture() == 'field':
                        row = {
                            'sample_id': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value': ar.getSample().id,
                                },
                            'sample_type': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value': ar.getSampleType().title,
                                },
                            'sampling_point': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value':
                                    ar.getSamplePoint().title
                                    if ar.getSamplePoint() else '',
                                },
                            'sampling_date': {
                                'hidden': True if arcell else False,
                                'rowspan': numans,
                                'value':  self.ulocalized_time(sample.getSamplingDate(), long_format=0),
                                },
                            'partition': {
                                'hidden': True if partcell else False,
                                'rowspan': numpartans,
                                'value': part.id,
                                },
                            'container': {
                                'hidden': True if partcell else False,
                                'rowspan': numpartans,
                                'value': container,
                                },
                            'analyses': {
                                'title': service.title,
                                'units': service.getUnit(),
                            },
                        }
                        rows.append(row)
                        arcell = True
                        partcell = True

        # table will contain the data that from where the html
        # will take the info
        table = {
            'columns': columns,
            'rows': rows,
        }
        return table

    def getAvailableTemplates(self):
        """
        Returns a DisplayList with the available templates found in
        browser/templates/samplesprint
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        for templates_resource in iterDirectoriesOfType(
                self._TEMPLATES_ADDON_DIR):
            prefix = templates_resource.__name__
            templates = [
                tpl for tpl in templates_resource.listDirectory()
                if tpl.endswith('.pt')
                ]
            for template in templates:
                out.append({
                    'id': '{0}:{1}'.format(prefix, template),
                    'title': '{0} ({1})'.format(template[:-3], prefix),
                })
        return out

    def getFormTemplate(self):
        """Returns the selected samples rendered using the template
            specified in the request (param 'template').
        """
        templates_dir = self._TEMPLATES_DIR
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, embedt = embedt.split(':')
            templates_dir = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix).directory
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            reptemplate = \
                "<div class='error-print'>%s '%s':<pre>%s</pre></div>" %\
                (_("Unable to load the template"), embedt, tbex)
        return reptemplate

    def getCSS(self):
        """ Returns the css style to be used for the current template.
            If the selected template is 'default.pt', this method will
            return the content from 'default.css'. If no css file found
            for the current template, returns empty string
        """
        template = self.request.get('template', self._DEFAULT_TEMPLATE)
        content = ''
        if template.find(':') >= 0:
            prefix, template = template.split(':')
            resource = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
            path = '%s/%s.css' % (templates_dir, template[:-3])
            with open(path, 'r') as content_file:
                content = content_file.read()
        return content

    def pdfFromPOST(self):
        """
        It returns the pdf with the printed form
        """
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html)
        return self.printFromHTML(safe_unicode(reporthtml).encode('utf-8'))

    def printFromHTML(self, code_html):
        """
        Tis function generates a pdf file from the html
        :code_html: the html to use to generate the pdf
        """
        # HTML written to debug file
        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".html")
            open(tmp_fn, "wb").write(code_html)

        # Creates the pdf
        # we must supply the file ourself so that createPdf leaves it alone.
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_report = createPdf(htmlreport=code_html, outfile=pdf_fn)
        return pdf_report

    def getSamplers(self):
        """
        Returns a dictionary of dictionaries with info about the samplers
        defined in each sample.
        {
            'uid': {'id':'xxx', 'name':'xxx'},
            'uid': {'id':'xxx', 'name':'xxx'}, ...}
        """
        samplers = {}
        for sample in self._items:
            sampler = sample.getSampler()
            if sampler and sample.UID() not in samplers.keys():
                samplers[sampler.UID()] = {
                    'id': sampler.id,
                    'name': sampler.getName()
                }
        return samplers

    def getClients(self):
        """
        Returns a dictionary of dictionaries with info about the clients
        related to the selected samples.
        {
            'uid': {'name':'xxx'},
            'uid': {'name':'xxx'}, ...}
        """
        clients = {}
        for sample in self._items:
            if sample.getClientUID() not in clients.keys():
                clients[sample.getClientUID()] = {
                    'name': sample.getClientTitle()
                }
        return clients

    def getLab(self):
        return self.context.bika_setup.laboratory.getLabURL()

    def getLogo(self):
        portal = self.context.portal_url.getPortalObject()
        return "%s/logo_print.png" % portal.absolute_url()


class ajaxGetSampleTypeInfo(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uid = self.request.get('UID', '')
        title = self.request.get('Title', '')
        ret = {
               'UID': '',
               'Title': '',
               'Prefix': '',
               'Hazardous': '',
               'SampleMatrixUID': '',
               'SampleMatrixTitle': '',
               'MinimumVolume':  '',
               'ContainerTypeUID': '',
               'ContainerTypeTitle': '',
               'SamplePoints': ('',),
               'StorageLocations': ('',),
               }
        proxies = None
        if uid:
            try:
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                proxies = bsc(UID=uid)
            except ParseError:
                pass
        elif title:
            try:
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                proxies = bsc(portal_type='SampleType', title=to_unicode(title))
            except ParseError:
                pass

        if proxies and len(proxies) == 1:
            st = proxies[0].getObject();
            ret = {
               'UID': st.UID(),
               'Title': st.Title(),
               'Prefix': st.getPrefix(),
               'Hazardous': st.getHazardous(),
               'SampleMatrixUID': st.getSampleMatrix() and \
                                  st.getSampleMatrix().UID() or '',
               'SampleMatrixTitle': st.getSampleMatrix() and \
                                  st.getSampleMatrix().Title() or '',
               'MinimumVolume':  st.getMinimumVolume(),
               'ContainerTypeUID': st.getContainerType() and \
                                   st.getContainerType().UID() or '',
               'ContainerTypeTitle': st.getContainerType() and \
                                     st.getContainerType().Title() or '',
               'SamplePoints': dict((sp.UID(),sp.Title()) for sp in st.getSamplePoints()),
               'StorageLocations': dict((sp.UID(),sp.Title()) for sp in st.getStorageLocations()),
               }

        return json.dumps(ret)
