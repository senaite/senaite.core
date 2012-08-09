from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF, logger
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.publish import Publish
from bika.lims.browser.sample import SamplesView
from bika.lims.permissions import *
from bika.lims.utils import TimeOrDate
from bika.lims.utils import isActive
from bika.lims.subscribers import skip
from bika.lims.subscribers import doActionFor
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.i18n import translate
from zope.interface import implements
import plone

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

                # transition the object if both values are present
                if Sampler and DateSampled:
                    workflow.doActionFor(sample, action)
                    new_state = workflow.getInfoFor(sample, 'review_state')
                    transitioned[new_state].append(sample.Title())
                doActionFor(ar, action)

            message = None
            for state in transitioned:
                t = transitioned[state]
                if len(t) > 1:
                    if state == 'to_be_preserved':
                        message = _('${items} are waiting for preservation.',
                                    mapping = {'items': ', '.join(t)})
                    else:
                        message = _('${items} are waiting to be received.',
                                    mapping = {'items': ', '.join(t)})
                    message = self.context.translate(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
                elif len(t) == 1:
                    if state == 'to_be_preserved':
                        message = _('${item} is waiting for preservation.',
                                    mapping = {'item': ', '.join(t)})
                    else:
                        message = _('${item} is waiting to be received.',
                                    mapping = {'item': ', '.join(t)})
                    message = self.context.translate(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
            if not message:
                message = _('No changes made.')
                message = self.context.translate(message)
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
            message = self.context.translate(message)
            self.context.plone_utils.addPortalMessage(message, 'info')

            # And then the sample itself
            if Preserver and DatePreserved and not not_transitioned:
                doActionFor(sample, action)
                #message = _('${item} is waiting to be received.',
                #            mapping = {'item': sample.Title()})
                #message = self.context.translate(message)
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

                transitioned = Publish(self.context,
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
            message = self.context.translate(message)
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        else:
            AnalysisRequestWorkflowAction.__call__(self)

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
        # client contact required
        active_contacts = [c for c in self.context.objectValues('Contact') if
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if isActive(self.context):
            if self.context.portal_type == "Client" and not active_contacts:
                msg = _("Client contact required before request may be submitted")
                addPortalMessage(self.context.translate(msg))
            else:
                if mtool.checkPermission(AddAnalysisRequest, self.context):
                    self.context_actions[self.context.translate(_('Add'))] = {
                        'url':'ar_add',
                        'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisRequestsView, self).__call__()

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

class ClientARImportsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {'portal_type': 'ARImport'}
        self.context_actions = {_('AR Import'):
                                {'url': 'createObject?type_name=ARImport',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "arimports"

        self.icon = "++resource++bika.lims.images/arimport_big.png"
        self.title = _("Analysis Request Imports")
        self.description = ""

        self.columns = {
            'title': {'title': _('Import')},
            'getDateImported': {'title': _('Date Imported')},
            'getStatus': {'title': _('Validity')},
            'getDateApplied': {'title': _('Date Submitted')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied',
                         'state_title']},
            {'id':'imported',
             'title': _('Imported'),
             'contentFilter':{'review_state':'imported'},
             'columns': ['title',
                         'getDateImported',
                         'getStatus']},
            {'id':'submitted',
             'title': _('Applied'),
             'contentFilter':{'review_state':'submitted'},
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientAnalysisProfilesView(BikaListingView):
    """This is displayed in the Profiles client action,
       in the "Analysis Profiles" tab
    """

    def __init__(self, context, request):
        super(ClientAnalysisProfilesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'AnalysisProfile',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisprofiles"

        self.icon = "++resource++bika.lims.images/analysisprofile_big.png"
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
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "artemplates"
        self.icon = "++resource++bika.lims.images/artemplate_big.png"
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
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level" : 0 },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "SamplePoints"
        self.icon = "++resource++bika.lims.images/samplepoint_big.png"
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

        self.icon = "++resource++bika.lims.images/analysisspec_big.png"
        self.title = _("Analysis Specifications")

        self.columns = {
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['SampleType']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['SampleType']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['SampleType']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if isActive(self.context):
            if checkPermission(AddAnalysisSpec, self.context):
                self.context_actions[_('Add')] = \
                    {'url': 'createObject?type_name=AnalysisSpec',
                     'icon': '++resource++bika.lims.images/add.png'}
            if checkPermission(ManageClients, self.context):
                self.context_actions[_('Set to lab defaults')] = \
                    {'url': 'set_to_lab_defaults',
                     'icon': '++resource++bika.lims.images/analysisspec.png'}
        return super(ClientAnalysisSpecsView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']

            items[x]['SampleType'] = obj.getSampleType() and \
                 obj.getSampleType().Title()

            items[x]['replace']['SampleType'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['SampleType'])

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
            _id = self.context.invokeFactory(type_name = 'AnalysisSpec', id = 'tmp')
            clientspec = self.context[_id]
            clientspec.processForm()
            clientspec.edit(
                SampleType = labspec.getSampleType(),
                ResultsRange = labspec.getResultsRange(),
            )
        translate = self.context.translate
        message = self.context.translate(
            _("Analysis specifications reset to lab defaults."))
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

        self.icon = "++resource++bika.lims.images/attachment_big.png"
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

class ClientOrdersView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'SupplyOrder',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=SupplyOrder',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "orders"

        self.icon = "++resource++bika.lims.images/order_big.png"
        self.title = _("Orders")

        self.columns = {
            'OrderNumber': {'title': _('Order Number')},
            'OrderDate': {'title': _('Order Date')},
            'DateDispatched': {'title': _('Date Dispatched')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['OrderNumber',
                         'OrderDate',
                         'DateDispatched',
                         'state_title']},
            {'id':'pending',
             'contentFilter':{'review_state':'pending'},
             'title': _('Pending'),
             'columns': ['OrderNumber',
                         'OrderDate']},
            {'id':'dispatched',
             'contentFilter':{'review_state':'dispatched'},
             'title': _('Dispatched'),
             'columns': ['OrderNumber',
                         'OrderDate',
                         'DateDispatched']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = TimeOrDate(self.context, obj.getOrderDate())
            items[x]['DateDispatched'] = TimeOrDate(self.context, obj.getDateDispatched())

            items[x]['replace']['OrderNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['OrderNumber'])

        return items

class ClientContactsView(BikaListingView):
    implements(IViewView)

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

        self.icon = "++resource++bika.lims.images/client_contact_big.png"
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
