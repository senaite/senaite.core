""" Display lists of items in tables.
"""
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.AdvancedQuery import And, Or, MatchGlob, MatchRegexp
from Products.Archetypes import PloneMessageFactory as PMF
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.utils import isActive, TimeOrDate
from operator import itemgetter
from plone.app.content.batching import Batch
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.app.component.hooks import getSite
from zope.component._api import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
import App, json, plone, re, transaction, urllib

class WorkflowAction:
    """ Workflow actions taken in any Bika contextAnalysisRequest context
        This function is called to do the worflow actions
    """
    def __init__(self, context, request):
        self.destination_url = ""
        self.context = context
        self.request = request
        # Save context UID for benefit of event subscribers.
        self.request['context_uid'] = hasattr(self.context, 'UID') and \
            self.context.UID() or ''

    def _get_form_workflow_action(self):
        """ Retrieve the workflow action from the submitted form """
        # "workflow_action" is the edit border transition
        # "workflow_action_button" is the bika_listing table buttons
        form = self.request.form
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            came_from = "workflow_action_button"
            action = form.get(came_from, '')
            # XXX some browsers agree better than others about our JS ideas.
            # Two actions (eg ['submit','submit']) are present in the form.
            if type(action) in(list, tuple): action = action[0]
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return None, None
        # convert button text to action id
        if came_from == "workflow_action_button":
            action = form[action]
        if type(action) in(list, tuple): action = action[0]
        return (action, came_from)

    def _get_selected_items(self, full_objects = True):
        """ return a list of selected form objects
            full_objects defaults to True
        """
        form = self.request.form
        uc = getToolByName(self.context, 'uid_catalog')

        selected_items = {}
        for uid in form.get('uids', []):
            try:
                item = uc(UID = uid)[0].getObject()
            except:
                # ignore selected item if object no longer exists
                continue
            selected_items[uid] = item
        return selected_items

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        if self.destination_url == "":
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = self._get_form_workflow_action()

        # transition the context object.
        if came_from == "workflow_action":
            obj = self.context
            # the only actions allowed on inactive/cancelled
            # items are "reinstate" and "activate"
            if not isActive(obj) and action not in ('reinstate', 'activate'):
                message = self.context.translate(_('Item is inactive.'))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.destination_url)
                return
            else:
                if obj.UID() not in skiplist:
                    allowed_transitions = []
                    for t in workflow.getTransitionsFor(obj):
                        allowed_transitions.append(t['id'])
                    if action in allowed_transitions:
                        workflow.doActionFor(obj, action)
                self.request.response.redirect(self.destination_url)
                return

        # transition selected items from the bika_listing/Table.
        transitioned = []
        selected_items = self._get_selected_items()
        for uid, item in selected_items.items():
            # the only action allowed on inactive items is "activate"
            if not isActive(item) and action not in ('reinstate', 'activate'):
                continue
            if uid not in skiplist:
                allowed_transitions = []
                for t in workflow.getTransitionsFor(item):
                    allowed_transitions.append(t['id'])
                if action in allowed_transitions:
                    try:
                        workflow.doActionFor(item, action)
                        transitioned.append(item.Title())
                    except WorkflowException:
                        pass

        if len(transitioned) > 0:
            message = self.context.translate(PMF('Changes saved.'))
            self.context.plone_utils.addPortalMessage(message, 'info')

        # automatic label printing
        if action == 'receive' and 'receive' in self.context.bika_setup.getAutoPrintLabels():
            q = "/sticker?size=%s&items=" % (self.context.bika_setup.getAutoLabelSize())
            # selected_items is a list of UIDs (stickers for AR_add use IDs)
            q += ",".join([i.getId() for i in selected_items.values()])
            self.request.response.redirect(self.context.absolute_url() + q)
        else:
            self.request.response.redirect(self.destination_url)

