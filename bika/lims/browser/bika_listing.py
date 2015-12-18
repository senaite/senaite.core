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
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, format_supsub
from bika.lims import logger
from bika.lims.interfaces import IFieldIcons
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import isActive, getHiddenAttributesForClass
from bika.lims.utils import to_utf8
from operator import itemgetter
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getAdapters
from zope.component import getUtility
from zope.component._api import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.interface import Interface

import App
import json
import pkg_resources
import plone
import re
import transaction
import urllib

try:
    from plone.batching import Batch
except:
    # Plone < 4.3
    from plone.app.content.batching import Batch


class WorkflowAction:
    """ Workflow actions taken in any Bika contextAnalysisRequest context

        This function provides the default behaviour for workflow actions invoked
        from bika_listing tables.

        Some actions (eg, AR copy_to_new) can be invoked from multiple contexts.
        In that case, I will begin to register their handlers here.
        XXX WorkflowAction handlers should be simple adapters.
    """
    def __init__(self, context, request):
        self.destination_url = ""
        self.context = context

        self.request = request
        # Save context UID for benefit of event subscribers.
        self.request['context_uid'] = hasattr(self.context, 'UID') and \
            self.context.UID() or ''
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()

        self.portal_url = self.portal.absolute_url()

    def _get_form_workflow_action(self):
        """ Retrieve the workflow action from the submitted form """
        # "workflow_action" is the edit border transition
        # "workflow_action_button" is the bika_listing table buttons
        form = self.request.form
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if type(action) in (list, tuple):
            action = action[0]
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

    def workflow_action_default(self, action, came_from):
        if came_from in ['workflow_action', 'edit']:
            # If a single item was acted on we will create the item list
            # manually from this item itself.  Otherwise, bika_listing will
            # pass a list of selected items in the requyest.
            items = [self.context, ]
        else:
            # normal bika_listing.
            items = self._get_selected_items().values()

        if items:
            trans, dest = self.submitTransition(action, came_from, items)
            if trans:
                message = PMF('Changes saved.')
                self.context.plone_utils.addPortalMessage(message, 'info')
            if dest:
                self.request.response.redirect(dest)
                return
        else:
            message = _('No items selected')
            self.context.plone_utils.addPortalMessage(message, 'warn')
        self.request.response.redirect(self.destination_url)
        return

    def workflow_action_copy_to_new(self):
        """Invoke the ar_add form in the current context, passing the UIDs of
        the source ARs as request parameters.
        """
        objects = WorkflowAction._get_selected_items(self)
        if not objects:
            message = self.context.translate(
                _("No analyses have been selected"))
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url() + \
                                   "/batchbook"
            self.request.response.redirect(self.destination_url)
            return

        url = self.context.absolute_url() + "/portal_factory/" + \
              "AnalysisRequest/Request new analyses/ar_add" + \
              "?ar_count={0}".format(len(objects)) + \
              "&copy_from={0}".format(",".join(objects.keys()))
        self.request.response.redirect(url)
        return

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        if self.destination_url == "":
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        action, came_from = self._get_form_workflow_action()

        if action:
            # Call out to the workflow action method
            # Use default bika_listing.py/WorkflowAction for other transitions
            method_name = 'workflow_action_' + action
            method = getattr(self, method_name, False)
            if method and not callable(method):
                raise Exception("Shouldn't Happen: %s.%s not callable." %
                                (self, method_name))
            if method:
                method()
            else:
                self.workflow_action_default(action, came_from)
        else:
            # Do nothing
            self.request.response.redirect(self.destination_url)
            return

    def submitTransition(self, action, came_from, items):
        """ Performs the action's transition for the specified items
            Returns (numtransitions, destination), where:
            - numtransitions: the number of objects successfully transitioned.
                If no objects have been successfully transitioned, gets 0 value
            - destination: the destination url to be loaded immediately
        """
        dest = None
        transitioned = []
        workflow = getToolByName(self.context, 'portal_workflow')

        # transition selected items from the bika_listing/Table.
        for item in items:
            # the only actions allowed on inactive/cancelled
            # items are "reinstate" and "activate"
            if not isActive(item) and action not in ('reinstate', 'activate'):
                continue
            if not skip(item, action, peek=True):
                allowed_transitions = [it['id'] for it in \
                                       workflow.getTransitionsFor(item)]
                if action in allowed_transitions:
                    success, message = doActionFor(item, action)
                    if success:
                        transitioned.append(item.id)
                    else:
                        self.context.plone_utils.addPortalMessage(message, 'error')
        # automatic label printing
        if transitioned and action == 'receive' \
            and 'receive' in self.portal.bika_setup.getAutoPrintStickers():
            q = "/sticker?autoprint=1&template=%s&items=" % (self.portal.bika_setup.getAutoStickerTemplate())
            # selected_items is a list of UIDs (stickers for AR_add use IDs)
            q += ",".join(transitioned)
            dest = self.context.absolute_url() + q

        return len(transitioned), dest


