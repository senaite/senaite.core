# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
import copy
import DateTime
import json
import re
import time
import Missing
from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF, api, deprecated, logger
from bika.lims.api import (get_current_user, get_object, get_object_by_uid,
                           get_tool, get_transitions_for)
from bika.lims.browser import BrowserView
from bika.lims.interfaces import (IFieldIcons, ITopLeftHTMLComponentsHook,
                                  ITopRightHTMLComponentsHook,
                                  ITopWideHTMLComponentsHook)
from bika.lims.utils import (getFromString, getHiddenAttributesForClass,
                             isActive, t, to_utf8)
from bika.lims.workflow import doActionFor, skip
from plone.app.content.browser import tableview
from plone.memoize import view as viewcache
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters, getMultiAdapter

COOKIE_LISTING_FILTER_BAR = "bika_listing_filter_bar"


class WorkflowAction:
    """Workflow actions taken in any Bika contextAnalysisRequest context

    This function provides the default behaviour for workflow actions
    invoked from bika_listing tables.

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
        self.portal = api.get_portal()
        self.addPortalMessage = self.context.plone_utils.addPortalMessage

    def _get_form_workflow_action(self):
        """Retrieve the workflow action from the submitted form
            - "workflow_action" is the edit border transition
            - "workflow_action_button" is the bika_listing table buttons
        """
        request = self.request
        form = request.form
        came_from = "workflow_action"
        action = form.get(came_from, '')

        if not action:
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    url = self.context.absolute_url()
                    self.destination_url = request.get_header("referer", url)
                request.response.redirect(self.destination_url)
                return None, None

        # A condition in the form causes Plone to sometimes send two actions
        if type(action) in (list, tuple):
            action = action[0]

        return action, came_from

    def _get_selected_items(self):
        """return a list of selected form objects
           full_objects defaults to True
        """
        form = self.request.form
        uids = form.get("uids", [])
        selected_items = collections.OrderedDict()
        for uid in uids:
            obj = get_object_by_uid(uid)
            if obj:
                selected_items[uid] = obj
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
                self.addPortalMessage(message, 'info')
            if dest:
                self.request.response.redirect(dest)
                return
        else:
            message = _('No items selected')
            self.addPortalMessage(message, 'warn')
        self.request.response.redirect(self.destination_url)
        return

    def workflow_action_copy_to_new(self):
        """Invoke the ar_add form in the current context, passing the UIDs of
        the source ARs as request parameters.
        """
        objects = self._get_selected_items()
        if not objects:
            message = self.context.translate(
                _("No analyses have been selected"))
            self.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url() + "/batchbook"
            self.request.response.redirect(self.destination_url)
            return

        url = self.context.absolute_url() + "/ar_add" + \
            "?ar_count={0}".format(len(objects)) + \
            "&copy_from={0}".format(",".join(objects.keys()))

        self.request.response.redirect(url)
        return

    def workflow_action_print_stickers(self):
        """Invoked from AR or Sample listings in the current context, passing
        the uids of the selected items and default sticker template as request
        parameters to the stickers rendering machinery, that generates the PDF
        """
        uids = self.request.form.get("uids", [])
        if not uids:
            message = self.context.translate(
                _("No ARs have been selected"))
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
            return

        url = '{0}/sticker?autoprint=1&template={1}&items={2}'.format(
            self.context.absolute_url(),
            self.portal.bika_setup.getAutoStickerTemplate(),
            ','.join(uids)
        )
        self.request.response.redirect(url)

    def __call__(self):
        request = self.request
        form = request.form

        if self.destination_url == "":
            self.destination_url = request.get_header(
                "referer", self.context.absolute_url())

        action, came_from = self._get_form_workflow_action()

        if action:
            # bika_listing sometimes gives us a list of items?
            if type(action) == list:
                action = action[0]
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
        elif form.get('bika_listing_filter_bar_submit', ''):
            # Getting all the filter inputs with the key starting with:
            # 'bika_listing_filter_bar_'
            filter_val = \
                [[k, v] for k, v in form.items()
                 if k.startswith('bika_listing_filter_bar_')]
            filter_val = json.dumps(filter_val)
            # Adding the filter parameters to cookue
            self.request.response.setCookie(
                'bika_listing_filter_bar', filter_val, path='/', max_age=10)
        else:
            # Do nothing
            self.request.response.redirect(self.destination_url)
            return

    # noinspection PyUnusedLocal
    def submitTransition(self, action, came_from, items):
        """Performs the action's transition for the specified items

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
                allowed_transitions = \
                    [it['id'] for it in workflow.getTransitionsFor(item)]
                if action in allowed_transitions:
                    # if action is "verify" and the item is an analysis or
                    # reference analysis, check if the if the required number
                    # of verifications done for the analysis is, at least,
                    # the number of verifications performed previously+1
                    if (action == 'verify' and
                            hasattr(item, 'getNumberOfVerifications') and
                            hasattr(item, 'getNumberOfRequiredVerifications')):
                        success = True
                        message = "Unknown error while submitting."
                        revers = item.getNumberOfRequiredVerifications()
                        nmvers = item.getNumberOfVerifications()
                        member = get_current_user()
                        username = member.getUserName()
                        item.addVerificator(username)
                        if revers - nmvers <= 1:
                            success, message = doActionFor(item, action)
                            if not success:
                                # If failed, delete last verificator.
                                item.deleteLastVerificator()
                        item.reindexObject()
                    else:
                        success, message = doActionFor(item, action)
                    if success:
                        transitioned.append(item.id)
                    else:
                        self.addPortalMessage(message, 'error')

        # automatic label printing
        if transitioned \
                and action == 'receive' \
                and 'receive' in self.portal.bika_setup.getAutoPrintStickers():
            q = "/sticker?template=%s&items=" % \
                (self.portal.bika_setup.getAutoStickerTemplate())
            # selected_items is a list of UIDs (stickers for AR_add use IDs)
            q += ",".join(transitioned)
            dest = self.context.absolute_url() + q
            self.destination_url = dest

        return len(transitioned), dest