class BikaListingView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/bika_listing.pt")

    title = ""
    description = ""
    contentFilter = {}
    allow_edit = True
    context_actions = {}
    setoddeven = True
    show_select_column = False
    show_select_row = False
    show_select_all_checkbox = True
    show_sort_column = False
    show_workflow_action_buttons = True
    categories = []
    # setting pagesize to 1000 specifically disables the batch sizez dropdown
    pagesize = 30
    pagenumber = 1
    # select checkbox is normally called uids:list
    # if table_only is set then the context form tag might require
    # these to have a different name=FieldName:list.
    select_checkbox_name = "uids"
    # when rendering multiple bika_listing tables, form_id must be unique
    form_id = "list"

    """
     ### column definitions
     The keys of the columns dictionary must all exist in all
     items returned by subclassing view's .folderitems.  Blank
     entries are inserted in the default folderitems for all entries
     without values.

     ### possible column dictionary keys are:
     - allow_edit
       if View.allow_edit is also True, this field is made editable
       Interim fields are always editable
     - type
       possible values: "string", "boolean", "choices".
       if "choices" is selected, item['choices'][column_id] must
       be a list of choice strings.
     - index
       the name of the catalog index for the column. adds 'indexed' class,
       to allow ajax table sorting for indexed columns
     - sortable: defaults True.  if False, adds nosort class
       (see bika_listing.js) to prevent inline table sorts.
    """
    columns = {
           'obj_type': {'title': _('Type')},
           'id': {'title': _('ID')},
           'title_or_id': {'title': _('Title')},
           'modified': {'title': _('Last modified')},
           'state_title': {'title': _('State')},
    }

    # Additional indexes to be searched
    # any index name not specified in self.columns[]
    # can be added here.
    filter_indexes = ['Title', 'Description', 'SearchableText']

    """
    ### review_state filter
    with just one review_state, the selector won't show.
    """
    review_states = [
        {'id':'all',
         'title': _('All'),
         'columns':['obj_type', 'title_or_id', 'modified', 'state_title']
         },
    ]

    def __init__(self, context, request):
        super(BikaListingView, self).__init__(context, request)
        path = hasattr(context, 'getPath') and context.getPath() \
            or "/".join(context.getPhysicalPath())
        if hasattr(self, 'contentFilter'):
            if not 'path' in self.contentFilter:
                self.contentFilter['path'] = {"query": path, "level" : 0 }
        else:
            if not 'path' in self.contentFilter:
                self.contentFilter = {'path': {"query": path, "level" : 0 }}

        self.base_url = context.absolute_url()
        self.view_url = self.base_url
        # contentsMethod may return a list of brains or a list of objects.
        # force it to "portal_catalog", subclass can/should override it
        #self.contentsMethod = self.context.getFolderContents
        self.contentsMethod = getToolByName(context, 'portal_catalog')

    def _process_request(self):
        # Use this function from a template that is using bika_listing_table
        # in such a way that the table_only request var will be used to
        # in-place-update the table.
        form_id = self.form_id
        form = self.request.form
        workflow = getToolByName(self.context, 'portal_workflow')

        # If table_only specifies another form_id, then we abort.
        # this way, a single table among many can request a redraw,
        # and only it's content will be rendered.
        if form_id not in self.request.get('table_only', form_id):
            return ''

        # review_state_selector
        review_state_name = self.request.get(form_id + '_review_state', None)
        if not review_state_name:
            review_state_name = 'all'
        self.request[form_id+'_review_state'] = review_state_name
        states = [r for r in self.review_states if r['id'] == review_state_name]
        review_state = states and states[0] or self.review_states[0]
        if review_state.has_key('contentFilter'):
            for k, v in review_state['contentFilter'].items():
                self.contentFilter[k] = v
        else:
            if review_state_name != 'all':
                self.contentFilter['review_state'] = review_state_name

        # sort on
        sort_on = self.request.get(form_id + '_sort_on', '')
        if sort_on \
           and sort_on in self.columns.keys() \
           and self.columns[sort_on].get('index', None):
            idx = self.columns[sort_on].get('index', sort_on)
            self.contentFilter['sort_on'] = idx
        else:
            if 'sort_on' not in self.contentFilter:
                self.contentFilter['sort_on'] = 'id'
                self.request.set(form_id+'_sort_on', 'id')

        # sort order
        sort_order = self.request.get(form_id + '_sort_order', '')
        if sort_order:
            self.contentFilter['sort_order'] = sort_order
        else:
            if 'sort_order' not in self.contentFilter:
                self.contentFilter['sort_order'] = 'ascending'
                self.request.set(form_id+'_sort_order', 'ascending')

        # pagesize
        self.pagesize = int(self.request.get(form_id + '_pagesize', self.pagesize))
        self.request.set('pagesize', self.pagesize)

        # pagenumber
        self.pagenumber = int(self.request.get(form_id + '_pagenumber', self.pagenumber))
        self.request.set('pagenumber', self.pagenumber)

        # index filters.
        self.And = []
        self.Or = []
        ##logger.info("contentFilter: %s"%self.contentFilter)
        for k, v in self.columns.items():
            if not v.has_key('index') \
               or v['index'] == 'review_state' \
               or v['index'] in self.filter_indexes:
                continue
            self.filter_indexes.append(v['index'])
        ##logger.info("Filter indexes: %s"%self.filter_indexes)
        # any request variable named ${form_id}_{index_name}
        # will pass it's value to that index in self.contentFilter.
        # all conditions using ${form_id}_{index_name} are searched with AND
        for index in self.filter_indexes:
            request_key = "%s_%s" % (form_id, index)
            if request_key in self.request:
                ##logger.info("And: %s=%s"%(index, self.request[request_key]))
                ##self.And.append(MatchGlob(index, self.request[request_key]))
                self.And.append(MatchRegexp(index, self.request[request_key]))
        # if there's a ${form_id}_filter in request, then all indexes
        # are are searched for it's value.
        # ${form_id}_filter is searched with OR agains all indexes
        request_key = "%s_filter" % form_id
        if request_key in self.request and self.request[request_key] != '':
            for index in self.filter_indexes:
                ##logger.info("Or: %s=%s"%(index, self.request[request_key]))
                ##self.Or.append(MatchGlob(index, self.request[request_key]))
                self.Or.append(MatchRegexp(index, self.request[request_key]))

    def __call__(self):
        """ Handle request parameters and render the form."""
        self._process_request()
        if self.request.get('table_only', '') == self.form_id:
            return self.contents_table(table_only=self.request.get('table_only'))
        else:
            return self.template()

    def selected_cats(self, items):
        """return a list of categories containing 'selected'=True items
        """
        cats = []
        for item in items:
            if 'selected' in item and \
               'category' in item and \
               item['selected'] and \
               item['category'] not in cats:
                cats.append(item['category'])
        return cats

    def folderitems(self, full_objects = False):
        """
        """
        context = aq_inner(self.context)
        plone_layout = getMultiAdapter((context, self.request), name = u'plone_layout')
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name = u'plone')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        workflow = getToolByName(context, 'portal_workflow')
        site_properties = portal_properties.site_properties
        norm = getUtility(IIDNormalizer).normalize
        show_all = self.request.get('show_all', '').lower() == 'true'
        pagenumber = int(self.request.get('pagenumber', 1) or 1)
        pagesize = self.pagesize
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        if (hasattr(self, 'And') and self.And) \
           or (hasattr(self, 'Or') and self.Or):
            # if contentsMethod is capable, we do an AdvancedQuery.
            if hasattr(self.contentsMethod, 'makeAdvancedQuery'):
                aq = self.contentsMethod.makeAdvancedQuery(self.contentFilter)
                if hasattr(self, 'And') and self.And:
                    tmpAnd = And()
                    for q in self.And:
                        tmpAnd.addSubquery(q)
                    aq &= tmpAnd
                if hasattr(self, 'Or') and self.Or:
                    tmpOr = Or()
                    for q in self.Or:
                        tmpOr.addSubquery(q)
                    aq &= tmpOr
                brains = self.contentsMethod.evalAdvancedQuery(aq)
            else:
                # otherwise, self.contentsMethod must handle contentFilter
                brains = self.contentsMethod(self.contentFilter)
        else:
            brains = self.contentsMethod(self.contentFilter)

        results = []
        for i, obj in enumerate(brains):
            # we don't know yet if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                 "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not show_all and not start <= i < end:
                if hasattr(obj, 'getObject'):
                    uid = obj.UID
                else:
                    uid = obj.UID()
                results.append(dict(path = path, uid = uid))
                continue

            if hasattr(obj, 'getObject'):
                obj = obj.getObject()

            uid = obj.UID()
            title = obj.Title()
            description = obj.Description()
            icon = plone_layout.getIcon(obj)
            url = obj.absolute_url()
            relative_url = obj.absolute_url(relative = True)

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type

            url_href_title = u'%s at %s: %s' % \
                (translate(type_title_msgid, context = self.request),
                 path,
                 safe_unicode(description))

            modified = TimeOrDate(self.context,
                                  obj.ModificationDate, long_format = 1)

            # element css classes
            type_class = 'contenttype-' + \
                plone_utils.normalizeString(obj.portal_type)

            state_class = ''
            states = {}
            for w in workflow.getWorkflowsFor(obj):
                state = w._getWorkflowStateOf(obj).id
                states[w.state_var] = state
                state_class += "state-%s " % state

            results_dict = dict(
                obj = obj,
                id = obj.getId,
                title = title,
                uid = uid,
                path = path,
                url = url,
                fti = fti,
                item_data = json.dumps([]),
                url_href_title = url_href_title,
                obj_type = obj.Type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                # a list of lookups for single-value-select fields
                choices = {},
                state_class = state_class,
                relative_url = relative_url,
                view_url = url,
                table_row_class = "",

                # a list of names of fields that may be edited on this item
                allow_edit = [],

                # a list of names of fields that are compulsory (if editable)
                required = [],

                # "before", "after" and replace: dictionary (key is column ID)
                # A snippet of HTML which will be rendered
                # before/after/instead of the table cell content.
                before = {}, # { before : "<a href=..>" }
                after = {},
                replace = {},
            )
            try:
                review_state = workflow.getInfoFor(obj, 'review_state')
                state_title = workflow.getTitleForStateOnType(review_state,
                                                              obj.portal_type)
            except:
                review_state = 'active'
                state_title = None
            if review_state:
                results_dict['review_state'] = review_state
            for state_var, state in states.items():
                if not state_title:
                    state_title = workflow.getTitleForStateOnType(
                        state, obj.portal_type)
                results_dict[state_var] = state
            results_dict['state_title'] = state_title