class BikaListingView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/bika_listing.pt")
    render_items = ViewPageTemplateFile("templates/bika_listing_table_items.pt")

    # If the view is rendered with control of it's own main_template etc,
    # then it will use this for the title/description.  This gives each
    # view a way to set this easily.
    title = ""
    description = ""

    # The name of the catalog which will, by default, be searched for results
    # matching self.contentFilter
    catalog = "portal_catalog"

    # This is the list of query parameters passed to the catalog.
    # It's just a default set.  This can be modified by Python, or by the
    # contentFilter key in self.review_states.
    contentFilter = {}

    # This is an override and a switch, but it does not guarantee allow_edit.
    # This can be used to turn it off, regardless of settings in place by
    # individual items/fields, but if it is turned on, ultimate control
    # is still given to the individual items/fields.
    allow_edit = True

    # We use the context_actions to show a list of buttons above the list
    # The "Add" button is usually inserted here.
    context_actions = {}

    # Display the left-most column for selecting all/individual items
    # If this is disabled, then you can't transition items from this view,
    # instead you will have to visit each item, and transition it inline.
    show_select_column = False

    # This comes from default Plone; I'm not sure it works still.
    show_select_row = False

    # Toggle display of the checkbox which selects all rows
    show_select_all_checkbox = True

    # This is the column used to hold the handles used to manually re-order
    # items in the list
    show_sort_column = False

    # Workflow action buttons (and anything hacked into that list of actions)
    # will not be displayed if this is False
    show_workflow_action_buttons = True

    # Column toggles are displayed when right-clicking on the column headers.
    # Set this to false to disallow setting column toggles for some reason.
    show_column_toggles = True

    # setting pagesize to 0 specifically disables the batch size dropdown.
    pagesize = 25

    # On first load, pagenumber=1 probably makes the most sense.
    pagenumber = 1

    # select checkbox is normally called uids:list
    # if table_only is set then the context form tag might require
    # these to have a different name=FieldName:list.
    # This is a cheat and we can ignore it.
    select_checkbox_name = "uids"

    # when rendering multiple bika_listing tables, form_id must be unique
    form_id = "list"
    review_state = 'default'

    # Show categorized list; categories are collapsed until required
    show_categories = False

    # These are the possible categories.  If self.show_categories is True,
    # These are the categories which will be rendered.  Any items without
    # a 'category' key/value will be shown in a special "None" category.
    categories = []

    # By default every category will be expanded.  Careful with this, if there
    # is a possibility that the list could get very large.
    expand_all_categories = False

    # With this setting, we allow categories to be simple empty place-holders.
    # When activated, the category data will be fetched from the server,
    # and complted inline.  This is useful for list which will have many
    # thousands of entries in many categories, where loading the entire list
    # in HTML would be very slow.
    ajax_categories = False

    # using the following attribute, some python class may add a CSS class
    # to the TH elements used for the category headings.  This allows all
    # manner of Javascript trickery.
    cat_header_class = ''

    # category_index is the catalog index from each listed object.
    # it will be used to decide if an item is a member of a category.
    # This is required, if using ajax_categories.
    category_index = None

    # A list of fields, and the icons that should be shown in them.
    field_icons = {}

    show_table_footer = True

    # Column definitions:
    #
    # The keys of the columns dictionary must all exist in all
    # items returned by subclassing view's .folderitems method.
    #
    # Blank entries are inserted in the default folderitems for
    # all entries without values.
    #
    # Possible column dictionary keys are:
    # - allow_edit
    #   This field is made editable.
    #   Interim fields are always editable
    # - type
    #   "string" is the default.
    #   "boolean" a checkbox is rendered
    #   "date" A text field is rendered, with a jquery DatePicker attached.
    #   "choices" renders a dropdown.  The vocabulary data must be placed in
    #             item['choices'][column_id].  it's a list of dictionaries:
    #             [{'ResultValue':x}, {'ResultText',x}].
    # - index
    #   The name of the catalog index for the column.  Allows full-table
    #            sorting.
    # - sortable: if False, adds nosort class to this column.
    # - toggle: enable/disable column toggle ability.
    # - input_class: CSS class applied to input widget in edit mode
    # - input_width: size attribute applied to input widget in edit mode
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

    # The current or default review_state when one hasn't been selected.
    # With this setting, BikaListing instances must be careful to change it,
    # without having valid review_state existing in self.review_states
    default_review_state = 'default'

    # review_state
    #
    # A list of dictionaries, specifying parameters for listing filter buttons.
    # - If review_state[x]['transitions'] is defined it's a list of dictionaries:
    #     [{'id':'x'}]
    # Transitions will be ordered by and restricted to, these items.
    #
    # - If review_state[x]['custom_actions'] is defined. it's a list of dict:
    #     [{'id':'x'}]
    # These transitions will be forced into the list of workflow actions.
    # They will need to be handled manually in the appropriate WorkflowAction
    # subclass.
    review_states = [
        {'id':'default',
         'contentFilter':{},
         'title': _('All'),
         'columns':['obj_type', 'title_or_id', 'modified', 'state_title']
         },
    ]

    def __init__(self, context, request, **kwargs):
        self.field_icons = {}
        super(BikaListingView, self).__init__(context, request)
        path = hasattr(context, 'getPath') and context.getPath() \
            or "/".join(context.getPhysicalPath())
        if hasattr(self, 'contentFilter'):
            if not 'path' in self.contentFilter:
                self.contentFilter['path'] = {"query": path, "level" : 0 }
        else:
            if not 'path' in self.contentFilter:
                self.contentFilter = {'path': {"query": path, "level" : 0 }}

        if 'show_categories' in kwargs:
            self.show_categories = kwargs['show_categories']

        if 'expand_all_categories' in kwargs:
            self.expand_all_categories = kwargs['expand_all_categories']

        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

        self.base_url = context.absolute_url()
        self.view_url = self.base_url

        self.translate = self.context.translate
        self.show_all = False

    @property
    def review_state(self):
        """Get workflow state of object in wf_id.
        First try request: <form_id>_review_state
        Then try 'default': self.default_review_state
        :return: item from self.review_states
        """
        if not self.review_states:
            logger.error("%s.review_states is undefined." % self)
            return None
        # get state_id from (request or default_review_states)
        key = "%s_review_state" % self.form_id
        state_id = self.request.form.get(key, self.default_review_state)
        states = [r for r in self.review_states if r['id'] == state_id]
        if not states:
            logger.error("%s.review_states does not contains id='%s'." %
                         (self, state_id))
            return None
        review_state = states[0] if states else self.review_states[0]
        # set selected state into the request
        self.request['%s_review_state' % self.form_id] = review_state['id']
        return review_state

    def _process_request(self):
        """Scan request for parameters and configure class attributes
        accordingly.  Setup AdvancedQuery or catalog contentFilter.

        Request parameters:
        <form_id>_sort_on:          list items are sorted on this key
        <form_id>_manual_sort_on:   no index - sort with python
        <form_id>_pagesize:         number of items
        <form_id>_pagenumber:       page number
        <form_id>_filter:           A string, will be regex matched against
                                    indexes in <form_id>_filter_indexes
        <form_id>_filter_indexes:   list of index names which will be searched
                                    for the value of <form_id>_filter

        <form_id>_<index_name>:     Any index name can be used after <form_id>_.

            any request variable named ${form_id}_{index_name} will pass it's
            value to that index in self.contentFilter.

            All conditions using ${form_id}_{index_name} are searched with AND.

            The parameter value will be matched with regexp if a FieldIndex or
            TextIndex.  Else, AdvancedQuery.Generic is used.
        """
        form_id = self.form_id
        form = self.request.form
        workflow = getToolByName(self.context, 'portal_workflow')
        catalog = getToolByName(self.context, self.catalog)

        # Some ajax calls duplicate form values?  I have not figured out why!
        if self.request.form:
            for key, value in self.request.form.items():
                if isinstance(value, list):
                    self.request.form[key] = self.request.form[key][0]

        # If table_only specifies another form_id, then we abort.
        # this way, a single table among many can request a redraw,
        # and only it's content will be rendered.
        if form_id not in self.request.get('table_only', form_id):
            return ''


        # contentFilter is expected in every self.review_state.
        for k, v in self.review_state['contentFilter'].items():
            self.contentFilter[k] = v
        # sort on
        self.sort_on = self.request.get(form_id + '_sort_on', None)
        # manual_sort_on: only sort the current batch of items
        # this is a compromise for sorting without column indexes
        self.manual_sort_on = None
        if self.sort_on \
           and self.sort_on in self.columns.keys() \
           and self.columns[self.sort_on].get('index', None):
            idx = self.columns[self.sort_on].get('index', self.sort_on)
            self.contentFilter['sort_on'] = idx
        else:
            if self.sort_on:
                self.manual_sort_on = self.sort_on
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
            pagesize = self.pagesize = 10
        self.pagesize = pagesize
        # Plone's batching wants this variable:
        self.request.set('pagesize', self.pagesize)
        # and we want to make our choice remembered in bika_listing also
        self.request.set(self.form_id + '_pagesize', self.pagesize)

        # pagenumber
        self.pagenumber = int(self.request.get(form_id + '_pagenumber', self.pagenumber))
        # Plone's batching wants this variable:
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
                    logger.info("Unhandled DateIndex search on '%s'"%index)
                    continue
                else:
                    self.Or.append(Generic(index, value))

        # if there's a ${form_id}_filter in request, then all indexes
        # are are searched for it's value.
        # ${form_id}_filter is searched with OR agains all indexes
        request_key = "%s_filter" % form_id
        value = self.request.get(request_key, '')
        if type(value) in (list, tuple):
            value = value[0]
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
                    self.expand_all_categories = True
                    # https://github.com/bikalabs/Bika-LIMS/issues/1069
                    vals = value.split('-')
                    if len(vals) > 2:
                        valroot = vals[0]
                        for i in range(1, len(vals)):
                            valroot = '%s-%s' % (valroot, vals[i])
                            self.Or.append(MatchRegexp(index, valroot+'-*'))
                            self.expand_all_categories = True
                elif idx.meta_type == 'DateIndex':
                    if type(value) in (list, tuple):
                        value = value[0]
                    if value.find(":") > -1:
                        try:
                            lohi = [DateTime(x) for x in value.split(":")]
                        except:
                            logger.info("Error (And, DateIndex='%s', term='%s')"%(index,value))
                        self.Or.append(Between(index, lohi[0], lohi[1]))
                        self.expand_all_categories = True
                    else:
                        try:
                            self.Or.append(Eq(index, DateTime(value)))
                            self.expand_all_categories = True
                        except:
                            logger.info("Error (Or, DateIndex='%s', term='%s')"%(index,value))
                else:
                    self.Or.append(Generic(index, value))
                    self.expand_all_categories = True
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
                                   if col in self.review_state['columns']
                                   and ('toggle' not in self.columns[col]
                                        or self.columns[col]['toggle'] == True)])
        return toggle_cols

    def GET_url(self, include_current=True, **kwargs):
        url = self.request['URL'].split("?")[0]
        # take values from form (both html form and GET request slurped here)
        query = {}
        if include_current:
            for k, v in self.request.form.items():
                if k.startswith(self.form_id + "_") and not "uids" in k:
                    query[k] = v
        # override from self attributes
        for x in "pagenumber", "pagesize", "review_state", "sort_order", "sort_on":
            if str(getattr(self, x, None)) != 'None':
                # I don't understand why on AR listing, getattr(self,x)
                # is a dict, but this line will resolve LIMS-1420
                if x == "review_state" and type(getattr(self, x))==dict:
                    query['%s_%s'%(self.form_id, x)] = getattr(self, x)['id']
                else:
                    query['%s_%s'%(self.form_id, x)] = getattr(self, x)
        # then override with passed kwargs
        for x in kwargs.keys():
            query['%s_%s'%(self.form_id, x)] = kwargs.get(x)
        if query:
            url = url + "?" + "&".join(["%s=%s"%(x,y) for x,y in query.items()])
        return url

    def __call__(self):
        """ Handle request parameters and render the form."""

        # ajax_categories, basic sanity.
        # we do this here to allow subclasses time to define these things.
        if self.ajax_categories and not self.category_index:
            msg = "category_index must be defined when using ajax_categories."
            raise AssertionError(msg)

        self._process_request()

        # ajax_category_expand is included in the form if this form submission
        # is an asynchronous one triggered by a category being expanded.
        if self.request.get('ajax_category_expand', False):
            # - get nice formatted category contents (tr rows only)
            return self.rendered_items()

        if self.request.get('table_only', '') == self.form_id:
            return self.contents_table(table_only=self.request.get('table_only'))
        else:
            return self.template()

    def selected_cats(self, items):
        """Return a list of categories that will be expanded by default when
        the page is reloaded.

        In this default method, categories which contain selected
        items are always expanded.

        :param items: A list of items returned from self.folderitems().
        :return: a list of strings, self.categories contains the complete list.
        """
        cats = []
        for item in items:
            cat = item.get('category', 'None')
            if item.get('selected', False) \
                or self.expand_all_categories \
                or not self.show_categories:
                if cat not in cats:
                    cats.append(cat)
        return cats

    def restricted_cats(self, items):
        """Return a list of categories that will not be displayed.

        The items will still be present, and account for a part of the page
        batch total.

        :param items: A list of items returned from self.folderitems().
        :return: a list of AnalysisCategory instances.
        """
        return []

    def isItemAllowed(self, obj):
        """ return if the item can be added to the items list.
        """
        return True

    def folderitems(self, full_objects = False):
        """
        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        Test page batching https://github.com/bikalabs/Bika-LIMS/issues/1276
        When visiting the second page, the Water sampletype should be displayed:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/bika_setup/bika_sampletypes/folder_view?",
        ... "list_pagesize=10&list_review_state=default&list_pagenumber=2")
        >>> browser.contents
        '...Water...'
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
        if self.request.get('show_all', '').lower() == 'true' \
                or self.show_all == True \
                or self.pagesize == 0:
            show_all = True
        else:
            show_all = False

        pagenumber = int(self.request.get('pagenumber', 1) or 1)
        pagesize = self.pagesize
        start = (pagenumber - 1) * pagesize
        end = start + pagesize - 1

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
        self.page_start_index = 0
        current_index = -1
        for i, obj in enumerate(brains):
            # we don't know yet if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                 "/".join(obj.getPhysicalPath())

            if hasattr(obj, 'getObject'):
                obj = obj.getObject()

            # check if the item must be rendered or not (prevents from
            # doing it later in folderitems) and dealing with paging
            if not self.isItemAllowed(obj):
                continue

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            # we only take allowed items into account
            current_index += 1
            if not show_all and not (start <= current_index <= end):
                results.append(dict(path = path, uid = obj.UID()))
                continue

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

            url_href_title = '%s at %s: %s' % (
                t(type_title_msgid),
                path,
                to_utf8(description))

            modified = self.ulocalized_time(obj.modified()),

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
                id = obj.getId(),
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
                category = 'None',

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
                rs = workflow.getInfoFor(obj, 'review_state')
                st_title = workflow.getTitleForStateOnType(rs, obj.portal_type)
                st_title = t(PMF(st_title))
            except:
                rs = 'active'
                st_title = None
            if rs:
                results_dict['review_state'] = rs
            for state_var, state in states.items():
                if not st_title:
                    st_title = workflow.getTitleForStateOnType(
                        state, obj.portal_type)
                results_dict[state_var] = state
            results_dict['state_title'] = st_title

            # extra classes for individual fields on this item { field_id : "css classes" }
            results_dict['class'] = {}
            for name, adapter in getAdapters((obj, ), IFieldIcons):
                auid = obj.UID() if hasattr(obj, 'UID') and callable(obj.UID) else None
                if not auid:
                    continue
                alerts = adapter()
                # logger.info(str(alerts))
                if alerts and auid in alerts:
                    if auid in self.field_icons:
                        self.field_icons[auid].extend(alerts[auid])
                    else:
                        self.field_icons[auid] = alerts[auid]

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

    def rendered_items(self):
        """ If you set table_only to true, then nothing outside of the
            <table/> tag will be printed (form tags, authenticator, etc).
            Then you can insert your own form tags around it.
        """
        # Category which we are going to query:
        self.cat = self.request.get('ajax_category_expand')
        self.contentFilter[self.category_index] = self.request.get('cat')

        # selected review_state must be adhered to
        st_id = self.request.get('review_state')

        # These are required to allow the template to work with this class as
        # the view.  Normally these are attributes of class BikaListingTable.
        self.bika_listing = self
        self.this_cat_selected = True
        self.this_cat_batch = self.folderitems()

        data = self.render_items()
        return data

    def get_workflow_actions(self):
        """ Compile a list of possible workflow transitions for items
            in this Table.
        """

        # cbb return empty list if we are unable to select items
        if not self.show_select_column:
            return []

        workflow = getToolByName(self.context, 'portal_workflow')

        # get all transitions for all items.
        transitions = {}
        actions = []
        for obj in [i.get('obj', '') for i in self.items]:
            obj = hasattr(obj, 'getObject') and obj.getObject() or obj
            for it in workflow.getTransitionsFor(obj):
                transitions[it['id']] = it

        # the list is restricted to and ordered by these transitions.
        if 'transitions' in self.review_state:
            for transition_dict in self.review_state['transitions']:
                if transition_dict['id'] in transitions:
                    actions.append(transitions[transition_dict['id']])
        else:
            actions = transitions.values()

        new_actions = []
        # remove any invalid items with a warning
        for a,action in enumerate(actions):
            if isinstance(action, dict) \
                    and 'id' in action:
                new_actions.append(action)
            else:
                logger.warning("bad action in custom_actions: %s. (complete list: %s)."%(action,actions))

        # and these are removed
        if 'hide_transitions' in self.review_state:
            actions = [a for a in actions
                       if a['id'] not in self.review_state['hide_transitions']]

        # cheat: until workflow_action is abolished, all URLs defined in
        # GS workflow setup will be ignored, and the default will apply.
        # (that means, WorkflowAction-bound URL is called).
        for i, action in enumerate(actions):
            actions[i]['url'] = ''

        # if there is a self.review_state['some_state']['custom_actions'] attribute
        # on the BikaListingView, add these actions to the list.
        if 'custom_actions' in self.review_state:
            for action in self.review_state['custom_actions']:
                if isinstance(action, dict) \
                        and 'id' in action:
                    actions.append(action)

        for a,action in enumerate(actions):
            actions[a]['title'] = t(PMF(actions[a]['id'] + "_transition_title"))
        return actions

    def getPriorityIcon(self):
        if hasattr(self.context, 'getPriority'):
            priority = self.context.getPriority()
            if priority:
                icon = priority.getBigIcon()
                if icon:
                    return '/'.join(icon.getPhysicalPath())

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i


class BikaListingTable(tableview.Table):

    render = ViewPageTemplateFile("templates/bika_listing_table.pt")
    render_items = ViewPageTemplateFile("templates/bika_listing_table_items.pt")

    def __init__(self, bika_listing = None, table_only = False):
        self.table = self
        self.table_only = table_only
        self.bika_listing = bika_listing
        self.pagesize = bika_listing.pagesize
        folderitems = bika_listing.folderitems()
        if self.pagesize == 0:
            self.pagesize = len(folderitems)
        bika_listing.items = folderitems
        self.hide_hidden_attributes()

        if hasattr(self.bika_listing, 'manual_sort_on') \
           and self.bika_listing.manual_sort_on:
            mso = self.bika_listing.manual_sort_on
            if type(mso) in (list, tuple):
                self.bika_listing.manual_sort_on = mso[0]
            psi = self.bika_listing.page_start_index
            psi = psi and psi or 0
            # We do a sort of the current page using self.manual_sort_on, here
            page = folderitems[psi:psi+self.pagesize]
            page.sort(lambda x,y:cmp(x.get(self.bika_listing.manual_sort_on, ''),
                                     y.get(self.bika_listing.manual_sort_on, '')))

            if self.bika_listing.sort_order[0] in ['d','r']:
                page.reverse()

            folderitems = folderitems[:psi] \
                + page \
                + folderitems[psi+self.pagesize:]


        tableview.Table.__init__(self,
                                 bika_listing.request,
                                 bika_listing.base_url,
                                 bika_listing.view_url,
                                 folderitems,
                                 pagesize = self.pagesize)

        self.context = bika_listing.context
        self.request = bika_listing.request
        self.form_id = bika_listing.form_id
        self.items = folderitems

    def rendered_items(self, cat=None, **kwargs):
        """
        Render the table rows of items in a particular category.
        :param cat: the category ID with which we will filter the results
        :param review_state: the current review_state from self.review_states
        :param kwargs: all other keyword args are set as attributes of
                       self and self.bika_listing, for injecting attributes
                       that templates require.
        :return: rendered HTML text
        """
        self.cat = cat
        for key,val in kwargs.items():
            self.__setattr__(key, val)
            self.bika_listing.__setattr__(key, val)
        selected_cats = self.bika_listing.selected_cats(self.batch)
        self.this_cat_selected = cat in selected_cats
        self.this_cat_batch = []
        for item in self.batch:
            if item.get('category', 'None') == cat:
                self.this_cat_batch.append(item)
        return self.render_items()

    def hide_hidden_attributes(self):
        """Use the bika_listing's contentFilter's portal_type
        values, if any, to remove fields from review_states if they
        are marked as hidden in the registry.
        """
        if 'portal_type' not in self.bika_listing.contentFilter:
            return
        ptlist = self.bika_listing.contentFilter['portal_type']
        if isinstance(ptlist, basestring):
            ptlist = [ptlist, ]
        new_states = []
        for portal_type in ptlist:
            hiddenattributes = getHiddenAttributesForClass(portal_type)
            for i, state in enumerate(self.bika_listing.review_states):
                for field in state['columns']:
                    if field in hiddenattributes:
                        state['columns'].remove(field)
                new_states.append(state)
        self.bika_listing.review_states = new_states

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i