class BikaListingView(BrowserView):
    """Base View for Bika Table Listings
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
    pagesize = 30

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
    # and completed inline.  This is useful for lists which will have many
    # thousands of entries in many categories, where loading the entire list
    # in HTML would be very slow.
    # If you want to use service categories set this option ajax_categories_url
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

    # Sort with JS when a column does not have an index associated.
    # It's not useful if the table is paginated since
    # it only searches visible items
    manual_sort_on = None

    # Column definitions:
    #
    # The keys of the columns dictionary must all exist in all
    # items returned by subclassing view's .folderitems method.
    #
    # Blank entries are inserted in the default folderitems for
    # all entries without values.
    #
    # Possible column dictionary keys are:
    #
    # - allow_edit:
    #   This field is made editable.
    #   Interim fields are always editable
    #
    # - type:
    #   "string"    is the default.
    #   "boolean"   a checkbox is rendered
    #   "date"      A text field is rendered, with a jquery DatePicker attached.
    #   "choices"   Renders a dropdown.  The vocabulary data must be placed in
    #               item['choices'][column_id]. It's a list of dictionaries:
    #               [{'ResultValue':x}, {'ResultText',x}].
    #
    # - index:
    #   The name of the catalog index for the column. Allows full-table
    #   sorting.
    #
    # - sortable:
    #   If False, adds nosort class to this column.
    #
    # - toggle:
    #   Enable/disable column toggle ability.
    #
    # - input_class:
    #   CSS class applied to input widget in edit mode
    #   autosave: when js detects this variable as 'true',
    #   the system will save the value after been
    #   introduced via ajax.
    #
    # - input_width:
    #   Size attribute applied to input widget in edit mode
    #
    # - attr:
    #   The name of the catalog column/metadata field from where to retrieve
    # the data
    #   that will be rendered in the column for a particular object. If not
    # specified
    #   then the column key will be used as this value. As an example:
    #
    #   self.columns = {
    #       'file_size': {
    #            'title': _("Size"),
    #            'attr': 'getFileSize',
    #            'sortable': False, }, }
    #
    #   ^Here, getFileSize will be used to retrieve the data
    #
    #   self.columns = {
    #       'file_size': {
    #            'title': _("Size"),
    #            'sortable': False, }, }
    #
    #   ^Here, file_size will be used to retrieve the data
    #
    # - title:
    #   Title that will be used to name the column when rendered
    #
    # - replace_url:
    #   if replace_url:
    #         attrobj = getFromString(obj, replace_url)
    #         if attrobj:
    #             results_dict['replace'][key] = \
    #                 '<a href="%s">%s</a>' % (attrobj, value)
    #

    columns = {
        'obj_type': {'title': _('Type')},
        'id': {'title': _('ID')},
        'title_or_id': {'title': _('Title')},
        'modified': {'title': _('Last modified')},
        'state_title': {'title': _('State')},
    }

    # BBB: Not used anymore
    filter_indexes = []

    # The current or default review_state when one hasn't been selected.
    # With this setting, BikaListing instances must be careful to change it,
    # without having valid review_state existing in self.review_states
    default_review_state = 'default'

    # review_state
    #
    # A list of dictionaries, specifying parameters for listing filter buttons.
    # - If review_state[x]['transitions'] is defined it's a list of dictionaries
    #     [{'id':'x'}]
    # Transitions will be ordered by and restricted to, these items.
    #
    # - If review_state[x]['custom_transitions'] is defined it's a list of dict:
    #     [{'id':'x'}]
    # These transitions will be forced into the list of workflow actions.
    # They will need to be handled manually in the appropriate WorkflowAction
    # subclass.
    review_states = [
        {
            'id': 'default',
            'contentFilter': {},
            'title': _('All'),
            'columns': ['obj_type', 'title_or_id', 'modified', 'state_title']
        },
    ]

    # The advanced filter bar instance, it is initialized using
    # getAdvancedFilterBar
    _advfilterbar = None

    # The following variable will contain an instance that checks whether the
    # logged in user has a certain permission for some object.
    # Save getSecurityManager() in this variable and then use
    # security_manager.checkPermission(ModifyPortalContent, obj)
    security_manager = None

    def __init__(self, context, request, **kwargs):
        """View constructor
        """
        super(BikaListingView, self).__init__(context, request)
        logger.info(u"ListingView::__init__")

        # set context and request for that view
        self.context = context
        self.request = request

        self.base_url = context.absolute_url()
        self.field_icons = {}
        self.items = []
        self.limit_from = 0
        self.member = None
        self.mtool = None
        self.show_all = False
        self.show_more = False
        self.sort_on = None
        self.sort_order = 'ascending'
        self.view_url = self.base_url
        self.workflow = None

        # N.B. We set that here so that it can be overridden by subclasses,
        #      e.g. by the worksheet add view
        if "path" not in self.contentFilter:
            self.contentFilter.update(self.get_path_query())

        # The listing object is bound to a class called BikaListingFilterBar
        # which can display an additional filter bar in the listing view in
        # order to filter the items by some terms. These terms should be
        # difined in the BikaListingFilterBar class following the descripton
        # and examples. This variable is overriden in other views, in order to
        # show the bar or not depending on the list. For example, Analysis
        # Requests view checks bika_setup.getSamplingBarEnabledAnalysisRequests
        # to know if the functionality is activeated or not for its views.
        self.filter_bar_enabled = False

        # Stores the translations of the statuses from the items displayed in
        # this list. It value is set automatically in folderitems function.
        self.state_titles = {}

        if 'show_categories' in kwargs:
            self.show_categories = kwargs["show_categories"]

        if 'expand_all_categories' in kwargs:
            self.expand_all_categories = kwargs["expand_all_categories"]

    def __call__(self):
        """Handle request parameters and render the form
        """
        logger.info(u"ListingView::__call__")

        # Always update on __call__
        self.update()

        form_id = self.get_form_id()

        # If table_only specifies another form_id, then we abort.
        # this way, a single table among many can request a redraw,
        # and only it's content will be rendered.
        if not self.get_table_only(form_id):
            return ""
        if not self.get_rows_only(form_id):
            return ""

        # ajax_categories, basic sanity.
        # we do this here to allow subclasses time to define these things.
        if self.ajax_categories and not self.category_index:
            msg = "category_index must be defined when using ajax_categories."
            raise AssertionError(msg)

        # ajax_category_expand is included in the form if this form submission
        # is an asynchronous one triggered by a category being expanded.
        if self.request.get('ajax_category_expand', False):
            # - get nice formatted category contents (tr rows only)
            return self.rendered_items()

        # render
        self.before_render()

        if self.get_table_only():
            return self.contents_table(table_only=form_id)
        if self.get_rows_only():
            return self.contents_table(table_only=form_id)
        else:
            return self.template(self.context)

    def update(self):
        """Update the view state
        """
        logger.info(u"ListingView::update")

        self.portal = api.get_portal()
        self.mtool = api.get_tool("portal_membership")
        self.workflow = api.get_tool("portal_workflow")
        self.member = api.get_current_user()
        self.translate = self.context.translate

        # Sanitize the request form
        # XXX When does this happen?
        if self.request.form:
            for key, value in self.request.form.items():
                if isinstance(value, list):
                    self.request.form[key] = self.request.form[key][0]

        self.rows_only = self.get_rows_only()
        self.limit_from = self.get_limit_from()

        # setup filter bar
        filter_bar_config = self.read_filter_bar_cookie()
        self.set_filter_bar_config(filter_bar_config)

        # pagesize
        self.pagesize = self.get_pagesize()
        # Plone's batching wants this variable:
        self.request.set('pagesize', self.pagesize)
        # and we want to make our choice remembered in bika_listing also
        self.request.set(self.form_id + '_pagesize', self.pagesize)

        # get toggle_cols cookie value
        # and modify self.columns[]['toggle'] to match.
        toggle_cols = self.get_toggle_cols()
        for col in self.columns.keys():
            self.columns[col]['toggle'] = col in toggle_cols

    def before_render(self):
        """Before render hook
        """
        logger.info(u"ListingView::before_render")

    @deprecated("Please use BikaListingView.update()")
    def _process_request(self):
        """BBB
        """
        self.update()

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

    def getPOSTAction(self):
        """This function returns a string as the value for the action attribute
        of the form element in the template.

        This method is used in bika_listing_table.pt
        """
        return 'workflow_action'

    def get_form_id(self):
        """Return the form id

        Note: The form_id must be unique when rendering multiple listing tables
        """
        return self.form_id

    def parse_json(self, data):
        """Parses the given json data
        """
        try:
            return json.loads(data)
        except (ValueError, TypeError):
            return None

    def read_filter_bar_cookie(self):
        """Read the filter bar cookie
        """
        # get the cookie
        cookie_value = self.request.get(COOKIE_LISTING_FILTER_BAR, [])

        # not sure why this is needed...
        self.unset_cookie(COOKIE_LISTING_FILTER_BAR)

        config = self.parse_json(cookie_value)
        if config is None:
            config = []
        logger.info(u"ListingView::read_filter_bar_cookie: config={}".format(config))
        return config

    def set_filter_bar_config(self, config):
        """Set the filter bar values

        :param config: list of dictionaries
        """
        cookie_data = {}
        for k, v in config:
            cookie_data[k] = v
        self.save_filter_bar_values(cookie_data)

    def set_cookie(self, cookie, value, **kw):
        """Set cookie

        :param cookie: The cookie name
        :param value: The cookie value
        :param kw: The keyword arguments to be set on the cookie
        """
        response = self.request.response
        response.setCookie(cookie, value, **kw)

    def unset_cookie(self, cookie):
        """Unset cookie

        :param cookie: The cookie name
        """
        self.set_cookie(cookie, value=None)
        response = self.request.response
        response.setCookie(cookie, None, path="/", max_age=0)

    def get_pagesize(self):
        """Return the pagesize request parameter
        """
        form_id = self.get_form_id()
        pagesize = self.request.get(form_id + '_pagesize', self.pagesize)
        try:
            return int(pagesize)
        except (ValueError, TypeError):
            return self.pagesize

    def get_limit_from(self):
        """Return the limit_from request parameter
        """
        form_id = self.get_form_id()
        limit = self.request.get(form_id + '_limit_from', 0)
        try:
            return int(limit)
        except (ValueError, TypeError):
            return 0

    def get_rows_only(self, default=""):
        """Checks if the rows_only request parameter is equal to form_id
        """
        form_id = self.get_form_id()
        rows_only = self.request.get("rows_only", default)
        return rows_only == form_id

    def get_table_only(self, default=""):
        """Checks if the table_only request parameter is equal to form_id
        """
        form_id = self.get_form_id()
        table_only = self.request.get("table_only", default)
        return table_only == form_id

    def get_toggle_cols(self):
        """Returns the list of column ids to be displayed for the current list.

        :returns: list of column ids to be displayed
        """
        # Get the toggle configuration from the cookie
        cookie_toggle = self.request.get('toggle_cols', '{}')
        cookie_toggle = json.loads(cookie_toggle)

        # Load the toggling configuration for the current list
        list_toggle_key = "%s%s" % (self.context.portal_type, self.form_id)
        list_toggle = cookie_toggle.get(list_toggle_key, [])

        # If there is no stored configuration re toggle for the current list
        # in the cookie (or if there is no cookie for toggle config), use the
        # default configuration based on the initial column settings
        if not list_toggle:
            columns_ids = self.review_state['columns']
            list_toggle = [col_id for col_id in columns_ids if
                           self.columns[col_id].get('toggle', True) is True]

        return list_toggle

    def GET_url(self, include_current=True, **kwargs):
        """Handler for the "Show More" Button
        """

        url = self.request['URL'].split("?")[0]
        # take values from form (both html form and GET request slurped here)
        query = {}
        if include_current:
            for k, v in self.request.form.items():
                if k.startswith(self.form_id + "_") and "uids" not in k:
                    query[k] = v

        # override from self attributes
        for x in ["pagesize",
                  "review_state",
                  "sort_order",
                  "sort_on",
                  "limit_from"]:
            if str(getattr(self, x, None)) != 'None':
                # I don't understand why on AR listing, getattr(self,x)
                # is a dict, but this line will resolve LIMS-1420
                if x == "review_state" and type(getattr(self, x)) == dict:
                    query['%s_%s' % (self.form_id, x)] = getattr(self, x)['id']
                else:
                    query['%s_%s' % (self.form_id, x)] = getattr(self, x)
        # then override with passed kwargs
        for x in kwargs.keys():
            query['%s_%s' % (self.form_id, x)] = kwargs.get(x)
        if query:
            url = url + "?" + "&".join(["%s=%s" % (x, y)
                                        for x, y in query.items()])
        return url

    def remove_column(self, column):
        """Removes the column passed-in, if exists

        :param column: Column key
        :returns: True if the column was removed
        """
        if column not in self.columns:
            return False

        del self.columns[column]
        for item in self.review_states:
            if column in item.get('columns', []):
                item['columns'].remove(column)
        return True

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

    # noinspection PyUnusedLocal
    def restricted_cats(self, items):
        """Return a list of categories that will not be displayed.

        The items will still be present, and account for a part of the page
        batch total.

        :param items: A list of items returned from self.folderitems().
        :return: a list of AnalysisCategory instances.
        """
        return []

    # noinspection PyUnusedLocal
    def isItemAllowed(self, obj):
        """ return if the item can be added to the items list.
        """
        return True

    def get_item_info(self, brain_or_object):
        """Return the data of this brain or object
        """
        return {
            "obj": brain_or_object,
            "uid": api.get_uid(brain_or_object),
            "url": api.get_url(brain_or_object),
            "id": api.get_id(brain_or_object),
            "title": api.get_title(brain_or_object),
            "portal_type": api.get_portal_type(brain_or_object),
            "review_state": getattr(brain_or_object, "review_state", ""),
        }

    # noinspection PyUnusedLocal
    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        return item

    def folderitems(self, full_objects=False, classic=True):
        """This function returns an array of dictionaries where each dictionary
        contains the columns data to render the list.

        No object is needed by default. We should be able to get all
        the listing columns taking advantage of the catalog's metadata,
        so that the listing will be much more faster. If a very specific
        info has to be retrieve from the objects, we can define
        full_objects as True but performance can be lowered.

        :full_objects: a boolean, if True, each dictionary will contain an item
                       with the object itself. item.get('obj') will return a
                       object. Only works with the 'classic' way.
        WARNING: :full_objects: could create a big performance hit!
        :classic: if True, the old way folderitems works will be executed. This
                  function is mainly used to maintain the integrity with the
                  old version.
        """
        # Getting a security manager instance for the current request
        self.security_manager = getSecurityManager()
        self.workflow = getToolByName(self.context, 'portal_workflow')

        if classic:
            return self._folderitems(full_objects)

        # idx increases one unit each time an object is added to the 'items'
        # dictionary to be returned. Note that if the item is not rendered,
        # the idx will not increase.
        idx = 0
        results = []
        self.show_more = False
        brains = self._fetch_brains(self.limit_from)
        for obj in brains:
            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            # we only take allowed items into account
            if idx >= self.pagesize:
                # Maximum number of items to be shown reached!
                self.show_more = True
                break

            # check if the item must be rendered or not (prevents from

            # doing it later in folderitems) and dealing with paging
            if not obj or not self.isItemAllowed(obj):
                continue

            # Get the css for this row in accordance with the obj's state
            states = obj.getObjectWorkflowStates
            if not states:
                states = {}
            state_class = ['state-{0}'.format(v) for v in states.values()]
            state_class = ' '.join(state_class)

            # Building the dictionary with basic items
            results_dict = dict(
                # To colour the list items by state
                state_class=state_class,
                # a list of names of fields that may be edited on this item
                allow_edit=[],
                # a dict where the column name works as a key and the value is
                # the name of the field related with the column. It is used
                # when the name given to the column and the content field it
                # represents diverges. bika_listing_table_items.pt defines an
                # attribute for each item, this attribute is named 'field' and
                # the system fills it taking advantage of this dictionary or
                # the name of the column if it isn't defined in the dict.
                field={},
                # "before", "after" and replace: dictionary (key is column ID)
                # A snippet of HTML which will be rendered
                # before/after/instead of the table cell content.
                before={},  # { before : "<a href=..>" }
                after={},
                replace={},
                choices={},
            )

            # update with the base item info
            results_dict.update(self.get_item_info(obj))

            # Set states and state titles
            ptype = obj.portal_type
            workflow = get_tool('portal_workflow')
            for state_var, state in states.items():
                results_dict[state_var] = state
                state_title = self.state_titles.get(state, None)
                if not state_title:
                    state_title = workflow.getTitleForStateOnType(state, ptype)
                    if state_title:
                        self.state_titles[state] = state_title
                if state_title and state == obj.review_state:
                    results_dict['state_title'] = _(state_title)

            # extra classes for individual fields on this item
            # { field_id : "css classes" }
            results_dict['class'] = {}

            # Search for values for all columns in obj
            for key in self.columns.keys():
                # if the key is already in the results dict
                # then we don't replace it's value
                value = results_dict.get(key, '')
                if not value:
                    attrobj = getFromString(obj, key)
                    value = attrobj if attrobj else value

                    # Custom attribute? Inspect to set the value
                    # for the current column dynamically
                    vattr = self.columns[key].get('attr', None)
                    if vattr:
                        attrobj = getFromString(obj, vattr)
                        value = attrobj if attrobj else value
                    results_dict[key] = value
                # Replace with an url?
                replace_url = self.columns[key].get('replace_url', None)
                if replace_url:
                    attrobj = getFromString(obj, replace_url)
                    if attrobj:
                        results_dict['replace'][key] = \
                            '<a href="%s">%s</a>' % (attrobj, value)
            # The item basics filled. Delegate additional actions to folderitem
            # service. folderitem service is frequently overriden by child
            # objects
            item = self.folderitem(obj, results_dict, idx)
            if item:
                results.append(item)
                idx += 1
        return results

    def get_catalog(self, default="portal_catalog"):
        """Get the catalog tool to be used in the listing

        :returns: ZCatalog tool
        """
        try:
            return api.get_tool(self.catalog)
        except api.BikaLIMSError:
            return api.get_tool(default)

    @viewcache.memoize
    def get_catalog_indexes(self):
        """Return a list of registered catalog indexes
        """
        return self.get_catalog().indexes()

    @viewcache.memoize
    def get_columns_indexes(self):
        """Returns a list of allowed sorting indexeds
        """
        columns = self.columns
        indexes = [v["index"] for k, v in columns.items() if "index" in v]
        return indexes

    def get_sort_order(self):
        """Get the sort_order criteria from the request or view
        """
        form_id = self.get_form_id()
        key = "{}_sort_order".format(form_id)
        sort_order = self.request.get(key, None)

        if sort_order is None:
            sort_order = self.contentFilter.get("sort_order", self.sort_order)
        if sort_order not in ["ascending", "descending"]:
            sort_order = "descending"

        return sort_order

    def is_valid_sort_index(self, sort_on):
        """Checks if the sort_on index is capable for a sort_

        :param sort_on: The name of the sort index
        :returns: True if the sort index is capable for sorting
        """
        # List of known catalog indexes
        catalog_indexes = self.get_catalog_indexes()
        if sort_on not in catalog_indexes:
            return False
        catalog = self.get_catalog()
        sort_index = catalog.Indexes.get(sort_on)
        if not hasattr(sort_index, 'documentToKeyMap'):
            return False
        return True

    def get_sort_on(self, default="created"):
        """Get the sort_on criteria to be used

        :param default: The default sort_on index to be used
        :returns: valid sort_on index or None
        """
        form_id = self.get_form_id()
        key = "{}_sort_on".format(form_id)

        # List of known catalog columns
        catalog_columns = self.get_metadata_columns()

        # The sort_on parameter from the request
        sort_on = self.request.get(key, None)
        # Use the index specified in the columns config
        if sort_on in self.columns:
            sort_on = self.columns[sort_on].get("index", sort_on)

        # Return immediately if the request sort_on parameter is found in the
        # catalog indexes
        if self.is_valid_sort_index(sort_on):
            return sort_on

        # Flag manual sorting if the request sort_on parameter is found in the
        # catalog metadata columns
        if sort_on in catalog_columns:
            self.manual_sort_on = sort_on

        # The sort_on parameter from the catalog query
        content_filter_sort_on = self.contentFilter.get("sort_on", None)
        if self.is_valid_sort_index(content_filter_sort_on):
            return content_filter_sort_on

        # The sort_on attribute from the instance
        instance_sort_on = self.sort_on
        if self.is_valid_sort_index(instance_sort_on):
            return instance_sort_on

        # The default sort_on
        if self.is_valid_sort_index(default):
            return default

        return None

    def get_path_query(self, context=None, level=0):
        """Return a path query

        :param context: The context to get the physical path from
        :param level: The depth level of the search
        :returns: Catalog path query
        """
        if context is None:
            context = self.context
        path = api.get_path(context)
        return {
            "path": {
                "query": path,
                "level": level,
            }
        }

    def get_catalog_query(self, searchterm=None):
        """Return the catalog query

        :param searchterm: Additional filter value to be added to the query
        :returns: Catalog query dictionary
        """

        # avoid to change the original content filter
        query = copy.deepcopy(self.contentFilter)

        # contentFilter is allowed in every self.review_state.
        for k, v in self.review_state.get("contentFilter", {}).items():
            query[k] = v

        # set the sort_on criteria
        sort_on = self.get_sort_on()
        if sort_on is not None:
            query["sort_on"] = sort_on

        # set the sort_order criteria
        query["sort_order"] = self.get_sort_order()

        # # Pass the searchterm as well to the Searchable Text index
        # if searchterm and isinstance(searchterm, basestring):
        #     query.update({"SearchableText": searchterm + "*"})

        # Adding the extra filtering elements
        extra = self.get_filter_bar_queryaddition() or {}
        query.update(extra)

        logger.info(u"ListingView::get_catalog_query: query={}".format(query))
        return query

    @viewcache.memoize
    def get_metadata_columns(self):
        """Get a list of all metadata column names

        :returns: List of catalog metadata column names
        """
        catalog = self.get_catalog()
        return catalog.schema()

    def is_date(self, thing):
        """checks if the passed in value is a date

        :param thing: an arbitrary object
        :returns: True if it can be converted to a date time object
        """
        if isinstance(thing, DateTime.DateTime):
            return True
        return False

    def to_str_date(self, date):
        """Converts the date to a string

        :param date: DateTime object or ISO date string
        :returns: locale date string
        """
        date = DateTime.DateTime(date)
        try:
            return date.strftime(self.date_format_long)
        except ValueError:
            return str(date)

    @viewcache.memoize
    def translate_review_state(self, state, portal_type):
        """Translates the review state to the current set language

        :param state: Review state title
        :type state: basestring
        :returns: Translated review state title
        """
        ts = api.get_tool("translation_service")
        wf = api.get_tool("portal_workflow")
        state_title = wf.getTitleForStateOnType(state, portal_type)
        translated_state = ts.translate(_(state_title or state), context=self.request)
        logger.info(u"ListingView:translate_review_state: {} -> {} -> {}"
                    .format(state, state_title, translated_state))
        return translated_state

    def metadata_to_searchable_text(self, brain, key, value):
        """Parse the given metadata to text

        :param brain: ZCatalog Brain
        :param key: The name of the metadata column
        :param value: The raw value of the metadata column
        :returns: Searchable and translated unicode value or None
        """
        if not value:
            return u""
        if value is Missing.Value:
            return u""
        if api.is_uid(value):
            return u""
        if isinstance(value, (bool)):
            return u""
        if isinstance(value, (list, tuple)):
            for v in value:
                return self.metadata_to_searchable_text(brain, key, v)
        if isinstance(value, (dict)):
            for k, v in value.items():
                return self.metadata_to_searchable_text(brain, k, v)
        if self.is_date(value):
            return self.to_str_date(value)
        if "state" in key.lower():
            return self.translate_review_state(value, api.get_portal_type(brain))
        if not isinstance(value, basestring):
            value = str(value)
        return safe_unicode(value)

    def make_regex_for(self, searchterm, ignorecase=True):
        """Make a regular expression for the given searchterm

        :param searchterm: The searchterm for the regular expression
        :param ignorecase: Flag to compile with re.IGNORECASE
        :returns: Compiled regular expression
        """
        # searchterm comes in as a 8-bit string, e.g. 'D\xc3\xa4'
        # but must be a unicode u'D\xe4' to match the metadata
        searchterm = safe_unicode(searchterm)
        if ignorecase:
            return re.compile(searchterm, re.IGNORECASE)
        return re.compile(searchterm)

    def sort_brains(self, brains, sort_on=None):
        """Sort the brains

        :param brains: List of catalog brains
        :param sort_on: The metadata column name to sort on
        :returns: Manually sorted list of brains
        """
        if sort_on not in self.get_metadata_columns():
            logger.warn("ListingView::sort_brains: '{}' not in metadata columns."
                        .format(sort_on))
            return brains

        logger.warn("ListingView::sort_brains: Manual sorting on metadata column '{}'. "
                    "Consider to add an explicit catalog index to speed up filtering."
                    .format(self.manual_sort_on))

        # calculate the sort_order
        reverse = self.get_sort_order() == "descending"

        def metadata_sort(a, b):
            a = getattr(a, self.manual_sort_on, "")
            b = getattr(b, self.manual_sort_on, "")
            return cmp(safe_unicode(a), safe_unicode(b))

        return sorted(brains, cmp=metadata_sort, reverse=reverse)

    def search(self, searchterm="", ignorecase=True):
        """Search the catalog tool

        :param searchterm: The searchterm for the regular expression
        :param ignorecase: Flag to compile with re.IGNORECASE
        :returns: List of catalog brains
        """

        # TODO Append start and pagesize to return just that slice of results

        # start the timer for performance checks
        start = time.time()

        # strip whitespaces off the searchterm
        searchterm = searchterm.strip()
        # strip illegal characters off the searchterm
        searchterm = searchterm.strip(u"*.!$%&/()=-+:'`´^")
        logger.info(u"ListingView::search:searchterm='{}'".format(searchterm))

        # create a catalog query
        logger.info(u"ListingView::search: Prepare catalog query for '{}'"
                    .format(self.catalog))
        query = self.get_catalog_query(searchterm=searchterm)

        # search the catalog
        catalog = api.get_tool(self.catalog)
        brains = catalog(query)

        # Sort manually?
        if self.manual_sort_on is not None:
            brains = self.sort_brains(brains, sort_on=self.manual_sort_on)

        # return the unfiltered catalog results
        if not searchterm:
            logger.info(u"ListingView::search: return {} results".format(len(brains)))
            return brains

        # Always expand all categories if we have a searchterm
        self.expand_all_categories = True

        # Build a regular expression for the given searchterm
        regex = self.make_regex_for(searchterm, ignorecase=ignorecase)

        # Get the catalog metadata columns
        columns = self.get_metadata_columns()

        # Filter predicate to match each metadata value against the searchterm
        def match(brain):
            for column in columns:
                value = getattr(brain, column, None)
                parsed = self.metadata_to_searchable_text(brain, column, value)
                if regex.search(parsed):
                    return True
            return False

        # Filtered brains by searchterm -> metadata match
        out = filter(match, brains)

        end = time.time()
        logger.info(u"ListingView::search: Search for '{}' executed in {:.2f}s ({} matches)"
                    .format(searchterm, end - start, len(out)))
        return out

    def get_searchterm(self):
        """Get the user entered search value from the request

        :returns: Current search box value from the request
        """
        form_id = self.get_form_id()
        key = "{}_filter".format(form_id)
        # we need to ensure unicode here
        return safe_unicode(self.request.get(key, ""))

    def _fetch_brains(self, idxfrom=0):
        """Fetch the catalog results for the current listing table state
        """

        searchterm = self.get_searchterm()
        brains = self.search(searchterm=searchterm)

        # Return a subset of results, if necessary
        if idxfrom and len(brains) > idxfrom:
            return brains[idxfrom:]
        return brains

    # noinspection PyUnusedLocal
    @deprecated("Using bikalisting.folderitems(classic=True) is very slow")
    def _folderitems(self, full_objects=False):
        """WARNING: :full_objects: could create a big performance hit.
        """
        # Setting up some attributes
        plone_layout = getMultiAdapter((self.context.aq_inner, self.request),
                                       name=u'plone_layout')
        plone_utils = getToolByName(self.context.aq_inner, 'plone_utils')
        portal_types = getToolByName(self.context.aq_inner, 'portal_types')
        if self.request.get('show_all', '').lower() == 'true' \
                or self.show_all is True \
                or self.pagesize == 0:
            show_all = True
        else:
            show_all = False

        # idx increases one unit each time an object is added to the 'items'
        # dictionary to be returned. Note that if the item is not rendered,
        # the idx will not increase.
        idx = 0
        results = []
        self.show_more = False
        brains = self._fetch_brains(self.limit_from)
        for obj in brains:
            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            # we only take allowed items into account
            if not show_all and idx >= self.pagesize:
                # Maximum number of items to be shown reached!
                self.show_more = True
                break

            # we don't know yet if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                "/".join(obj.getPhysicalPath())

            # This item must be rendered, we need the object instead of a brain
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj

            # check if the item must be rendered or not (prevents from
            # doing it later in folderitems) and dealing with paging
            if not obj or not self.isItemAllowed(obj):
                continue

            uid = obj.UID()
            title = obj.Title()
            description = obj.Description()
            icon = plone_layout.getIcon(obj)
            url = obj.absolute_url()
            relative_url = obj.absolute_url(relative=True)

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
            for w in self.workflow.getWorkflowsFor(obj):
                state = w._getWorkflowStateOf(obj).id
                states[w.state_var] = state
                state_class += "state-%s " % state

            results_dict = dict(
                obj=obj,
                id=obj.getId(),
                title=title,
                uid=uid,
                path=path,
                url=url,
                fti=fti,
                item_data=json.dumps([]),
                url_href_title=url_href_title,
                obj_type=obj.Type,
                size=obj.getObjSize,
                modified=modified,
                icon=icon.html_tag(),
                type_class=type_class,
                # a list of lookups for single-value-select fields
                choices={},
                state_class=state_class,
                relative_url=relative_url,
                view_url=url,
                table_row_class="",
                category='None',

                # a list of names of fields that may be edited on this item
                allow_edit=[],

                # a list of names of fields that are compulsory (if editable)
                required=[],
                # a dict where the column name works as a key and the value is
                # the name of the field related with the column. It is used
                # when the name given to the column and the content field it
                # represents diverges. bika_listing_table_items.pt defines an
                # attribute for each item, this attribute is named 'field' and
                # the system fills it taking advantage of this dictionary or
                # the name of the column if it isn't defined in the dict.
                field={},
                # "before", "after" and replace: dictionary (key is column ID)
                # A snippet of HTML which will be rendered
                # before/after/instead of the table cell content.
                before={},  # { before : "<a href=..>" }
                after={},
                replace={},
            )

            rs = None
            wf_state_var = None

            workflows = self.workflow.getWorkflowsFor(obj)
            for wf in workflows:
                if wf.state_var:
                    wf_state_var = wf.state_var
                    break

            if wf_state_var is not None:
                rs = self.workflow.getInfoFor(obj, wf_state_var)
                st_title = self.workflow.getTitleForStateOnType(rs, obj.portal_type)
                st_title = t(PMF(st_title))

            if rs:
                results_dict['review_state'] = rs

            for state_var, state in states.items():
                if not st_title:
                    st_title = self.workflow.getTitleForStateOnType(
                        state, obj.portal_type)
                results_dict[state_var] = state
            results_dict['state_title'] = st_title

            results_dict['class'] = {}

            # As far as I am concerned, adapters for IFieldIcons are only used
            # for Analysis content types. Since AnalysesView is not using this
            # "classic" folderitems from bikalisting anymore, this logic has
            # been added in AnalysesView. Even though, this logic hasn't been
            # removed from here, cause this _folderitems function is marked as
            # deprecated, so it will be eventually removed alltogether.
            for name, adapter in getAdapters((obj,), IFieldIcons):
                auid = obj.UID() if hasattr(obj, 'UID') and callable(
                    obj.UID) else None
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
                # if the key is already in the results dict
                # then we don't replace it's value
                value = results_dict.get(key, '')
                if key not in results_dict:
                    attrobj = getFromString(obj, key)
                    value = attrobj if attrobj else value

                    # Custom attribute? Inspect to set the value
                    # for the current column dinamically
                    vattr = self.columns[key].get('attr', None)
                    if vattr:
                        attrobj = getFromString(obj, vattr)
                        value = attrobj if attrobj else value
                    results_dict[key] = value

                # Replace with an url?
                replace_url = self.columns[key].get('replace_url', None)
                if replace_url:
                    attrobj = getFromString(obj, replace_url)
                    if attrobj:
                        results_dict['replace'][key] = \
                            '<a href="%s">%s</a>' % (attrobj, value)

            # The item basics filled. Delegate additional actions to folderitem
            # service. folderitem service is frequently overriden by child
            # objects
            item = self.folderitem(obj, results_dict, idx)
            if item:
                results.append(item)
                idx += 1

        return results

    def contents_table(self, table_only=None):
        """If you set table_only to true, then nothing outside of the
           <table/> tag will be printed (form tags, authenticator, etc).
           Then you can insert your own form tags around it.
        """
        table = BikaListingTable(bika_listing=self, table_only=table_only)
        return table.render(self)

    def rendered_items(self):
        """If you set table_only to true, then nothing outside of the
           <table/> tag will be printed (form tags, authenticator, etc).
           Then you can insert your own form tags around it.
        """
        # Category which we are going to query:
        self.cat = self.request.get('ajax_category_expand')
        self.contentFilter[self.category_index] = self.request.get('cat')

        # Filter items by state. First remove them from contentFilter
        # and then, look for its value from the request
        clear_states = ['inactive_state', 'review_state', 'cancellation_state']
        for clear_state in clear_states:
            if clear_state in self.contentFilter:
                del self.contentFilter[clear_state]
        req_revstate = self.request.get('review_state', None)
        if req_revstate:
            for revstate in self.review_states:
                if revstate.get('id', None) != req_revstate:
                    continue
                rev_cfilter = revstate.get('contentFilter', {})
                if not rev_cfilter:
                    continue
                for key, value in rev_cfilter.items():
                    self.contentFilter[key] = value
                break

        # These are required to allow the template to work with this class as
        # the view.  Normally these are attributes of class BikaListingTable.
        self.bika_listing = self
        self.this_cat_selected = True
        self.this_cat_batch = self.folderitems()

        data = self.render_items(self.context)
        return data

    def get_transitions_for_items(self, items):
        """Extract Worfklow transitions for the bika listing items
        """
        out = {}

        # extract all objects from the items
        for obj in map(get_object, [item.get('obj') for item in items]):
            for transition in get_transitions_for(obj):
                # append the transition by its id to the transitions dictionary
                out[transition['id']] = transition
        return out

    def get_workflow_actions(self):
        """Compile a list of possible workflow transitions for items
           in this Table.
        """

        # cbb return empty list if we are unable to select items
        if not self.show_select_column:
            return []

        # get all transitions for all items.
        transitions = self.get_transitions_for_items(self.items)

        # The actions which will be displayed in the listing view
        actions = []

        # the list is restricted to and ordered by these transitions.
        if 'transitions' in self.review_state:
            for transition in self.review_state['transitions']:
                # noinspection PyTypeChecker
                if transition['id'] in transitions:
                    # noinspection PyTypeChecker
                    actions.append(transitions[transition['id']])
        else:
            actions = transitions.values()

        new_actions = []
        # remove any invalid items with a warning
        for action in actions:
            if isinstance(action, dict) and 'id' in action:
                new_actions.append(action)
            else:
                logger.warning("Bad custom_action: {}".format(actions))
        actions = new_actions

        # and these are removed
        if 'hide_transitions' in self.review_state:
            actions = [a for a in actions
                       if a['id'] not in self.review_state['hide_transitions']]

        # cheat: until workflow_action is abolished, all URLs defined in
        # GS workflow setup will be ignored, and the default will apply.
        # (that means, WorkflowAction-bound URL is called).
        for action in actions:
            action['url'] = ''

        # if there is a self.review_state['some_state']['custom_actions']
        # attribute on the BikaListingView, add these actions to the list.
        if 'custom_actions' in self.review_state:
            for action in self.review_state['custom_actions']:
                if isinstance(action, dict) and 'id' in action:
                    actions.append(action)

        # # translate the workflow action title for the template
        # for action in actions:
        #     action['title'] = t(_(action['title']))

        return actions

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def getFilterBar(self):
        """ This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.

        :return: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            BikaListingFilterBar(context=self.context, request=self.request)
        return self._advfilterbar

    def save_filter_bar_values(self, filter_bar_items=None):
        """This function saves the values to filter the bika_listing inside the
        BikaListingFilterBar object.

        :filter_bar_items: an array of tuples with the items to define the
        query. The array has the following format: [(key, value), (), ...]
        """
        self.getFilterBar().save_filter_bar_values(filter_bar_items)

    def get_filter_bar_queryaddition(self):
        """This function calls the filter bar get_filter_bar_queryaddition
        from self._advfilterbar in order to obtain the obtain the extra filter
        conditions.
        """
        if self.getFilterBar():
            return self.getFilterBar().get_filter_bar_queryaddition()
        else:
            return {}

    def get_filter_bar_values(self):
        """This function calls the filter bar get_filter_bar_dict
        from the filterbar object in order to obtain the filter values.

        :return: a dictionary
        """
        return self.getFilterBar().get_filter_bar_dict()

    def filter_bar_check_item(self, item):
        """This functions receives a key-value items, and checks if it should
        be displayed.

        It is recomended to be used in isItemAllowed() method.
        This function should be only used for those fields without
        representation as an index in the catalog.

        :item: The item to check.
        :return: boolean
        """
        if self.getFilterBar():
            return self.getFilterBar().filter_bar_check_item(item)
        else:
            return True


