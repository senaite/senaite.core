""" Display lists of items in tables.
"""
from DateTime import DateTime
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.AdvancedQuery import And, Or, MatchRegexp, Between, Generic, Eq
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import isActive, TimeOrDate
from operator import itemgetter
from plone.app.content.batching import Batch
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.component._api import getMultiAdapter
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
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return None, None
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
        action, came_from = self._get_form_workflow_action()

        # transition the context object (plone edit bar dropdown)
        if came_from == "workflow_action":
            obj = self.context
            # the only actions allowed on inactive/cancelled
            # items are "reinstate" and "activate"
            if not isActive(obj) and action not in ('reinstate', 'activate'):
                message = self.context.translate(_('Item is inactive.'))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.destination_url)
                return
            if not skip(obj, action, peek=True):
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
            # the only actions allowed on inactive/cancelled
            # items are "reinstate" and "activate"
            if not isActive(item) and action not in ('reinstate', 'activate'):
                continue
            if not skip(item, action, peek=True):
                allowed_transitions = []
                for t in workflow.getTransitionsFor(item):
                    allowed_transitions.append(t['id'])
                if action in allowed_transitions:
                    doActionFor(item, action)
                    transitioned.append(item.Title())

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
    catalog = "portal_catalog"
    contentFilter = {}
    allow_edit = True
    context_actions = {}
    show_select_column = False
    show_select_row = False
    show_select_all_checkbox = True
    show_sort_column = False
    show_workflow_action_buttons = True
    show_column_toggles = True
    categories = []
    # setting pagesize to 1000 specifically disables the batch sizez dropdown
    pagesize = 25
    pagenumber = 1
    # select checkbox is normally called uids:list
    # if table_only is set then the context form tag might require
    # these to have a different name=FieldName:list.
    select_checkbox_name = "uids"
    # when rendering multiple bika_listing tables, form_id must be unique
    form_id = "list"
    review_state = 'default'


    """
     ### column definitions
     The keys of the columns dictionary must all exist in all
     items returned by subclassing view's .folderitems.  Blank
     entries are inserted in the default folderitems for all entries
     without values.

     ### possible column dictionary keys are:
     - allow_edit
       if self.allow_edit is also True, this field is made editable
       Interim fields are always editable
     - type
       "string" is the default, and actually, will require a NUMBER entry
                in the rendered text field.
       "choices" renders a dropdown.  Selected automatically if a vocabulary
                 exists.  the vocabulary data must be placed in
                 item['choices'][column_id].  it's a list of dictionaries:
                 [{'ResultValue':x}, {'ResultText',x}].
                 TODO 'choices' should probably expect a DisplayList...
       "boolean" a checkbox is rendered
       "date" A text field is rendered, with a jquery DatePicker attached.
     - index
       the name of the catalog index for the column. adds 'indexed' class,
       to allow ajax table sorting for indexed columns
     - sortable: defaults True.  if False, adds nosort class
     - toggle: enable/disable column toggle ability
     - input_class: CSS class applied to input widget in edit mode
     - input_width: size attribute applied to input widget in edit mode
    """
    columns = {
           'obj_type': {'title': _('Type')},
           'id': {'title': _('ID')},
           'title_or_id': {'title': _('Title')},
           'modified': {'title': _('Last modified')},
           'state_title': {'title': _('State')},
    }

    # Additional indexes to be searched
    # any index name not specified in self.columns[] can be added here.
    filter_indexes = ['Title', 'Description', 'SearchableText']

    """
    ### review_state filter
    with just one review_state, the selector won't show.

    if review_state[x]['transitions'] is defined, it is a list of dictionaries:
        [{'id':'x'}]
    Transitions will be ordered by and restricted to, these items.

    if review_state[x]['custom_actions'] is defined. it's a list of dict:
        [{'id':'x'}]
    These transitions will be forced into the list of workflow actions.
    They will need to be handled manually in the appropriate WorkflowAction
    subclass.
    """
    review_states = [
        {'id':'default',
         'contentFilter':{},
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

        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

        self.base_url = context.absolute_url()
        self.view_url = self.base_url

        self.translate = self.context.translate

    def _process_request(self):
        # Use this function from a template that is using bika_listing_table
        # in such a way that the table_only request var will be used to
        # in-place-update the table.
        form_id = self.form_id
        form = self.request.form
        workflow = getToolByName(self.context, 'portal_workflow')
        catalog = getToolByName(self.context, self.catalog)

        # If table_only specifies another form_id, then we abort.
        # this way, a single table among many can request a redraw,
        # and only it's content will be rendered.
        if form_id not in self.request.get('table_only', form_id):
            return ''

        ## review_state_selector
        cookie = json.loads(self.request.get("review_state", '{}'))
        cookie_key = "%s%s" % (self.context.portal_type, form_id)
        # first check POST
        selected_state = self.request.get("%s_review_state"%form_id, '')
        if not selected_state:
            # then check cookie
            selected_state = cookie.get(cookie_key, 'default')
        # get review_state id=selected_state
        states = [r for r in self.review_states if r['id'] == selected_state]
        review_state = states and states[0] or self.review_states[0]
        # set request and cookie to currently selected state id
        if not selected_state:
            selected_state = self.review_states[0]['id']

        self.review_state = cookie[cookie_key] = selected_state
        cookie = json.dumps(cookie)
        self.request['review_state'] = cookie
        self.request.response.setCookie('review_state', cookie, path="/")

        # contentFilter is expected in every review_state.
        for k, v in review_state['contentFilter'].items():
            self.contentFilter[k] = v

        # sort on
        sort_on = self.request.get(form_id + '_sort_on', '')
        # manual_sort_on: only sort the current batch of items
        # this is a compromise for sorting without column indexes
        self.manual_sort_on = None
        if sort_on \
           and sort_on in self.columns.keys() \
           and self.columns[sort_on].get('index', None):
            idx = self.columns[sort_on].get('index', sort_on)
            self.contentFilter['sort_on'] = idx
        else:
            if sort_on:
                self.manual_sort_on = sort_on
                if 'sort_on' in self.contentFilter:
                    del self.contentFilter['sort_on']

        # sort order
        self.sort_order = self.request.get(form_id + '_sort_order', '')
        if self.sort_order:
            self.contentFilter['sort_order'] = self.sort_order
        else:
            if 'sort_order' not in self.contentFilter:
                self.sort_order = 'ascending'
                self.contentFilter['sort_order'] = 'ascending'
                self.request.set(form_id+'_sort_order', 'ascending')
            else:
                self.sort_order = self.contentFilter['sort_order']
        if self.manual_sort_on:
            del self.contentFilter['sort_order']

        # pagesize
        pagesize = self.request.get(form_id + '_pagesize', self.pagesize)
        if type(pagesize) in (list, tuple):
            pagesize = pagesize[0]
        try:
            pagesize = int(pagesize)
        except:
            pagesize = self.pagesize
        self.pagesize = pagesize
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
            idx = catalog.Indexes.get(index, None)
            if not idx:
                logger.debug("index named '%s' not found in %s.  "
                             "(Perhaps the index is still empty)." %
                            (index, self.catalog))
                continue
            request_key = "%s_%s" % (form_id, index)
            value = self.request.get(request_key, '')
            if len(value) > 1:
                ##logger.info("And: %s=%s"%(index, value))
                if idx.meta_type in('ZCTextIndex', 'FieldIndex'):
                    self.And.append(MatchRegexp(index, value))
                elif idx.meta_type == 'DateIndex':
                    logger.error("Unhandled DateIndex search on '%s'"%index)
                    continue
                else:
                    self.Or.append(Generic(index, value))

        # if there's a ${form_id}_filter in request, then all indexes
        # are are searched for it's value.
        # ${form_id}_filter is searched with OR agains all indexes
        request_key = "%s_filter" % form_id
        value = self.request.get(request_key, '')
        if len(value) > 1:
            for index in self.filter_indexes:
                idx = catalog.Indexes.get(index, None)
                if not idx:
                    logger.debug("index named '%s' not found in %s.  "
                                 "(Perhaps the index is still empty)." %
                                 (index, self.catalog))
                    continue
                ##logger.info("Or: %s=%s"%(index, value))
                if idx.meta_type in('ZCTextIndex', 'FieldIndex'):
                    self.Or.append(MatchRegexp(index, value))
                elif idx.meta_type == 'DateIndex':
                    if value.find(":") > -1:
                        try:
                            lohi = [DateTime(x) for x in value.split(":")]
                        except:
                            logger.error("Error (And, DateIndex='%s', term='%s')"%(index,value))
                        self.Or.append(Between(index, lohi[0], lohi[1]))
                    else:
                        try:
                            self.Or.append(Eq(index, DateTime(value)))
                        except:
                            logger.error("Error (Or, DateIndex='%s', term='%s')"%(index,value))
                else:
                    self.Or.append(Generic(index, value))
            self.Or.append(MatchRegexp('review_state', value))

        # get toggle_cols cookie value
        # and modify self.columns[]['toggle'] to match.
        toggle_cols = self.get_toggle_cols()
        for col in self.columns.keys():
            if col in toggle_cols:
                self.columns[col]['toggle'] = True
            else:
                self.columns[col]['toggle'] = False

    def get_toggle_cols(self):
        states = [r for r in self.review_states if r['id'] == self.review_state]
        review_state = states and states[0] or self.review_states[0]
        try:
            toggles = {}
            # request OR cookie OR default
            toggles = json.loads(self.request.get(self.form_id+"_toggle_cols",
                                 self.request.get("toggle_cols", "{}")))
        except:
            pass
        finally:
            if not toggles:
                toggles = {}
        cookie_key = "%s%s" % (self.context.portal_type, self.form_id)
        toggle_cols = toggles.get(cookie_key,
                                  [col for col in self.columns.keys()
                                   if col in review_state['columns']
                                   and ('toggle' not in self.columns[col]
                                        or self.columns[col]['toggle'] == True)])
        return toggle_cols

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
        #self.contentsMethod = self.context.getFolderContents
        if not hasattr(self, 'contentsMethod'):
            self.contentsMethod = getToolByName(self.context, self.catalog)

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
        self.page_start_index = ""
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
            if self.page_start_index == "":
                self.page_start_index = i

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
                (self.context.translate(type_title_msgid,
                                        context = self.request),
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
                state_title = self.context.translate(
                    PMF(workflow.getTitleForStateOnType(review_state,
                                                    obj.portal_type)))
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
##                            self.review_states[x]['columns'].append('version_id')
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

        if hasattr(self.bika_listing, 'manual_sort_on') \
           and self.bika_listing.manual_sort_on:
            psi = self.bika_listing.page_start_index
            psi = psi and psi or 0
            # We do a sort of the current page using self.manual_sort_on, here
            page = folderitems[psi:psi+self.bika_listing.pagesize]
            page.sort(lambda x,y:cmp(x.get(self.bika_listing.manual_sort_on, ''),
                                     y.get(self.bika_listing.manual_sort_on, '')))

            if self.bika_listing.sort_order[0] in ['d','r']:
                page.reverse()

            folderitems = folderitems[:psi] \
                + page \
                + folderitems[psi+self.bika_listing.pagesize:]


        tableview.Table.__init__(self,
                                 bika_listing.request,
                                 bika_listing.base_url,
                                 bika_listing.view_url,
                                 folderitems,
                                 pagesize = bika_listing.pagesize)

        self.context = bika_listing.context
        self.request = bika_listing.request
        self.form_id = bika_listing.form_id
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


        cookie = json.loads(self.request.get("review_state", '{}'))
        cookie_key = "%s%s" % (self.context.portal_type,
                               self.form_id)
        # first check POST
        selected_state = self.request.get("%s_review_state"%self.form_id, '')
        if not selected_state:
            # then check cookie
            selected_state = cookie.get(cookie_key, '')
        # get review_state id=selected_state
        states = [r for r in self.bika_listing.review_states
                  if r['id'] == selected_state]
        review_state = states and states[0] \
            or self.bika_listing.review_states[0]

        # get all transitions for all items.
        transitions = {}
        actions = []
        for obj in [i.get('obj', '') for i in self.items]:
            obj = hasattr(obj, 'getObject') and obj.getObject() or obj
            for t in workflow.getTransitionsFor(obj):
                transitions[t['id']] = t

        # the list is restricted to and ordered by these transitions.
        if 'transitions' in review_state:
            for transition_dict in review_state['transitions']:
                if transition_dict['id'] in transitions:
                    actions.append(transitions[transition_dict['id']])
        else:
            actions = transitions.values()

        # and these are removed
        if 'hide_transitions' in review_state:
            actions = [a for a in actions
                       if a['id'] not in review_state['hide_transitions']]

        # if there is a review_state['some_state']['custom_actions'] attribute
        # on the BikaListingView, append these actions to the list.
        if 'custom_actions' in review_state:
            for action in review_state['custom_actions']:
                actions.append(action)

        for a,action in enumerate(actions):
            actions[a]['title'] = \
                self.bika_listing.translate(PMF(actions[a]['id'] + "_transition_title"))
        return actions
