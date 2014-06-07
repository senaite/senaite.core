import plone, json
import zope.event

from bika.lims.permissions import *

from AccessControl import getSecurityManager
from Acquisition import aq_parent, aq_inner
from bika.lims import PMF, logger, bikaMessageFactory as _
from bika.lims.adapters.referencewidgetvocabulary import DefaultReferenceWidgetVocabulary
from bika.lims.adapters.widgetvisibility import WidgetVisibility as _WV
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction
from bika.lims.browser.batchfolder import BatchFolderContentsView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.publish import doPublish
from bika.lims.browser.sample import SamplesView
from bika.lims.browser.supplyorderfolder import SupplyOrderFolderView
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IContacts
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.subscribers import doActionFor, skip
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import isActive
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.vocabularies import CatalogVocabulary
from DateTime import DateTime
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements


class ClientWorkflowAction(AnalysisRequestWorkflowAction):
    """ This function is called to do the worflow actions
        that apply to objects transitioned directly from Client views

        The main lab 'analysisrequests' and 'samples' views also have
        workflow_action urls bound to this handler.

        The parent AnalysisRequestWorkflowAction handles
        AR and Sample context workflow actions (affecting parts/analyses)

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        self.context = aq_inner(self.context)
        workflow = getToolByName(self.context, 'portal_workflow')
        bc = getToolByName(self.context, 'bika_catalog')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        translate = self.context.translate
        checkPermission = self.context.portal_membership.checkPermission

        # use came_from to decide which UI action was clicked.
        # "workflow_action" is the action name specified in the
        # portal_workflow transition url.
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            # workflow_action_button is the action name specified in
            # the bika_listing_view table buttons.
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return

        if action == "sample":
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            transitioned = {'to_be_preserved':[], 'sample_due':[]}
            for obj_uid, obj in objects.items():
                if obj.portal_type == "AnalysisRequest":
                    ar = obj
                    sample = obj.getSample()
                else:
                    sample = obj
                    ar = sample.aq_parent
                # can't transition inactive items
                if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive':
                    continue
                if not checkPermission(SampleSample, sample):
                    continue

                # grab this object's Sampler and DateSampled from the form
                # (if the columns are available and edit controls exist)
                if 'getSampler' in form and 'getDateSampled' in form:
                    try:
                        Sampler = form['getSampler'][0][obj_uid].strip()
                        DateSampled = form['getDateSampled'][0][obj_uid].strip()
                    except KeyError:
                        continue
                    Sampler = Sampler and Sampler or ''
                    DateSampled = DateSampled and DateTime(DateSampled) or ''
                else:
                    continue

                # write them to the sample
                sample.setSampler(Sampler)
                sample.setDateSampled(DateSampled)
                sample.reindexObject()
                ars = sample.getAnalysisRequests()
                # Analyses and AnalysisRequets have calculated fields
                # that are indexed; re-index all these objects.
                for ar in ars:
                    ar.reindexObject()
                    analyses = sample.getAnalyses({'review_state':'to_be_sampled'})
                    for a in analyses:
                        a.getObject().reindexObject()

                # transition the object if both values are present
                if Sampler and DateSampled:
                    workflow.doActionFor(sample, action)
                    new_state = workflow.getInfoFor(sample, 'review_state')
                    doActionFor(ar, action)
                    transitioned[new_state].append(sample.Title())

            message = None
            for state in transitioned:
                tlist = transitioned[state]
                if len(tlist) > 1:
                    if state == 'to_be_preserved':
                        message = _('${items} are waiting for preservation.',
                                    mapping = {'items': ', '.join(tlist)})
                    else:
                        message = _('${items} are waiting to be received.',
                                    mapping = {'items': ', '.join(tlist)})
                    self.context.plone_utils.addPortalMessage(message, 'info')
                elif len(tlist) == 1:
                    if state == 'to_be_preserved':
                        message = _('${item} is waiting for preservation.',
                                    mapping = {'item': ', '.join(tlist)})
                    else:
                        message = _('${item} is waiting to be received.',
                                    mapping = {'item': ', '.join(tlist)})
                    self.context.plone_utils.addPortalMessage(message, 'info')
            if not message:
                message = _('No changes made.')
                self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        elif action == "preserve":
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            transitioned = {}
            not_transitioned = []
            for obj_uid, obj in objects.items():
                if obj.portal_type == "AnalysisRequest":
                    ar = obj
                    sample = obj.getSample()
                else:
                    sample = obj
                    ar = sample.aq_parent
                # can't transition inactive items
                if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive':
                    continue
                if not checkPermission(PreserveSample, sample):
                    continue

                # grab this object's Preserver and DatePreserved from the form
                # (if the columns are available and edit controls exist)
                if 'getPreserver' in form and 'getDatePreserved' in form:
                    try:
                        Preserver = form['getPreserver'][0][obj_uid].strip()
                        DatePreserved = form['getDatePreserved'][0][obj_uid].strip()
                    except KeyError:
                        continue
                    Preserver = Preserver and Preserver or ''
                    DatePreserved = DatePreserved and DateTime(DatePreserved) or ''
                else:
                    continue

                for sp in sample.objectValues("SamplePartition"):
                    if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved':
                        sp.setDatePreserved(DatePreserved)
                        sp.setPreserver(Preserver)
                for sp in sample.objectValues("SamplePartition"):
                    if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved':
                        if Preserver and DatePreserved:
                            doActionFor(sp, action)
                            transitioned[sp.aq_parent.Title()] = sp.Title()
                        else:
                            not_transitioned.append(sp)

            if len(transitioned.keys()) > 1:
                message = _('${items}: partitions are waiting to be received.',
                        mapping = {'items': ', '.join(transitioned.keys())})
            else:
                message = _('${item}: ${part} is waiting to be received.',
                        mapping = {'item': ', '.join(transitioned.keys()),
                                   'part': ', '.join(transitioned.values()),})
            self.context.plone_utils.addPortalMessage(message, 'info')

            # And then the sample itself
            if Preserver and DatePreserved and not not_transitioned:
                doActionFor(sample, action)
                #message = _('${item} is waiting to be received.',
                #            mapping = {'item': sample.Title()})
                #message = t(message)
                #self.context.plone_utils.addPortalMessage(message, 'info')

            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        elif action in ('prepublish', 'publish', 'republish'):
            # We pass a list of AR objects to Publish.
            # it returns a list of AR IDs which were actually published.
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            ARs_to_publish = []
            transitioned = []
            for obj_uid, obj in objects.items():
                if isActive(obj):
                    obj.setDatePublished(DateTime())
                    ARs_to_publish.append(obj)

            transitioned = self.doPublish(self.context,
                                   self.request,
                                   action,
                                   ARs_to_publish)()

            if len(transitioned) > 1:
                message = _('${items} were published.',
                            mapping = {'items': ', '.join(transitioned)})
            elif len(transitioned) == 1:
                message = _('${item} published.',
                            mapping = {'item': ', '.join(transitioned)})
            else:
                message = _('No items were published')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        else:
            AnalysisRequestWorkflowAction.__call__(self)

    def doPublish(self, context, request, action, analysis_requests):
        return doPublish(context, request, action, analysis_requests)


class ClientBatchesView(BatchFolderContentsView):
    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

    def __call__(self):
        # self.context_actions[_('Add')] = \
        #         {'url': '../../batches/createObject?type_name=Batch',
        #          'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}
        return BatchFolderContentsView.__call__(self)

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
        state = [x for x in self.review_states if x['id'] == self.review_state][0]
        batches = {}
        for ar in bc(portal_type = 'AnalysisRequest',
                     getClientUID = self.context.UID()):
            ar = ar.getObject()
            batch = ar.getBatch()
            if batch is not None:
                batches[batch.UID()] = batch
        return batches.values()

class ClientAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['path'] = {"query": "/".join(context.getPhysicalPath()),
                                      "level" : 0 }
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
        self.review_states = review_states

    def __call__(self):
        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        translate = self.context.translate
        # client contact required
        active_contacts = [c for c in self.context.objectValues('Contact') if
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if isActive(self.context):
            if self.context.portal_type == "Client" and not active_contacts:
                msg = _("Client contact required before request may be submitted")
                addPortalMessage(msg)
            else:
                if mtool.checkPermission(AddAnalysisRequest, self.context):
                    self.context_actions[t(_('Add'))] = {
                        'url': self.context.absolute_url() + "/portal_factory/"
                        "AnalysisRequest/Request new analyses/ar_add",
                        'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisRequestsView, self).__call__()

class ClientBatchAnalysisRequestsView(ClientAnalysisRequestsView):
    pass

class ClientSamplesView(SamplesView):
    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)

        self.contentFilter['path'] = {"query": "/".join(context.getPhysicalPath()),
                                      "level" : 0 }
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
        self.review_states = review_states

class ClientAnalysisProfilesView(BikaListingView):
    """This is displayed in the Profiles client action,
       in the "Analysis Profiles" tab
    """

    def __init__(self, context, request):
        super(ClientAnalysisProfilesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'AnalysisProfile',
            'sort_on':'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisprofiles"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisprofile_big.png"
        self.title = _("Analysis Profiles")
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'getProfileKey': {'title': _('Profile Key')},

        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title', 'Description', 'getProfileKey']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddAnalysisProfile, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=AnalysisProfile',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisProfilesView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientARTemplatesView(BikaListingView):
    """This is displayed in the Templates client action,
       in the "AR Templates" tab
    """

    def __init__(self, context, request):
        super(ClientARTemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'ARTemplate',
            'sort_on':'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "artemplates"
        self.icon = self.portal_url + "/++resource++bika.lims.images/artemplate_big.png"
        self.title = _("AR Templates")
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['title', 'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['title', 'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title', 'Description']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddARTemplate, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=ARTemplate',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientARTemplatesView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['title'] = obj.Title()
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientSamplePointsView(BikaListingView):
    """This is displayed in the "Sample Points" tab on each client
    """

    def __init__(self, context, request):
        super(ClientSamplePointsView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SamplePoint',
            'sort_on':'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "SamplePoints"
        self.icon = self.portal_url + "/++resource++bika.lims.images/samplepoint_big.png"
        self.title = _("Sample Points")
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['title', 'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['title', 'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title', 'Description']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddSamplePoint, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=SamplePoint',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientSamplePointsView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['title'] = obj.Title()
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientAnalysisSpecsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': 'AnalysisSpec',
            'sort_on':'sortable_title',
            'getClientUID': context.UID(),
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level" : 0
            }
        }
        self.context_actions = {}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisspecs"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisspec_big.png"
        self.title = _("Analysis Specifications")

        self.columns = {
            'Title': {'title': _('Title'),
                           'index': 'title'},
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 'SampleType']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if isActive(self.context):
            if checkPermission(AddAnalysisSpec, self.context):
                self.context_actions[_('Add')] = \
                    {'url': 'createObject?type_name=AnalysisSpec',
                     'icon': '++resource++bika.lims.images/add.png'}
            #
            # @lemoene with the changes made in AR-specs, I dont know how much
            # sense this makes anymore.
            # if checkPermission("Modify portal content", self.context):
            #     self.context_actions[_('Set to lab defaults')] = \
            #         {'url': 'set_to_lab_defaults',
            #          'icon': '++resource++bika.lims.images/analysisspec.png'}
        return super(ClientAnalysisSpecsView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['SampleType'] = obj.getSampleType().Title() \
                if obj.getSampleType() else ""
        return items

class SetSpecsToLabDefaults(BrowserView):
    """ Remove all client specs, and add copies of all lab specs
    """
    def __call__(self):
        form = self.request.form
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        # find and remove existing specs
        cs = bsc(portal_type = 'AnalysisSpec',
                  getClientUID = self.context.UID())
        if cs:
            self.context.manage_delObjects([s.id for s in cs])

        # find and duplicate lab specs
        ls = bsc(portal_type = 'AnalysisSpec',
                 getClientUID = self.context.bika_setup.bika_analysisspecs.UID())
        ls = [s.getObject() for s in ls]
        for labspec in ls:
            clientspec = _createObjectByType("AnalysisSpec", self.context, tmpID())
            clientspec.processForm()
            clientspec.edit(
                SampleType = labspec.getSampleType(),
                ResultsRange = labspec.getResultsRange(),
            )
        translate = self.context.translate
        message = _("Analysis specifications reset to lab defaults.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.request.RESPONSE.redirect(self.context.absolute_url() +
                                       "/analysisspecs")
        return

class ClientAttachmentsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Attachment',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "attachments"

        self.icon = self.portal_url + "/++resource++bika.lims.images/attachment_big.png"
        self.title = _("Attachments")
        self.description = ""

        self.columns = {
            'getTextTitle': {'title': _('Request ID')},
            'AttachmentFile': {'title': _('File')},
            'AttachmentType': {'title': _('Attachment Type')},
            'ContentType': {'title': _('Content Type')},
            'FileSize': {'title': _('Size')},
            'DateLoaded': {'title': _('Date Loaded')},
        }
        self.review_states = [
            {'id':'default',
             'title': 'All',
             'contentFilter':{},
             'columns': ['getTextTitle',
                         'AttachmentFile',
                         'AttachmentType',
                         'ContentType',
                         'FileSize',
                         'DateLoaded']},
        ]

    def lookupMime(self, name):
        mimetool = getToolByName(self, 'mimetypes_registry')
        mimetypes = mimetool.lookup(name)
        if len(mimetypes):
            return mimetypes[0].name()
        else:
            return name

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            obj_url = obj.absolute_url()
            file = obj.getAttachmentFile()
            icon = file.getBestIcon()

            items[x]['AttachmentFile'] = file.filename()
            items[x]['AttachmentType'] = obj.getAttachmentType().Title()
            items[x]['AttachmentType'] = obj.getAttachmentType().Title()
            items[x]['ContentType'] = self.lookupMime(file.getContentType())
            items[x]['FileSize'] = '%sKb' % (file.get_size() / 1024)
            items[x]['DateLoaded'] = obj.getDateLoaded()

            items[x]['replace']['getTextTitle'] = "<a href='%s'>%s</a>" % \
                 (obj_url, items[x]['getTextTitle'])

            items[x]['replace']['AttachmentFile'] = \
                 "<a href='%s/at_download/AttachmentFile'>%s</a>" % \
                 (obj_url, items[x]['AttachmentFile'])
        return items


class ClientOrdersView(SupplyOrderFolderView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'SupplyOrder',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse',
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'level': 0
            }
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=SupplyOrder',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }


class ClientContactsView(BikaListingView):
    implements(IViewView, IContacts)

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'Contact',
            'sort_on':'sortable_title',
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level" : 0
            }
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Contact',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "contacts"

        self.icon = self.portal_url + "/++resource++bika.lims.images/client_contact_big.png"
        self.title = _("Contacts")
        self.description = ""

        self.columns = {
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'Username': {'title': _('User Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']
            items[x]['getFullname'] = obj.getFullname()
            items[x]['getEmailAddress'] = obj.getEmailAddress()
            items[x]['getBusinessPhone'] = obj.getBusinessPhone()
            items[x]['getMobilePhone'] = obj.getMobilePhone()
            username = obj.getUsername()
            items[x]['Username'] = username and username or ''

            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

            if items[x]['getEmailAddress']:
                items[x]['replace']['getEmailAddress'] = "<a href='mailto:%s'>%s</a>" % \
                     (items[x]['getEmailAddress'], items[x]['getEmailAddress'])

        return items


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(self.context.getPhysicalPath()),
                  'level': 0}
        )


class ReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):

    def __call__(self):
        base_query = json.loads(self.request['base_query'])
        portal_type = base_query.get('portal_type', [])
        if 'Contact' in portal_type:
            base_query['getParentUID'] = [self.context.UID(),]
        self.request['base_query'] = json.dumps(base_query)
        return DefaultReferenceWidgetVocabulary.__call__(self)


class ajaxGetClientInfo(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        wf = getToolByName(self.context, 'portal_workflow')
        ret = {'ClientTitle': self.context.Title(),
               'ClientID': self.context.getClientID(),
               'ClientSysID': self.context.id,
               'ClientUID': self.context.UID(),
               'ContactUIDs' : [c.UID() for c in self.context.objectValues('Contact') if
                                wf.getInfoFor(c, 'inactive_state', '') == 'active']
               }

        return json.dumps(ret)