class BikaListingTable(tableview.Table):
    render = ViewPageTemplateFile("templates/bika_listing_table.pt")
    render_items = ViewPageTemplateFile("templates/bika_listing_table_items.pt")

    def __init__(self, bika_listing=None, table_only=None):
        self.table = self
        self.table_only = table_only
        self.bika_listing = bika_listing
        self.pagesize = bika_listing.pagesize
        folderitems = bika_listing.folderitems()
        if self.pagesize == 0:
            self.pagesize = len(folderitems)
        bika_listing.items = folderitems
        self.hide_hidden_attributes()

        tableview.Table.__init__(self,
                                 bika_listing.request,
                                 bika_listing.base_url,
                                 bika_listing.view_url,
                                 folderitems,
                                 pagesize=self.pagesize)

        self.context = bika_listing.context
        self.request = bika_listing.request
        self.form_id = bika_listing.form_id
        self.items = folderitems

    def rendered_items(self, cat=None, **kwargs):
        """Render the table rows of items in a particular category.

        :param cat: the category ID with which we will filter the results
        :param kwargs: all other keyword args are set as attributes of
                       self and self.bika_listing, for injecting attributes
                       that templates require.
        :return: rendered HTML text
        """
        self.cat = cat
        for key, val in kwargs.items():
            self.__setattr__(key, val)
            self.bika_listing.__setattr__(key, val)
        selected_cats = self.bika_listing.selected_cats(self.batch)
        self.this_cat_selected = cat in selected_cats
        self.this_cat_batch = []
        for item in self.batch:
            if item.get('category', 'None') == cat:
                self.this_cat_batch.append(item)
        return self.render_items(self.context)

    def hide_hidden_attributes(self):
        """Use the bika_listing's contentFilter's portal_type values, if any,
        to remove fields from review_states if they are marked as hidden in the
        registry.
        """
        if 'portal_type' not in self.bika_listing.contentFilter:
            return
        ptlist = self.bika_listing.contentFilter['portal_type']
        if not isinstance(ptlist, (list, tuple)):
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

    def get_top_right_hooks(self):
        """Get adapters (hooks) that implements ITopRightListingHook. The
        information got from those adapters will be placed right-over the list.

        :return: html code
        """
        return self.get_adapters_html(ITopRightHTMLComponentsHook)

    def get_top_left_hooks(self):
        """Get adapters (hooks) that implements ITopLeftListingHook. The
        information got from those adapters will be placed left-over the list.

        :return: html code
        """
        return self.get_adapters_html(ITopLeftHTMLComponentsHook)

    def get_top_wide_hooks(self):
        """Get adapters (hooks) that implements ITopWideListingHook. The
        information got from those adapters will be placed wide-over the list.

        :return: html code
        """
        return self.get_adapters_html(ITopWideHTMLComponentsHook)

    def get_adapters_html(self, adapter_provider=None):
        if not adapter_provider:
            return ''
        adapters = getAdapters((self, ), adapter_provider)
        export_options = ''
        for name, adapter in adapters:
            export_options += adapter(self.request)
        return export_options

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i


