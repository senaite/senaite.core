# -*- coding: utf-8 -*-

import collections
import copy
import json
import re
import time

import DateTime
import Missing
from AccessControl import getSecurityManager
from ajax import AjaxListingView
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.interfaces import IFieldIcons
from bika.lims.utils import getFromString
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters
from zope.component import getMultiAdapter


class ListingView(AjaxListingView):
    """Base Listing View
    """
    template = ViewPageTemplateFile("templates/listing.pt")

    # The title of the outer listing view
    # see: templates/listing.pt
    title = ""

    # The description of the outer listing view
    # see: templates/listing.pt
    description = ""

    # TODO: Refactor to viewlet
    # Context actions rendered next to the title
    # see: templates/listing.pt
    context_actions = {}

    # Default search catalog to be used for the content filter query
    catalog = "portal_catalog"

    # Catalog query used for the listing. It can be extended by the
    # review_state filter
    contentFilter = {}

    # A mapping of column_key -> colum configuration
    columns = collections.OrderedDict((
        ("Title", {
            "title": _("Title"),
            "index": "sortable_title"}),
        ("Description", {
            "title": _("Description"),
            "index": "Description"}),
    ))

    # A list of dictionaries, specifying parameters for listing filter buttons.
    #
    # - If review_state[x]["transitions"] is defined, e.g.:
    #     "transitions": [{"id": "x"}]
    # The possible transitions will be restricted by those defined
    #
    # - If review_state[x]["custom_transitions"] is defined, e.g.:
    #     "custom_transitions": [{"id": "x"}]
    # The possible transitions will be extended by those defined.
    review_states = [
        {
            "id": "default",
            "title": _("All"),
            "contentFilter": {},
            "transitions": [],
            "custom_transitions": [],
            "columns": ["Title", "Descritpion"],
        }
    ]

    # The initial/default review_state
    default_review_state = "default"

    # When rendering multiple listing tables, e.g. AR lab/field/qc tables, the
    # form_id must be unique for each listing table.
    form_id = "list"

    # This is an override and a switch, but it does not guarantee allow_edit.
    # This can be used to turn it off, regardless of settings in place by
    # individual items/fields, but if it is turned on, ultimate control
    # is still given to the individual items/fields.
    allow_edit = True

    # Defines the input name of the select checkbox.
    # This will be probaly removed in later versions, because most of the form
    # handlers expect the selected UIDs inside the "uids" request parameter
    select_checkbox_name = "uids"

    # Display a checkbox to select all visible rows
    show_select_all_checkbox = True

    # Display the left-most column for selecting all/individual items.
    # Also see the "fetch_transitions_on_select" option.
    show_select_column = False

    # Automatically fetch all possible transitions for selected items.
    fetch_transitions_on_select = True

    # Allow to show/hide columns by right-clicking on the column header.
    show_column_toggles = True

    # Render items in expandable categories
    show_categories = False

    # These are the possible categories. If self.show_categories is True, only
    # these categories which will be rendered.
    categories = []

    # Expand all categories on load. If set to False, only categories
    # containing selected items are expanded.
    expand_all_categories = False

    # Number of rows initially displayed. If more items are returned from the
    # database, a paging control is displayed in the lower right corner
    pagesize = 50

    # Override pagesize and show all items on one page
    # XXX: Currently only used in classic folderitems method.
    #      -> Consider if it is worth to keep that funcitonality
    show_all = False

    # Manually sort catalog results on this column
    # XXX: Currently the listing table sorts only if the catalog index exists.
    #      -> Consider if it is worth to keep that functionality
    manual_sort_on = None

    # Render the search box in the upper right corner
    show_search = True

    # Omit the outer form wrapper of the contents table, e.g. when the listing
    # is used as an embedded widget in an edit form.
    omit_form = False

    # Toggle transition button rendering of the table footer
    show_workflow_action_buttons = True

    # Toggle the whole table footer rendering. This includes the pagination and
    # transition buttons.
    show_table_footer = True

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        self.context = context
        self.request = request

        # N.B. We set that here so that it can be overridden by subclasses,
        #      e.g. by the worksheet add view
        if "path" not in self.contentFilter:
            self.contentFilter.update(self.get_path_query())

        self.total = 0
        self.limit_from = 0
        self.show_more = False
        self.sort_on = "sortable_title"
        self.sort_order = "ascending"

        # Internal cache for translated state titles
        self.state_titles = {}

        # TODO: Refactor to a view memoized property
        # Internal cache for alert icons
        self.field_icons = {}

    def __call__(self):
        """Handle request parameters and render the form
        """
        logger.info(u"ListingView::__call__")

        self.portal = api.get_portal()
        self.mtool = api.get_tool("portal_membership")
        self.workflow = api.get_tool("portal_workflow")
        self.member = api.get_current_user()
        self.translate = self.context.translate

        # Call update hook
        self.update()

        # handle subpath calls
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()

        # Call before render hook
        self.before_render()

        return self.template(self.context)

    def update(self):
        """Update the view state
        """
        logger.info(u"ListingView::update")
        self.limit_from = self.get_limit_from()
        self.pagesize = self.get_pagesize()

    def before_render(self):
        """Before render hook
        """
        logger.info(u"ListingView::before_render")

    def contents_table(self, *args, **kwargs):
        """Render the ReactJS enabled contents table template
        """
        return self.contents_table_template()

    @view.memoize
    def is_permission_granted_for(self, permission, context=None):
        """Checks if the the given permission is granted

        :param permission: Permission to check
        :param brain_or_object: Object to check the permission
        """
        sm = getSecurityManager()
        if context is None:
            context = self.context
        context = api.get_object(context)
        return sm.checkPermission(permission, context)

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
        if not state_id:
            state_id = self.default_review_state
        states = [r for r in self.review_states if r["id"] == state_id]
        if not states:
            logger.error("%s.review_states does not contain id='%s'." %
                         (self, state_id))
            return None
        review_state = states[0] if states else self.review_states[0]
        # set selected state into the request
        self.request["%s_review_state" % self.form_id] = review_state["id"]
        return review_state

    def remove_column(self, column):
        """Removes the column passed-in, if exists

        :param column: Column key
        :returns: True if the column was removed
        """
        if column not in self.columns:
            return False

        del self.columns[column]
        for item in self.review_states:
            if column in item.get("columns", []):
                item["columns"].remove(column)
        return True

    def getPOSTAction(self):
        """This function returns a string as the value for the action attribute
        of the form element in the template.

        This method is used in bika_listing_table.pt
        """
        return "workflow_action"

    def get_form_id(self):
        """Return the form id

        Note: The form_id must be unique when rendering multiple listing tables
        """
        return self.form_id

    def get_catalog(self, default="portal_catalog"):
        """Get the catalog tool to be used in the listing

        :returns: ZCatalog tool
        """
        try:
            return api.get_tool(self.catalog)
        except api.BikaLIMSError:
            return api.get_tool(default)

    @view.memoize
    def get_catalog_indexes(self):
        """Return a list of registered catalog indexes
        """
        return self.get_catalog().indexes()

    @view.memoize
    def get_columns_indexes(self):
        """Returns a list of allowed sorting indexeds
        """
        columns = self.columns
        indexes = [v["index"] for k, v in columns.items() if "index" in v]
        return indexes

    @view.memoize
    def get_metadata_columns(self):
        """Get a list of all metadata column names

        :returns: List of catalog metadata column names
        """
        catalog = self.get_catalog()
        return catalog.schema()

    @view.memoize
    def translate_review_state(self, state, portal_type):
        """Translates the review state to the current set language

        :param state: Review state title
        :type state: basestring
        :returns: Translated review state title
        """
        ts = api.get_tool("translation_service")
        wf = api.get_tool("portal_workflow")
        state_title = wf.getTitleForStateOnType(state, portal_type)
        translated_state = ts.translate(
            _(state_title or state), context=self.request)
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
            return self.translate_review_state(
                value, api.get_portal_type(brain))
        if not isinstance(value, basestring):
            value = str(value)
        return safe_unicode(value)

    def get_sort_order(self):
        """Get the sort_order criteria from the request or view
        """
        form_id = self.get_form_id()
        allowed = ["ascending", "descending"]
        sort_order = [self.request.form.get("{}_sort_order"
                                            .format(form_id), None),
                      self.contentFilter.get("sort_order", None)]
        sort_order = filter(lambda order: order in allowed, sort_order)
        return sort_order and sort_order[0] or "descending"

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
        sort_on = self.request.form.get(key, None)
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
        if not hasattr(sort_index, "documentToKeyMap"):
            return False
        return True

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

    def get_pagesize(self):
        """Return the pagesize request parameter
        """
        form_id = self.get_form_id()
        pagesize = self.request.form.get(form_id + '_pagesize', self.pagesize)
        try:
            return int(pagesize)
        except (ValueError, TypeError):
            return self.pagesize

    def get_limit_from(self):
        """Return the limit_from request parameter
        """
        form_id = self.get_form_id()
        limit = self.request.form.get(form_id + '_limit_from', 0)
        try:
            return int(limit)
        except (ValueError, TypeError):
            return 0

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
            "review_state": api.get_workflow_status_of(brain_or_object),
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

        logger.info(u"ListingView::get_catalog_query: query={}".format(query))
        return query

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
            logger.warn(
                "ListingView::sort_brains: '{}' not in metadata columns."
                .format(sort_on))
            return brains

        logger.warn(
            "ListingView::sort_brains: Manual sorting on metadata column '{}'."
            "Consider to add an explicit catalog index to speed up filtering."
            .format(self.manual_sort_on))

        # calculate the sort_order
        reverse = self.get_sort_order() == "descending"

        def metadata_sort(a, b):
            a = getattr(a, self.manual_sort_on, "")
            b = getattr(b, self.manual_sort_on, "")
            return cmp(safe_unicode(a), safe_unicode(b))

        return sorted(brains, cmp=metadata_sort, reverse=reverse)

    def get_searchterm(self):
        """Get the user entered search value from the request

        :returns: Current search box value from the request
        """
        form_id = self.get_form_id()
        key = "{}_filter".format(form_id)
        # we need to ensure unicode here
        return safe_unicode(self.request.form.get(key, ""))

    def metadata_search(self, catalog, query, searchterm, ignorecase=True):
        """ Retrieves all the brains from given catalog and returns the ones
        with at least one metadata containing the search term
        :param catalog: catalog to search
        :param query:
        :param searchterm:
        :param ignorecase:
        :return: brains matching search result
        """
        # create a catalog query
        logger.info(u"ListingView::search: Prepare metadata query for '{}'"
                    .format(self.catalog))

        brains = catalog(query)

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
        return filter(match, brains)

    def ng3_index_search(self, catalog, query, searchterm):
        """Searches given catalog by query and also looks for a keyword in the
        specific index called "listing_searchable_text"

        #REMEMBER TextIndexNG indexes are the only indexes that wildcards can
        be used in the beginning of the string.
        http://zope.readthedocs.io/en/latest/zope2book/SearchingZCatalog.html#textindexng

        :param catalog: catalog to search
        :param query:
        :param searchterm: a keyword to look for in "listing_searchable_text"
        :return: brains matching the search result
        """
        logger.info(u"ListingView::search: Prepare NG3 index query for '{}'"
                    .format(self.catalog))
        # Remove quotation mark
        searchterm = searchterm.replace('"', '')
        # If the keyword is not encoded in searches, TextIndexNG3 encodes by
        # default encoding which we cannot always trust
        searchterm = searchterm.encode("utf-8")
        query["listing_searchable_text"] = "*" + searchterm + "*"
        return catalog(query)

    def _fetch_brains(self, idxfrom=0):
        """Fetch the catalog results for the current listing table state
        """

        searchterm = self.get_searchterm()
        brains = self.search(searchterm=searchterm)
        self.total = len(brains)

        # Return a subset of results, if necessary
        if idxfrom and len(brains) > idxfrom:
            return brains[idxfrom:self.pagesize + idxfrom]
        return brains[:self.pagesize]

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
        # Strip illegal characters of the searchterm
        searchterm = searchterm.strip(u"*.!$%&/()=-+:'`´^")
        logger.info(u"ListingView::search:searchterm='{}'".format(searchterm))

        # create a catalog query
        logger.info(u"ListingView::search: Prepare catalog query for '{}'"
                    .format(self.catalog))
        query = self.get_catalog_query(searchterm=searchterm)

        # search the catalog
        catalog = api.get_tool(self.catalog)

        # return the unfiltered catalog results if no searchterm
        if not searchterm:
            brains = catalog(query)

        # check if there is ng3 index in the catalog to query by wildcards
        elif "listing_searchable_text" in catalog.indexes():
            # Always expand all categories if we have a searchterm
            self.expand_all_categories = True
            brains = self.ng3_index_search(catalog, query, searchterm)

        else:
            self.expand_all_categories = True
            brains = self.metadata_search(
                catalog, query, searchterm, ignorecase)

        # Sort manually?
        if self.manual_sort_on is not None:
            brains = self.sort_brains(brains, sort_on=self.manual_sort_on)

        end = time.time()
        logger.info(u"ListingView::search: Search for '{}' executed in "
                    u"{:.2f}s ({} matches)"
                    .format(searchterm, end - start, len(brains)))
        return brains

    def isItemAllowed(self, obj):
        """ return if the item can be added to the items list.
        """
        return True

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
            workflow = api.get_tool('portal_workflow')
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

    @deprecated("Using bikalisting.folderitems(classic=True) is very slow")
    def _folderitems(self, full_objects=False):
        """WARNING: :full_objects: could create a big performance hit.
        """
        # Setting up some attributes
        plone_layout = getMultiAdapter((self.context.aq_inner, self.request),
                                       name=u'plone_layout')
        plone_utils = getToolByName(self.context.aq_inner, 'plone_utils')
        portal_types = getToolByName(self.context.aq_inner, 'portal_types')
        if self.request.form.get('show_all', '').lower() == 'true' \
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
                st_title = self.workflow.getTitleForStateOnType(
                    rs, obj.portal_type)
                st_title = t(_(st_title))

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
