from bika.lims.permissions import SampleSample
from zope.i18n import translate
from bika.lims.permissions import ManageClients
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import PMF, logger
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.publish import Publish
from bika.lims.browser.sample import SamplesView
from bika.lims.permissions import AddARProfile
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone

class ClientWorkflowAction(WorkflowAction):
    """ This function is called to do the worflow actions
        that apply to objects transitioned directly from Client views

        The main lab 'analysisrequests' and 'samples' views also have
        workflow_action urls bound to this handler.

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        translate = self.context.translation_service.translate
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

        if action == "sampled":
            objects = WorkflowAction._get_selected_items(self)
            transitioned = {'to_be_preserved':[], 'sample_due':[]}
            for obj_uid, obj in objects.items():
                if obj.portal_type == "AnalysisRequest":
                    sample = obj.getSample()
                else:
                    sample = obj
                # can't transition inactive items
                if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive':
                    continue
                if not checkPermission(SampleSample, sample):
                    continue

                # grab this object's Sampler and DateSampled from the form
                Sampler = form['getSampler'][0][obj_uid].strip()
                DateSampled = form['getDateSampled'][0][obj_uid].strip()

                # write them to the sample
                sample.edit(Sampler = Sampler and Sampler or '',
                            DateSampled = DateSampled and DateTime(DateSampled) or '')

                # transition the object if both values are present
                if Sampler and DateSampled:
                    workflow.doActionFor(sample, 'sampled')
                    new_state = workflow.getInfoFor(sample, 'review_state')
                    transitioned[new_state].append(sample.Title())

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

        elif action in ('prepublish', 'publish', 'republish'):
            # We pass a list of AR objects to Publish.
            # it returns a list of AR IDs which were actually published.
            ARs_to_publish = []
            transitioned = []
            if 'paths' in form:
                for path in form['paths']:
                    item_id = path.split("/")[-1]
                    item_path = path.replace("/" + item_id, '')
                    ar = pc(id = item_id,
                              path = {'query':item_path,
                                      'depth':1})[0].getObject()
                    # can't publish inactive items
                    if not(
                        'bika_inactive_workflow' in workflow.getChainFor(ar) and \
                        workflow.getInfoFor(ar, 'inactive_state', '') == 'inactive'):
                        ar.setDatePublished(DateTime())
                        ARs_to_publish.append(ar)

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
            message = translate(message)
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class ClientAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)

        self.contentFilter['path'] = {"query": "/".join(context.getPhysicalPath()),
                                      "level" : 0 }

        translate = self.context.translation_service.translate

        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        # client contact required
        active_contacts = [c for c in context.objectValues('Contact') if \
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if context.portal_type == "Client" and not active_contacts:
            msg = _("Client contact required before request may be submitted")
            self.context.plone_utils.addPortalMessage(translate(msg))
        else:
            # add actions enabled only for active clients
            self.context_actions = {}
            if wf.getInfoFor(self.context, 'inactive_state', '') == 'active':
                self.context_actions[translate(_('Add'))] = {
                    'url':'analysisrequest_add',
                    'icon': '++resource++bika.lims.images/add.png'}

        review_states = []
        for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
        self.review_states = review_states

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
        self.contentFilter = {'portal_type': 'ARImport'}
        self.context_actions = {_('AR Import'):
                                {'url': 'createObject?type_name=ARImport',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

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
            {'id':'all',
             'title': _('All'),
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied',
                         'state_title']},
            {'id':'imported',
             'title': _('Imported'),
             'columns': ['title',
                         'getDateImported',
                         'getStatus']},
            {'id':'submitted',
             'title': _('Applied'),
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

class ClientARProfilesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientARProfilesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARProfile',
                              'getClientUID': context.UID(),
                              'path': {"query": "/".join(context.getPhysicalPath()),
                                       "level" : 0 }
                              }
        bsc = getToolByName(context, 'bika_setup_catalog')
        wf = getToolByName(context, 'portal_workflow')
        self.contentsMethod = bsc
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.icon = "++resource++bika.lims.images/arprofile_big.png"
        self.title = _("Analysis Request Profiles")
        self.description = ""

        self.context_actions = {}
        checkPermission = self.context.portal_membership.checkPermission
        if checkPermission(AddARProfile, self.context):
            if wf.getInfoFor(self.context, 'inactive_state', '') == 'active':
                self.context_actions[translate(_('Add'))] = \
                    {'url': 'createObject?type_name=ARProfile',
                     'icon': '++resource++bika.lims.images/add.png'}

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'getProfileKey': {'title': _('Profile Key'),
                              'index':'getProfileKey'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['title', 'getProfileKey']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ClientAnalysisSpecsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        bsc = getToolByName(context, 'bika_setup_catalog')
        wf = getToolByName(context, 'portal_workflow')
        self.contentFilter = {'portal_type': 'AnalysisSpec',
                              'getClientUID': context.UID(),
                              'path': {"query": "/".join(context.getPhysicalPath()),
                                       "level" : 0 }
                              }
        self.contentsMethod = bsc

        checkPermission = self.context.portal_membership.checkPermission
        self.context_actions = {}
        if wf.getInfoFor(self.context, 'inactive_state', '') == 'active':
            if checkPermission(AddARProfile, self.context):
                self.context_actions[translate(_('Add'))] = \
                    {'url': 'createObject?type_name=AnalysisSpec',
                     'icon': '++resource++bika.lims.images/add.png'}
            if checkPermission(ManageClients, self.context):
                self.context_actions[translate(_('Set to lab defaults'))] = \
                    {'url': 'set_to_lab_defaults',
                     'icon': '++resource++bika.lims.images/analysisspec.png'}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.icon = "++resource++bika.lims.images/analysisspec_big.png"
        self.title = _("Analysis Specifications")

        self.columns = {
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['SampleType'],
             },
        ]

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
        translate = self.context.translation_service.translate
        message = translate(_("Analysis specifications reset to lab defaults."))
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.request.RESPONSE.redirect(self.context.absolute_url() + "/analysisspecs")
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
            {'id':'all',
             'title': 'All',
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

        self.icon = "++resource++bika.lims.images/order_big.png"
        self.title = _("Orders")

        self.columns = {
            'OrderNumber': {'title': _('Order Number')},
            'OrderDate': {'title': _('Order Date')},
            'DateDispatched': {'title': _('Date Dispatched')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['OrderNumber',
                         'OrderDate',
                         'DateDispatched',
                         'state_title']},
            {'id':'pending',
             'title': _('Pending'),
             'columns': ['OrderNumber',
                         'OrderDate']},
            {'id':'dispatched',
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
        self.contentFilter = {'portal_type': 'Contact',
                              'sort_on':'sortable_title',
                              'path': {"query": "/".join(context.getPhysicalPath()),
                                       "level" : 0 }
                              }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Contact',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.icon = "++resource++bika.lims.images/client_contact_big.png"
        self.title = _("Contacts")
        self.description = ""

        self.columns = {
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
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

            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

            if items[x]['getEmailAddress']:
                items[x]['replace']['getEmailAddress'] = "<a href='mailto:%s'>%s</a>" % \
                     (items[x]['getEmailAddress'], items[x]['getEmailAddress'])

        return items