# XXX add some kind of out-of-date indicator to bika listing
##            if App.config.getConfiguration().debug_mode:
##                from Products.CMFEditions.utilities import dereference
##                pr = getToolByName(self.context, 'portal_repository')
##                o = hasattr(obj, 'getObject') and obj.getObject() or obj
##                if pr.isVersionable(o):
##                    pa = getToolByName(self.context, 'portal_archivist')
##                    history_id = str(dereference(o)[1])
##                    version_id = hasattr(o, 'version_id') \
##                               and str(o.version_id) or None
##                    if not 'version_id' in self.columns.keys():
##                        self.columns['version_id'] = {'title':'version'}
##                        for x in range(len(self.review_states)):
##                            if self.review_states[x]['id'] == 'all':
##                                self.review_states[x]['columns'].append('version_id')
##                    results_dict['version_id'] = '%s/%s' % (version_id, history_id)

            # extra classes for individual fields on this item { field_id : "css classes" }
            results_dict['class'] = {}

            # Search for values for all columns in obj
            for key in self.columns.keys():
                if hasattr(obj, key):
                    # if the key is already in the results dict
                    # then we don't replace it's value
                    if results_dict.has_key(key):
                        continue
                    value = getattr(obj, key)
                    if callable(value):
                        value = value()
                    results_dict[key] = value
                # bika_listing.js uses sortable-xx for sorting rows in-place,
                # so we only have to include it for columns with no index
                ## un-editable cells seem to work fine without sortabledata-X
                ## classes, just need sortabledata-X for sorting editable cells
                if key in results_dict['allow_edit']:
                    if not self.columns[key].has_key('index'):
                        results_dict['class'][key] = \
                            'sortabledata-%s'%norm(results_dict[key])
            results.append(results_dict)

        return results

    def contents_table(self, table_only = False):
        """ If you set table_only to true, then nothing outside of the
            <table/> tag will be printed (form tags, authenticator, etc).
            Then you can insert your own form tags around it.
        """
        table = BikaListingTable(bika_listing = self, table_only = table_only)
        return table.render(self)

