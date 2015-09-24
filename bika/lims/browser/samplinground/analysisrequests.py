from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as _ARAV
from bika.lims.browser.analysisrequest import AnalysisRequestsView as _ARV
from bika.lims.permissions import *
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from bika.lims.utils import t
from copy import copy


class AnalysisRequestsView(_ARV, _ARAV):
    ar_add = ViewPageTemplateFile("../analysisrequest/templates/ar_add.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()
        self.columns = {
            'partition': {'title': _('Partition ID'),
                          'toggle': True},
            'securitySealIntact': {'title': _('Security Seal Intact'),
                                  'toggle': True},
            'samplingRoundTemplate': {'title': _('Sampling Round Template'),
                                      'toggle': True},
            'getRequestID': {'title': _('Request ID'),
                             'index': 'getRequestID'},
            'getSample': {'title': _("Sample"),
                          'toggle': True, },
            'Priority': {'title': _('Priority'),
                            'toggle': True,
                            'index': 'Priority',
                            'sortable': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index': 'getDateSampled',
                               'toggle': True,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
            'getProfilesTitle': {'title': _('Profile'),
                                'index': 'getProfilesTitle',
                                'toggle': False},
            'getTemplateTitle': {'title': _('Template'),
                                 'index': 'getTemplateTitle',
                                 'toggle': False},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'cancellation_state': 'active',
                              'sort_on': 'created',
                              'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'preserve'},
                             {'id': 'receive'},
                             {'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'to_be_preserved',
                                                'sample_due'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'preserve'},
                             {'id': 'receive'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state': 'to_be_verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published', 'invalid'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': ('to_be_sampled', 'to_be_preserved',
                                                'sample_due', 'sample_received',
                                                'to_be_verified', 'attachment_due',
                                                'verified', 'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'assigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/assigned.png'/>" % (
                       t(_("Assigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'assigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            {'id': 'unassigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/unassigned.png'/>" % (
                       t(_("Unassigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'unassigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'receive'},
                             {'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['partition',
                         'securitySealIntact',
                         'getRequestID',
                         'samplingRoundTemplate',
                         'getSample',
                         'Priority',
                         'getDateSampled',
                         'state_title']},
            ]

    def contentsMethod(self, contentFilter):
        pc = getToolByName(self.context, 'portal_catalog')
        if 'SamplingRoundUID' not in contentFilter.keys():
            contentFilter['SamplingRoundUID'] = self.context.UID()
        return pc(contentFilter)

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # We give the number of analysis request templates in order to fill out the analysis request form
            # automatically :)
            num_art = len(self.context.ar_templates)
            self.context_actions[self.context.translate(_('Add new'))] = {
                'url': self.context.aq_parent.absolute_url() + \
                    "/portal_factory/"
                    "AnalysisRequest/Request new analyses/ar_add?samplinground="
                    + self.context.UID() + "&ar_count=" + str(num_art),
                'icon': '++resource++bika.lims.images/add.png'}
        return super(AnalysisRequestsView, self).__call__()

    def folderitems(self, full_objects=True):
        # In sampling rounds, analysis request list will be listed per Sample Partition/Container
        # Obtaining analysis requests
        items = _ARV.folderitems(self, full_objects)
        new_items = []
        for x in range(len(items)):
            if 'obj' not in items[x]:
                new_items.append(items[x])
                continue
            obj = items[x]['obj']
            # Getting the sampling round template uid
            srTemplateUID = obj.getSamplingRound().sr_template if obj.getSamplingRound().sr_template else ''
            # Getting the sampling round object
            catalog = getToolByName(self.context, 'uid_catalog')
            srTemplateObj = catalog(UID=srTemplateUID)[0].getObject() if catalog(UID=srTemplateUID) else None
            # Getting the partitions and creating a row per partition
            partitions = obj.getPartitions()
            for part in partitions:
                item = items[x].copy()
                # We ave to make a copy of 'replace' because it's a reference to a dict object
                item['replace'] = items[x]['replace'].copy()
                item['partition'] = part.id
                if part.getContainer():
                    img_url = '<img src="'+self.portal_url+'/++resource++bika.lims.images/ok.png"/>'
                    item['securitySealIntact'] = part.getContainer().getSecuritySealIntact()
                    item['replace']['securitySealIntact'] = img_url \
                        if part.getContainer().getSecuritySealIntact() else ' '
                else:
                    item['securitySealIntact'] = ' '
                item['replace']['partition'] = "<a href='%s'>%s</a>" % (part.absolute_url(), item['partition'])
                item['samplingRoundTemplate'] = srTemplateObj.title if srTemplateObj else ''
                if srTemplateObj:
                    item['replace']['samplingRoundTemplate'] = \
                        "<a href='%s'>%s</a>" % (srTemplateObj.absolute_url, item['samplingRoundTemplate'])
                new_items.append(item)
        return new_items
