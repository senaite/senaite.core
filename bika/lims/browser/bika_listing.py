# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" Display lists of items in tables.
"""
import json
import re
import urllib
import copy
from operator import itemgetter

import App
import pkg_resources
import plone
import transaction
from AccessControl import getSecurityManager
from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from Products.AdvancedQuery import And, Or, MatchRegexp, Between, Generic, Eq
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IFieldIcons
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import isActive, getHiddenAttributesForClass
from bika.lims.utils import t, format_supsub
from bika.lims.utils import to_utf8
from bika.lims.utils import getFromString
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getAdapters
from zope.component import getUtility
from zope.component._api import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import implements
from bika.lims.browser.bika_listing_filter_bar import BikaListingFilterBar
import types

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
        if not action:
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return None, None
        # A condition in the form causes Plone to sometimes send two actions
        if type(action) in (list, tuple):
            action = action[0]
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
        if form.get('bika_listing_filter_bar_submit', ''):
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
                    success = False
                    # if action is "verify" and the item is an analysis or
                    # reference analysis, check if the if the required number
                    # of verifications done for the analysis is, at least,
                    # the number of verifications performed previously+1
                    if (action == 'verify' and
                        hasattr(item, 'getNumberOfVerifications') and
                        hasattr(item, 'getNumberOfRequiredVerifications')):
                        success = True
                        revers = item.getNumberOfRequiredVerifications()
                        nmvers = item.getNumberOfVerifications()
                        username=getToolByName(self.context,'portal_membership').getAuthenticatedMember().getUserName()
                        item.addVerificator(username)
                        if revers-nmvers <= 1:
                            success, message = doActionFor(item, action)
                            if not success:
                                # If failed, delete last verificator.
                                item.deleteLastVerificator()
                    else:
                        success, message = doActionFor(item, action)
                    if success:
                        transitioned.append(item.id)
                    else:
                        self.context.plone_utils.addPortalMessage(message, 'error')
        # automatic label printing
        if transitioned and action == 'receive' \
            and 'receive' in self.portal.bika_setup.getAutoPrintStickers():
            q = "/sticker?template=%s&items=" % (self.portal.bika_setup.getAutoStickerTemplate())
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
    #               autosave: when js detects this variable as 'true',
    #               the system will save the value after been
    #               introduced via ajax.
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
    # The advanced filter bar instance, it is initialized using
    # getAdvancedFilterBar
    _advfilterbar = None
    # The following variable will contain an instance that checks whether the
    # logged in user has a certain permission for some object.
    # Save getSecurityManager() in this variable and then use
    # security_manager.checkPermission(ModifyPortalContent, obj)
    security_manager = None

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
        self.show_more = False
        self.limit_from = 0
        self.mtool = None
        self.member = None
        # The listing object is bound to a class called BikaListingFilterBar
        # which can display an additional filter bar in the listing view in
        # order to filter the items by some terms. These terms should be
        # difined in the BikaListingFilterBar class following the descripton
        # and examples. This variable is overriden in other views, in order to
        # show the bar or not depending on the list. For example, Analysis
        # Requests view checks bika_setup.getSamplingBarEnabledAnalysisRequests
        # to know if the functionality is activeated or not for its views.
        self.filter_bar_enabled = False

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
        """
        This function returns a string as the value for the action attribute of
        the form element in the template.
        This method is used in bika_listing_table.pt
        """
        return 'workflow_action'

    def _process_request(self):
        """Scan request for parameters and configure class attributes
        accordingly.  Setup AdvancedQuery or catalog contentFilter.

        Request parameters:
        <form_id>_limit_from:       index of the first item to display
        <form_id>_rows_only:        returns only the rows
        <form_id>_sort_on:          list items are sorted on this key
        <form_id>_manual_sort_on:   no index - sort with python
        <form_id>_pagesize:         number of items
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
        if form_id not in self.request.get('table_only', form_id) \
            or form_id not in self.request.get('rows_only', form_id):
            return ''

        self.rows_only = self.request.get('rows_only','') == form_id
        self.limit_from = int(self.request.get(form_id + '_limit_from',0))

        # contentFilter is allowed in every self.review_state.
        for k, v in self.review_state.get('contentFilter', {}).items():
            self.contentFilter[k] = v

        # sort on
        self.sort_on = self.sort_on \
            if hasattr(self, 'sort_on') and self.sort_on \
            else None
        self.sort_on = self.request.get(form_id + '_sort_on', self.sort_on)
        self.sort_order = self.sort_order \
            if hasattr(self, 'sort_order') and self.sort_order \
            else 'ascending'
        self.sort_order = self.request.get(form_id + '_sort_order', self.sort_order)
        self.manual_sort_on = self.request.get(form_id + '_manual_sort_on', None)

        if self.sort_on:
            if self.sort_on in self.columns.keys():
               if self.columns[self.sort_on].get('index', None):
                   self.request.set(form_id+'_sort_on', self.sort_on)
                   # The column can be sorted directly using an index
                   idx = self.columns[self.sort_on]['index']
                   self.sort_on = idx
                   # Don't sort manually!
                   self.manual_sort_on = None
               else:
                   # The column must be manually sorted using python
                   self.manual_sort_on = self.sort_on
            else:
                # We cannot sort for a column that doesn't exist!
                msg = "{}: sort_on is '{}', not a valid column".format(
                    self, self.sort_on)
                logger.warn(msg)
                self.sort_on = None

        if self.manual_sort_on:
            self.manual_sort_on = self.manual_sort_on[0] \
                                if type(self.manual_sort_on) in (list, tuple) \
                                else self.manual_sort_on
            if self.manual_sort_on not in self.columns.keys():
                # We cannot sort for a column that doesn't exist!
                msg = "{}: manual_sort_on is '{}', not a valid column".format(
                    self, self.manual_sort_on)
                logger.error(msg)
                self.manual_sort_on = None

        if self.sort_on or self.manual_sort_on:
            # By default, if sort_on is set, sort the items ASC
            # Trick to allow 'descending' keyword instead of 'reverse'
            self.sort_order = 'reverse' if self.sort_order \
                                        and self.sort_order[0] in ['d','r'] \
                                        else 'ascending'
        else:
            # By default, sort on created
            self.sort_order = 'reverse'
            self.sort_on = 'created'

        self.contentFilter['sort_order'] = self.sort_order
        if self.sort_on:
            self.contentFilter['sort_on'] = self.sort_on

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
        for x in "pagesize", "review_state", "sort_order", "sort_on", "limit_from":
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
        # Getting the bika_listing_filter_bar cookie
        cookie_filter_bar = self.request.get('bika_listing_filter_bar', '')
        self.request.response.setCookie(
            'bika_listing_filter_bar', None,  path='/', max_age=0)
        # Saving the filter bar values
        cookie_filter_bar = json.loads(cookie_filter_bar) if\
            cookie_filter_bar else ''
        # Creating a dict from cookie data
        cookie_data = {}
        for k, v in cookie_filter_bar:
            cookie_data[k] = v
        self.save_filter_bar_values(cookie_data)
        self._process_request()
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.member = self.mtool.getAuthenticatedMember()

        # ajax_category_expand is included in the form if this form submission
        # is an asynchronous one triggered by a category being expanded.
        if self.request.get('ajax_category_expand', False):
            # - get nice formatted category contents (tr rows only)
            return self.rendered_items()

        if self.request.get('table_only', '') == self.form_id \
            or self.request.get('rows_only', '') == self.form_id:
            return self.contents_table(table_only=self.form_id)
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

    def folderitem(self, obj, item, index):
        """ Service triggered each time an item is iterated in folderitems.
            The use of this service prevents the extra-loops in child objects.
            :obj: the instance of the class to be foldered
            :item: dict containing the properties of the object to be used by
                the template
            :index: current index of the item
        """
        return item

    def folderitems(self, full_objects=False, classic=True):
        """
        This function returns an array of dictionaries where each dictionary
        contains the columns data to render the list.

        No object is needed by default. We should be able to get all
        the listing columns taking advantage of the catalog's metadata,
        so that the listing will be much more faster. If a very specific
        info has to be retrive from the objects, we can define
        full_objects as True but performance can be lowered.

        :full_objects: a boolean, if True, each dictionary will contain an item
        with the cobject itself. item.get('obj') will return a object.
        Only works with the 'classic' way.
        WARNING: :full_objects: could create a big performance hit!
        :classic: if True, the old way folderitems works will be executed. This
        function is mainly used to mantain the integrity with the old version.
        """
        # Getting a security manager instance for the current reques
        self.security_manager = getSecurityManager()
        # If the classic is True,, use the old way.
        if classic:
            return self._folderitems(full_objects)

        if not hasattr(self, 'contentsMethod'):
            self.contentsMethod = getToolByName(self.context, self.catalog)
        # Setting up some attributes
        context = aq_inner(self.context)
        workflow = getToolByName(context, 'portal_workflow')

        # Creating a copy of the contentFilter dictionary in order to include
        # the filter bar's filtering additions in the query. We don't want to
        # modify contentFilter with those 'extra' filtering elements to be
        # inculded in the.
        contentFilterTemp = copy.deepcopy(self.contentFilter)
        addition = self.get_filter_bar_queryaddition()
        # Adding the extra filtering elements
        if addition:
            contentFilterTemp.update(addition)
        # Check for 'and'/'or' logic queries
        if (hasattr(self, 'And') and self.And) \
           or (hasattr(self, 'Or') and self.Or):
            # if contentsMethod is capable, we do an AdvancedQuery.
            if hasattr(self.contentsMethod, 'makeAdvancedQuery'):
                aq = self.contentsMethod.makeAdvancedQuery(contentFilterTemp)
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
                brains = self.contentsMethod(contentFilterTemp)
        else:
            brains = self.contentsMethod(contentFilterTemp)

        # idx increases one unit each time an object is added to the 'items'
        # dictionary to be returned. Note that if the item is not rendered,
        # the idx will not increase.
        idx = 0
        results = []
        self.show_more = False
        brains = brains[self.limit_from:]
        for i, obj in enumerate(brains):
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
            modified = self.ulocalized_time(obj.modified()),
            state_class = ''
            states = obj.getObjectWorkflowStates
            for w_id in states.keys():
                state_class += "state-%s " % states.get(w_id, '')
            # Building the dictionary with basic items
            results_dict = dict(
                # obj can be an object or a brain!!
                obj=obj,
                uid=obj.UID,
                url=obj.getURL(),
                id=obj.id,
                title=obj.Title,
                # To colour the list items by state
                state_class=state_class,
                review_state=obj.review_state,
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
            # Getting the state title, if the review_state doesn't have a title
            # use the title of the first workflow found for the object
            try:
                rs = obj.review_state
                st_title = workflow.getTitleForStateOnType(rs, obj.portal_type)
                st_title = t(PMF(st_title))
            except:
                logger.warning(
                    "Workflow title doesn't obtined for object %s" % obj.id)
                rs = 'active'
                st_title = None
            for state_var, state in states.items():
                if not st_title:
                    st_title = workflow.getTitleForStateOnType(
                        state, obj.portal_type)
                results_dict[state_var] = state
            results_dict['state_title'] = st_title
            # extra classes for individual fields on this item
            # { field_id : "css classes" }
            results_dict['class'] = {}
            # TODO: This trace of code should be implemented in analysis only
            # obj_f=obj.getObject()
            # for name, adapter in getAdapters((obj_f, ), IFieldIcons):
            #     auid = obj.UID
            #     if not auid:
            #         continue
            #     alerts = adapter()
            #     if alerts and auid in alerts:
            #         if auid in self.field_icons:
            #             self.field_icons[auid].extend(alerts[auid])
            #         else:
            #             self.field_icons[auid] = alerts[auid]
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

    def _folderitems(self, full_objects=False):
        """
        WARNING: :full_objects: could create a big performance hit.
        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        Test page batching https://github.com/bikalabs/Bika-LIMS/issues/1276
        When visiting the second page, the Water sampletype should be displayed:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/bika_setup/bika_sampletypes/folder_view?",
        ... "list_pagesize=10&list_review_state=default")
        >>> browser.contents
        '...Water...'
        """

        #self.contentsMethod = self.context.getFolderContents
        if not hasattr(self, 'contentsMethod'):
            self.contentsMethod = getToolByName(self.context, self.catalog)
        # Setting up some attributes
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
        # Creating a copy of the contentFilter dictionary in order to include
        # the filter bar's filtering additions in the query. We don't want to
        # modify contentFilter with those 'extra' filtering elements to be
        # inculded in the.
        contentFilterTemp = copy.deepcopy(self.contentFilter)
        addition = self.get_filter_bar_queryaddition()
        # Adding the extra filtering elements
        if addition:
            contentFilterTemp.update(addition)
        # Check for 'and'/'or' logic queries
        if (hasattr(self, 'And') and self.And) \
           or (hasattr(self, 'Or') and self.Or):
            # if contentsMethod is capable, we do an AdvancedQuery.
            if hasattr(self.contentsMethod, 'makeAdvancedQuery'):
                aq = self.contentsMethod.makeAdvancedQuery(contentFilterTemp)
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
                brains = self.contentsMethod(contentFilterTemp)
        else:
            brains = self.contentsMethod(contentFilterTemp)

        # idx increases one unit each time an object is added to the 'items'
        # dictionary to be returned. Note that if the item is not rendered,
        # the idx will not increase.
        idx = 0
        results = []
        self.show_more = False
        brains = brains[self.limit_from:]
        for i, obj in enumerate(brains):
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
            # service. folderitem service is frequently overriden by child objects
            item = self.folderitem(obj, results_dict, idx)
            if item:
                results.append(item)
                idx+=1

        # Need manual_sort?
        # Note that the order has already been set in contentFilter, so
        # there is no need to reverse
        if self.manual_sort_on:
            results.sort(lambda x,y:cmp(x.get(self.manual_sort_on, ''),
                                     y.get(self.manual_sort_on, '')))

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
        actions = new_actions
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

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :return: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            BikaListingFilterBar(context=self.context, request=self.request)
        return self._advfilterbar

    def save_filter_bar_values(self, filter_bar_items={}):
        """
        This function saves the values to filter the bika_listing inside the
        BikaListingFilterBar object.
        :filter_bar_items: an array of tuples with the items to define the
        query. The array has the following format: [(key, value), (), ...]
        """
        self.getFilterBar().save_filter_bar_values(filter_bar_items)

    def get_filter_bar_queryaddition(self):
        """
        This function calls the filter bar get_filter_bar_queryaddition
        from self._advfilterbar in order to obtain the obtain the extra filter
        conditions.
        """
        if self.getFilterBar():
            return self.getFilterBar().get_filter_bar_queryaddition()
        else:
            return {}

    def get_filter_bar_values(self):
        """
        This function calls the filter bar get_filter_bar_dict
        from the filterbar object in order to obtain the filter values.
        :return: a dictionary
        """
        return self.getFilterBar().get_filter_bar_dict()

    def filter_bar_check_item(self, item):
        """
        This functions receives a key-value items, and checks if it should be
        displayed.
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