class BikaListingTable(tableview.Table):

    render = ViewPageTemplateFile("templates/bika_listing_table.pt")

    def __init__(self, bika_listing = None, table_only = False):
        self.table = self
        self.table_only = table_only
        self.bika_listing = bika_listing
        self.pagesize = bika_listing.pagesize
        folderitems = bika_listing.folderitems()

        tableview.Table.__init__(self,
                                 bika_listing.request,
                                 bika_listing.base_url,
                                 bika_listing.view_url,
                                 folderitems,
                                 pagesize = bika_listing.pagesize)

        self.context = bika_listing.context
        self.request = bika_listing.request
        self.items = folderitems

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def get_workflow_actions(self):
        """ Compile a list of possible workflow transitions for items
            in this Table.
        """

        # return empty list if selecting checkboxes are disabled
        if not self.show_select_column:
            return []

        workflow = getToolByName(self.context, 'portal_workflow')

        state = self.request.get('review_state', 'all')
        review_state = [i for i in self.bika_listing.review_states if i['id'] == state][0]

        # get all transitions for all items.
        transitions = {}
        actions = []
        for obj in [i.get('obj', '') for i in self.items]:
            obj = hasattr(obj, 'getObject') and \
                obj.getObject() or \
                obj
            for t in workflow.getTransitionsFor(obj):
                transitions[t['id']] = t

        # if there is a review_state['some_state']['transitions'] attribute
        # on the BikaListingView, the list is restricted to and ordered by
        # these transitions
        if 'transitions' in review_state:
            for tid in review_state['transitions']:
                if tid in transitions:
                    actions.append(transitions[tid])
        else:
            actions = transitions.values()

        # if there is a review_state['some_state']['custom_actions'] attribute
        # on the BikaListingView, append these actions to the list.
        if 'custom_actions' in review_state:
            for action in review_state['custom_actions']:
                actions.append(action)

        return actions
