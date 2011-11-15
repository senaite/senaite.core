""" Display lists of items in tables.
"""
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import isActive, TimeOrDate
from plone.app.content.batching import Batch
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.app.component.hooks import getSite
from zope.component._api import getMultiAdapter
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
import App
import json
import plone
import transaction
import urllib

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
            if type(action) in(list,tuple): action = action[0]
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return None, None
        # convert button text to action id
        if came_from == "workflow_action_button":
            action = form[action]
        if type(action) in(list,tuple): action = action[0]
        return (action, came_from)

    def _get_selected_items(self, full_objects = True):
        """ return a list of selected form objects
            full_objects defaults to True
        """
        form = self.request.form
        pc = getToolByName(self.context, 'portal_catalog')
        selected_items = {}
        if 'paths' in form:
            for path in form['paths']:
                item_id = path.split("/")[-1]
                item_path = path.replace("/" + item_id, '')
                try:
                    item = pc(id = item_id,
                              path = {'query':item_path,
                                  'depth':1})[0].getObject()
                except:
                # ignore selected item if object no longer exists
                    continue
                uid = item.UID()
                selected_items[uid] = item
            return selected_items
        return {}

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
                message = _('Item is inactive.')
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.destination_url)
                return
            else:
                if obj.UID() not in skiplist:
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
                try:
                    workflow.doActionFor(item, action)
                    transitioned.append(item.Title())
                except WorkflowException:
                    pass

        if len(transitioned) > 0:
            message = _('Changes saved.')
            self.context.plone_utils.addPortalMessage(message, 'info')

        # automatic label printing
        if action == 'receive' and 'receive' in self.context.bika_setup.getAutoPrintLabels():
            q = "/sticker?size=%s&items="%(self.context.bika_setup.getAutoLabelSize())
            # selected_items is a list of UIDs (stickers for AR_add use IDs)
            q += ",".join([i.getId() for i in selected_items.values()])
            self.request.response.redirect(self.context.absolute_url()+q)
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
    content_add_actions = {}
    show_select_column = False
    show_select_row = False
    show_select_all_checkbox = True
    show_sort_column = False
    show_workflow_action_buttons = True
    categories = []
    # just set pagesize high to disable batching.
    pagesize = 20

    """
     The keys of the columns dictionary must all exist in all
     items returned by subclassing view's .foldercontents.
     possible column dictionary keys are:
     - allow_edit
       if View.allow_edit is also True, this field is made editable
       Interim fields are always editable
     - type
       possible values: "string", "boolean", "choices".
       if "choices" is selected, item['choices'][column_id] must
       be a list of choice strings.
    """
    columns = {
           'obj_type': {'title': _('Type')},
           'id': {'title': _('ID')},
           'title_or_id': {'title': _('Title')},
           'modified': {'title': _('Last modified')},
           'state_title': {'title': _('State')},
    }

    # with just one review_state, the selector won't show.
    review_states = [
        {'id':'all',
         'title': _('All'),
         'columns':['state_title', ]
         },
    ]

    def __init__(self, context, request):
        super(BikaListingView, self).__init__(context, request)
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        # contentsMethod may return a list of brains or a list of objects.
        self.contentsMethod = self.context.getFolderContents

    def __call__(self):
        """ bika_listing view initial display and form handler
        """

        form = self.request.form
        pc = getToolByName(self.context, 'portal_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')

        for c in self.columns.keys():
            if c in self.request:
                self.contentFilter[c]=urllib.unquote(self.request[c])

        if form.has_key('review_state'):
            self.modified_contentFilter = self.contentFilter
            if form.has_key("review_state"):
                review_state = [r for r in self.review_states if \
                                r['id'] == form['review_state']][0]
                if review_state.has_key('contentFilter'):
                    for k, v in review_state['contentFilter'].items():
                        self.modified_contentFilter[k] = v
                else:
                    if form['review_state'] != 'all':
                        self.modified_contentFilter['review_state'] = form['review_state']

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

        show_all = self.request.get('show_all', '').lower() == 'true'
        pagenumber = int(self.request.get('pagenumber', 1) or 1)
        pagesize = self.pagesize
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        if not hasattr(self, 'modified_contentFilter'):
            self.modified_contentFilter = self.contentFilter

        results = []
        for i, obj in enumerate(self.contentsMethod(self.modified_contentFilter)):
            # we don't know yet if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                 "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not show_all and not start <= i < end:
                results.append(dict(path = path))
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

            # Check for InterimFields attribute on our object,
            # XXX move interim/itemdata to analyses.py
            interim_fields = hasattr(obj, 'getInterimFields') \
                           and obj.getInterimFields() or []

            # element css classes
            type_class = 'contenttype-' + \
                plone_utils.normalizeString(obj.portal_type)

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

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
                interim_fields = interim_fields,
                item_data = json.dumps(interim_fields),
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
                table_row_class = table_row_class,

                # a list of names of fields that may be edited on this item
                allow_edit = [],
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

            # XXX debug - add history_id column
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
            results.append(results_dict)

        return results

    def contents_table(self):
        table = BikaListingTable(self)
        return table.render(self)

class BikaListingTable(tableview.Table):

    render = ViewPageTemplateFile("templates/bika_listing_table.pt")
    batching = ViewPageTemplateFile("templates/bika_listing_batching.pt")

    def __init__(self, bika_listing):
        self.table = self
        self.bika_listing = bika_listing
        folderitems = bika_listing.folderitems()

        tableview.Table.__init__(self,
                                 bika_listing.request,
                                 bika_listing.base_url,
                                 bika_listing.view_url,
                                 folderitems,
                                 show_select_column = bika_listing.show_select_column,
                                 show_sort_column = bika_listing.show_sort_column,
                                 pagesize = bika_listing.pagesize)

        self.context = bika_listing.context
        self.request = bika_listing.request
        self.columns = bika_listing.columns
        self.allow_edit = bika_listing.allow_edit
        self.items = folderitems
        self.show_sort_column = bika_listing.show_sort_column
        self.show_select_row = bika_listing.show_select_row
        self.show_select_column = bika_listing.show_select_column
        self.show_select_all_checkbox = bika_listing.show_select_all_checkbox
        self.show_workflow_action_buttons = bika_listing.show_workflow_action_buttons
        self.review_states = bika_listing.review_states

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
        review_state = [i for i in self.review_states if i['id'] == state][0]

        # get all transitions for all items.
        transitions = {}
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
            ordered = []
            for tid in review_state['transitions']:
                if tid in transitions:
                    ordered.append(transitions[tid])
            transitions = ordered
        else:
            transitions = transitions.values()

        return transitions
