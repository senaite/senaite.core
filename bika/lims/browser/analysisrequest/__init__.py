from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.adapters.referencewidgetvocabulary import DefaultReferenceWidgetVocabulary
from bika.lims.adapters.widgetvisibility import WidgetVisibility as _WV
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.jsonapi import get_include_fields
from bika.lims.jsonapi import load_brain_metadata
from bika.lims.jsonapi import load_field_values
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.permissions import *
from bika.lims.workflow import get_workflow_actions
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getAdapters
from zope.interface import implements

import json
import plone

from .view import AnalysisRequestViewView    # view first.
from .add import AnalysisRequestAddView
from .invoice import InvoicePrintView
from .invoice import InvoiceView
from .log import AnalysisRequestLog
from .manage_analyses import AnalysisRequestAnalysesView
from .manage_results import AnalysisRequestManageResultsView
from .published_results import AnalysisRequestPublishedResults
from .results_not_requested import AnalysisRequestResultsNotRequestedView
from .workflow import AnalysisRequestWorkflowAction


class ResultOutOfRange(object):

    """Return alerts for any analyses inside the context ar
    """
    implements(IFieldIcons)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter(obj)
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        parent = self.context.aq_parent
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(parent.getPhysicalPath()),
                  'level': 0}
        )


class WidgetVisibility(_WV):

    def __call__(self):
        ret = super(WidgetVisibility, self).__call__()
        workflow = getToolByName(self.context, 'portal_workflow')
        state = workflow.getInfoFor(self.context, 'review_state')
        if 'add' not in ret:
            ret['add'] = {}
        if 'visible' not in ret['add']:
            ret['add']['visible'] = []
        if 'hidden' not in ret['add']:
            ret['add']['hidden'] = []
        if self.context.aq_parent.portal_type == 'Client':
            ret['add']['visible'].remove('Client')
            ret['add']['hidden'].append('Client')
        if self.context.aq_parent.portal_type == 'Batch':
            ret['add']['visible'].remove('Batch')
            ret['add']['hidden'].append('Batch')
        # header_table default visible fields
        ret['header_table'] = {
            'prominent': ['Contact', 'CCContact', 'CCEmails'],
            'visible': [
                'Contact',
                'CCContact',
                'CCEmails',
                'Sample',
                'Batch',
                'SubGroup',
                'Template',
                'Profile',
                'SamplingDate',
                'SampleType',
                'Specification',
                'PublicationSpecification',
                'SamplePoint',
                'StorageLocation',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'SamplingDeviation',
                'Priority',
                'SampleCondition',
                'DateSampled',
                'DateReceived',
                'DatePublished',
                'ReportDryMatter',
                'AdHoc',
                'Composite',
                'MemberDiscount',
                'InvoiceExclude',
                ]}
        # Edit and View widgets are displayed/hidden in different workflow
        # states.  The widget.visible is used as a default.  This is placed
        # here to manage the header_table display.
        if state in ('to_be_sampled', 'to_be_preserved', 'sample_due', ):
            ret['header_table']['visible'].remove('DateReceived')
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Batch',
                'SubGroup',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'InvoiceExclude'
                'SampleCondition',
                'SamplePoint',
                'SampleType',
                'SamplingDate',
                'StorageLocation',
                'SamplingDeviation',
                'Priority',
            ]
            ret['view']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'DateSampled',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Specification',
                'Sample',
                'Template',
            ]
        elif state in ('sample_received', ):
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'Batch',
                'SubGroup',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'SampleType',
                'SamplePoint',
                'StorageLocation',
                'InvoiceExclude',
                'Priority',
            ]
            ret['view']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Composite',
                'DateReceived',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'Specification',
                'SamplingDate',
                'SamplingDeviation',
                'Template',
            ]
        # include this in to_be_verified - there may be verified analyses to
        # pre-publish
        elif state in ('to_be_verified', 'verified', ):
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'PublicationSpecification',
                'StorageLocation',
                'Priority',
            ]
            ret['view']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Batch',
                'SubGroup',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'DateReceived',
                'InvoiceExclude',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'SamplePoint',
                'Specification',
                'SampleType',
                'SamplingDate',
                'SamplingDeviation',
                'Template',
            ]
        elif state in ('published', ):
            ret['edit']['visible'] = [
                'StorageLocation',
                'PublicationSpecification',
            ]
            ret['view']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Batch',
                'SubGroup',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'DatePublished',
                'DateReceived',
                'InvoiceExclude'
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'SamplePoint',
                'Specification',
                'SampleType',
                'SamplingDate',
                'SamplingDeviation',
                'Priority',
                'Template',
            ]

        return ret


class ReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):

    def __call__(self):
        base_query = json.loads(self.request['base_query'])
        # In client context, restrict samples to client samples only
        if 'portal_type' in base_query \
        and (base_query['portal_type'] == 'Sample'
             or base_query['portal_type'][0] == 'Sample'):
            base_query['getClientUID'] = self.context.aq_parent.UID()
            self.request['base_query'] = json.dumps(base_query)
        return DefaultReferenceWidgetVocabulary.__call__(self)


class JSONReadExtender(object):

    """- Adds the full details of all analyses to the AR.Analyses field
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def ar_analysis_values(self):
        ret = []
        analyses = self.context.getAnalyses(cancellation_state='active')
        for proxy in analyses:
            analysis = proxy.getObject()
            service = analysis.getService()
            if proxy.review_state == 'retracted':
                # these are scraped up when Retested analyses are found below.
                continue
            # things that are manually inserted into the analysis.
            # These things will be included even if they are not present in
            # include_fields in the request.
            method = analysis.getMethod()
            if not method:
                method = service.getMethod()
            service = analysis.getService()
            hs = hasattr(analysis, "specification")
            analysis_data = {
                "Uncertainty": service.getUncertainty(analysis.getResult()),
                "Method": method.Title() if method else '',
                "specification": analysis.specification if hs else {},
            }
            # Place all schema fields ino the result.
            analysis_data.update(load_brain_metadata(proxy, []))
            # Place all schema fields ino the result.
            analysis_data.update(load_field_values(analysis, []))
            # call any adapters that care to modify the Analysis data.
            # adapters = getAdapters((analysis, ), IJSONReadExtender)
            # for name, adapter in adapters:
            #     adapter(request, analysis_data)
            if self.include_fields and "transitions" in self.include_fields:
                analysis_data['transitions'] = get_workflow_actions(analysis)
            if analysis.getRetested():
                retracted = self.context.getAnalyses(review_state='retracted',
                                            title=analysis.Title(),
                                            full_objects=True)
                prevs = sorted(retracted, key=lambda item: item.created())
                prevs = [{'created': str(p.created()),
                          'Result': p.getResult(),
                          'InterimFields': p.getInterimFields()}
                         for p in prevs]
                analysis_data['Previous Results'] = prevs
            ret.append(analysis_data)
        return ret

    def __call__(self, request, data):
        self.request = request
        self.include_fields = get_include_fields(request)
        if not self.include_fields or "Analyses" in self.include_fields:
            data['Analyses'] = self.ar_analysis_values()
        return data


class PriorityIcons(object):

    """An icon provider for indicating AR priorities
    """

    implements(IFieldIcons)
    # adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        result = {
            'msg': '',
            'field': 'Priority',
            'icon': '',
        }
        priority = self.context.getPriority()
        if priority:
            result['msg'] = priority.Title()
            icon = priority.getSmallIcon()
            if icon:
                result['icon'] = '/'.join(icon.getPhysicalPath())
            return {self.context.UID(): [result]}
        return {}


class mailto_link_from_contacts:

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        contacts = field.get(self.context)
        if not type(contacts) in (list, tuple):
            contacts = [contacts, ]
        ret = []
        for contact in contacts:
            mailto = "<a href='mailto:%s'>%s</a>" % (
                contact.getEmailAddress(), contact.getFullname())
            ret.append(mailto)
        return ",".join(ret)


def mailto_link_from_ccemails(ccemails):
    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        ccemails = field.get(self.context)
        addresses = ccemails.split(",")
        ret = []
        for address in addresses:
            mailto = "<a href='mailto:%s'>%s</a>" % (
                address, address)
            ret.append(mailto)
        return ",".join(ret)


class AnalysisRequestsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'AnalysisRequest',
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'path': {"query": "/", "level": 0}
                              }

        self.context_actions = {}

        if self.context.portal_type == "AnalysisRequestsFolder":
            self.request.set('disable_border', 1)

        if self.view_url.find("analysisrequests") == -1:
            self.view_url = self.view_url + "/analysisrequests"

        translate = self.context.translate

        self.allow_edit = True

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.form_id = "analysisrequests"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.title = _("Analysis Requests")
        self.description = ""

        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        user_is_preserver = 'Preserver' in member.getRoles()

        self.columns = {
            'getRequestID': {'title': _('Request ID'),
                             'index': 'getRequestID'},
            'getClientOrderNumber': {'title': _('Client Order'),
                                     'index': 'getClientOrderNumber',
                                     'toggle': True},
            'Creator': {'title': PMF('Creator'),
                                     'index': 'Creator',
                                     'toggle': True},
            'Created': {'title': PMF('Date Created'),
                        'index': 'created',
                        'toggle': False},
            'getSample': {'title': _("Sample"),
                          'toggle': True, },
            'BatchID': {'title': _("Batch ID"), 'toggle': True},
            'SubGroup': {'title': _('Sub-group')},
            'Client': {'title': _('Client'),
                       'toggle': True},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': True},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': True},
            'ClientContact': {'title': _('Contact'),
                                 'toggle': False},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle',
                                   'toggle': True},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'getStorageLocation': {'title': _('Storage Location'),
                                    'toggle': False},
            'SamplingDeviation': {'title': _('Sampling Deviation'),
                                  'toggle': False},
            'Priority': {'title': _('Priority'),
                            'index': 'Priority',
                            'toggle': True},
            'AdHoc': {'title': _('Ad-Hoc'),
                      'toggle': False},
            'SamplingDate': {'title': _('Sampling Date'),
                             'index': 'getSamplingDate',
                             'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index': 'getDateSampled',
                               'toggle': not SamplingWorkflowEnabled,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': not SamplingWorkflowEnabled},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10',
                                 'sortable': False},  # no datesort without index
            'getPreserver': {'title': _('Preserver'),
                             'toggle': user_is_preserver},
            'getDateReceived': {'title': _('Date Received'),
                                'index': 'getDateReceived',
                                'toggle': False},
            'getDatePublished': {'title': _('Date Published'),
                                 'index': 'getDatePublished',
                                 'toggle': False},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
            'getProfileTitle': {'title': _('Profile'),
                                'index': 'getProfileTitle',
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'ClientContact',
                        'getClientSampleID',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id': 'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'}],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id': 'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published', 'invalid'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished',
                        'state_title']},
            {'id': 'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
            {'id': 'assigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/assigned.png'/>" % (
                       to_utf8(self.context.translate(_("Assigned"))), self.portal_url),
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            {'id': 'unassigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/unassigned.png'/>" % (
                       to_utf8(self.context.translate(_("Unassigned"))), self.portal_url),
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
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            ]

    def folderitems(self, full_objects=False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            sample = obj.getSample()

            if getSecurityManager().checkPermission(EditResults, obj):
                url = obj.absolute_url() + "/manage_results"
            else:
                url = obj.absolute_url()

            items[x]['Client'] = obj.aq_parent.Title()
            if (hideclientlink is False):
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            items[x]['Creator'] = self.user_fullname(obj.Creator())
            items[x]['getRequestID'] = obj.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])
            items[x]['getSample'] = sample
            items[x]['replace']['getSample'] = \
                "<a href='%s'>%s</a>" % (sample.absolute_url(), sample.Title())

            batch = obj.getBatch()
            if batch:
                items[x]['BatchID'] = batch.getBatchID()
                items[x]['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                     (batch.absolute_url(), items[x]['BatchID'])
            else:
                items[x]['BatchID'] = ''

            val = obj.Schema().getField('SubGroup').get(obj)
            items[x]['SubGroup'] = val.Title() if val else ''

            samplingdate = obj.getSample().getSamplingDate()
            items[x]['SamplingDate'] = self.ulocalized_time(samplingdate, long_format=1)
            items[x]['getDateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['getDatePublished'] = self.ulocalized_time(obj.getDatePublished())

            deviation = sample.getSamplingDeviation()
            items[x]['SamplingDeviation'] = deviation and deviation.Title() or ''
            priority = obj.getPriority()
            items[x]['Priority'] = priority and priority.Title() or ''

            items[x]['getStorageLocation'] = sample.getStorageLocation() and sample.getStorageLocation().Title() or ''
            items[x]['AdHoc'] = sample.getAdHoc() and True or ''

            after_icons = ""
            state = workflow.getInfoFor(obj, 'worksheetanalysis_review_state')
            if state == 'assigned':
                after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("All analyses assigned"))))
            if workflow.getInfoFor(obj, 'review_state') == 'invalid':
                after_icons += "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'/>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("Results have been withdrawn"))))
            if obj.getLate():
                after_icons += "<img src='%s/++resource++bika.lims.images/late.png' title='%s'>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("Late Analyses"))))
            if samplingdate > DateTime():
                after_icons += "<img src='%s/++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("Future dated sample"))))
            if obj.getInvoiceExclude():
                after_icons += "<img src='%s/++resource++bika.lims.images/invoice_exclude.png' title='%s'>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("Exclude from invoice"))))
            if sample.getSampleType().getHazardous():
                after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                    (self.portal_url, to_utf8(self.context.translate(_("Hazardous"))))
            if after_icons:
                items[x]['after']['getRequestID'] = after_icons

            items[x]['Created'] = self.ulocalized_time(obj.created())

            SamplingWorkflowEnabled =\
                self.context.bika_setup.getSamplingWorkflowEnabled()

            if not samplingdate > DateTime() and SamplingWorkflowEnabled:
                datesampled = self.ulocalized_time(sample.getDateSampled())

                if not datesampled:
                    datesampled = self.ulocalized_time(
                        DateTime(),
                        long_format=1)
                    items[x]['class']['getDateSampled'] = 'provisional'
                sampler = sample.getSampler().strip()
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

            items[x]['ClientContact'] = obj.getContact().Title()
            items[x]['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (obj.getContact().absolute_url(), obj.getContact().Title())

            # sampling workflow - inline edits for Sampler and Date Sampled
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(SampleSample, obj) \
                and not samplingdate > DateTime():
                items[x]['required'] = ['getSampler', 'getDateSampled']
                items[x]['allow_edit'] = ['getSampler', 'getDateSampled']
                samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
                         for u in samplers]
                items[x]['choices'] = {'getSampler': users}
                Sampler = sampler and sampler or \
                    (username in samplers.keys() and username) or ''
                items[x]['getSampler'] = Sampler

            # These don't exist on ARs
            # XXX This should be a list of preservers...
            items[x]['getPreserver'] = ''
            items[x]['getDatePreserved'] = ''

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                preserver = username in preservers.keys() and username or ''
                items[x]['getPreserver'] = preserver
                items[x]['getDatePreserved'] = self.ulocalized_time(
                    DateTime(),
                    long_format=1)
                items[x]['class']['getPreserver'] = 'provisional'
                items[x]['class']['getDatePreserved'] = 'provisional'

            # Submitting user may not verify results
            if items[x]['review_state'] == 'to_be_verified' and \
               not checkPermission(VerifyOwnResults, obj):
                self_submitted = False
                try:
                    review_history = list(workflow.getInfoFor(obj, 'review_history'))
                    review_history.reverse()
                    for event in review_history:
                        if event.get('action') == 'submit':
                            if event.get('actor') == member.getId():
                                self_submitted = True
                            break
                    if self_submitted:
                        items[x]['after']['state_title'] = \
                             "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                             (to_utf8(self.context.translate(_("Cannot verify: Submitted by current user"))))
                except Exception:
                    pass

        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i, state in enumerate(self.review_states):
            if state['id'] == self.review_state:
                if 'getSampler' not in toggle_cols \
                   or 'getDateSampled' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('sample')
                    else:
                        state['hide_transitions'] = ['sample', ]
                if 'getPreserver' not in toggle_cols \
                   or 'getDatePreserved' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('preserve')
                    else:
                        state['hide_transitions'] = ['preserve', ]
            new_states.append(state)
        self.review_states = new_states

        return items