class BikaListingFilterBar(BrowserView):
    """This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    template = ViewPageTemplateFile("templates/bika_listing_filter_bar.pt")
    _filter_bar_dict = {}

    def render(self):
        """Returns a ViewPageTemplateFile instance with the filter inputs and
        submit button.
        """
        return self.template()

    def setRender(self, new_template):
        """Defines a new template to render.

        :new_template: should be a ViewPageTemplateFile object such as
                       'ViewPageTemplateFile("templates/bika_listing_filter_bar.pt")'
        """
        if new_template:
            self.template = new_template

    def save_filter_bar_values(self, filter_bar_items=None):
        """This function saves the values to filter the bika_listing inside the
        BikaListingFilterBar object.

        The dictionary is saved inside a class attribute.
        This function tranforms the unicodes to strings and removes the
        'bika_listing_filter_bar_' starting string of each key.

        :filter_bar_items: a dictionary with the items to define the
        query.
        """
        if filter_bar_items:
            new_dict = {}
            for k in filter_bar_items.keys():
                value = str(filter_bar_items[k])
                key = str(k).replace("bika_listing_filter_bar_", "")
                new_dict[key] = value
            self._filter_bar_dict = new_dict

    def get_filter_bar_dict(self):
        """Returns the _filter_bar_dict attribute
        """
        return self._filter_bar_dict

    def get_filter_bar_queryaddition(self):
        """This function gets the values from the filter bar inputs in order to
        create a catalog query accordingly.

        Only returns the items that can be added to contentFilter dictionary,
        this means that only the dictionary items (key-value) with index
        representations should be returned.

        :return: a dictionary to be added to contentFilter.
        """
        return {}

    # noinspection PyUnusedLocal
    def filter_bar_check_item(self, item):
        """This functions receives a key-value items, and checks if it should
        be displayed.

        It is recomended to be used in isItemAllowed() method. This function
        should be only used for those fields without representation as an index
        in the catalog.

        :item: The item to check.
        :return: boolean.
        """
        return True

    def filter_bar_builder(self):
        """The template is going to call this method to create the filter bar
        in bika_listing_filter_bar.pt If the method returns None, the filter
        bar will not be shown.

        :return: a list of dictionaries as the filtering fields or None.

        Each dictionary defines a field, those are the expected elements
        for each field type by the default template:
        - select/multiple:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'select/multiple',
                'voc': <a DisplayList object containing the options>,
            }
        - simple text input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'text',
            }
        - autocomplete text input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'autocomplete_text',
                'voc': <a List object containing the options in JSON>,
            }
        - value range input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'range',
            },
        - date range input:
            {
                'name': 'field_name',
                'label': _('Field name'),
                'type': 'date_range',
            },
        """
        return None
