""" Display lists of items in tables.
"""
from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
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
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')

        originating_url = self.request.get_header("referer",
                                                  self.context.absolute_url())

        # "workflow_action" is the edit border transition
        # "workflow_action_button" is the bika_listing table buttons
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            came_from = "workflow_action_button"
            action = form.get(came_from, '')
            # XXX some browsers agree better than others about our JS ideas.
            if type(action) == type([]): action = action[0]
            if not action:
                logger.warn("No workflow action provided.")
                return

        # transition the context object.
        if came_from == "workflow_action":
            obj = self.context
            # the only action allowed on inactive items is "activate"
            if not isActive(obj):
                message = _('No items were affected.')
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(originating_url)
                return
            else:
                if hasattr(self.request, 'workflow_skiplist') and \
                   obj.UID() in self.request['workflow_skiplist']:
                    pass
                else:
                    workflow.doActionFor(obj, action)
                self.request.response.redirect(originating_url)
                return

        # transition selected items from the bika_listing/Table.
        transitioned = []
        if 'paths' in form:
            for path in form['paths']:
                item_id = path.split("/")[-1]
                item_path = path.replace("/" + item_id, '')
                item = pc(id = item_id,
                          path = {'query':item_path,
                                  'depth':1})[0].getObject()
                if isActive(item):
                    if hasattr(self.request, 'workflow_skiplist') and \
                       item.UID() in self.request['workflow_skiplist']:
                        pass
                    else:
                        workflow.doActionFor(item, action)
                        transitioned.append(item.Title())

        if len(transitioned) > 0:
            message = _('Changes saved.')
        else:
            message = _('No items were affected.')

        self.context.plone_utils.addPortalMessage(message, 'info')
        self.request.response.redirect(originating_url)

class BikaListingView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/bika_listing.pt")

    title = ""
    description = ""
    contentFilter = {}
    allow_edit = True
    content_add_actions = {}    # XXX menu.zcml/menu.py
    show_editable_border = True # XXX viewlets.zcml entries
    show_filters = False
    show_select_column = False
    show_select_row = False
    show_sort_column = False
    show_workflow_action_buttons = True
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
         'columns':['state_title',]
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
        if hasattr(self, 'show_editable_border') and not self.show_editable_border:
            self.request.set('disable_border', 1)

        form = self.request.form
        pc = getToolByName(self.context, 'portal_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')

        if form.has_key('review_state_clicked'):
            self.modified_contentFilter = self.contentFilter
            if form.has_key("review_state"):
                review_state = [r for r in self.review_states if \
                                r['id'] == form['review_state']][0]
                if review_state.has_key('contentFilter'):
                    for k,v in review_state['contentFilter'].items():
                        self.modified_contentFilter[k] = v
                else:
                    if form['review_state'] != 'all':
                        self.modified_contentFilter['review_state'] = form['review_state']

            return self.contents_table()

        if form.has_key('filter_input_keypress'):
            self.modified_contentFilter = self.contentFilter
            for key, value in form.items():
                if key.endswith("column-filter-input") and value:
                    self.modified_contentFilter[key.split("-")[1]] = value
            return self.contents_table()

        if form.has_key('clear_filters'):
            if hasattr(self, 'modified_contentFilter'):
                del self.modified_contentFilter
            return self.contents_table()

        return self.template()

    def folderitems(self, full_objects=False):
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

        # XXX temporary
        if not hasattr(self, 'modified_contentFilter'):
            self.modified_contentFilter = self.contentFilter

        results = []
        for i, obj in enumerate(self.contentsMethod(self.modified_contentFilter)):
            # we still don't know if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                 "/".join(obj.getPhysicalPath())

            item_inactive = False
            if (hasattr(obj,'inactive_review_state') and \
                obj.inactive_review_state == 'inactive') \
               or workflow.getInfoFor(obj, 'inactive_review_state', '') == 'inactive':
                item_inactive = True

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not show_all and not start <= i < end:
                results.append(dict(path = path))
                continue

            if full_objects and hasattr(obj, 'getObject'):
                obj = obj.getObject()

            uid = hasattr(obj, 'getUID') and obj.getUID() or obj.UID
            if callable(uid): uid = uid()

            title = hasattr(obj, 'getTitle') and obj.getTitle() or obj.Title
            if callable(title): title = title()

            icon = plone_layout.getIcon(obj)

            review_state = hasattr(obj, 'review_state') \
                         and obj.review_state or None
            if not review_state:
                try:
                    review_state = workflow.getInfoFor(obj, 'review_state')
                except:
                    review_state = ''

            url = hasattr(obj, 'getURL') and obj.getURL() or \
                "/".join(obj.getPhysicalPath())

            relative_url = hasattr(obj, 'getURL') and \
                         obj.getURL(relative=True) or \
                         "/".join(obj.getPhysicalPath())

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type

            description = obj.Description
            if callable(description): description = description()
            url_href_title = u'%s at %s: %s' % \
                (translate(type_title_msgid, context = self.request),
                 path,
                 safe_unicode(description))

            modified = plone_view.toLocalizedTime(obj.ModificationDate,
                                                  long_format = 1)

            # Check for InterimFields attribute on our object,
            interim_fields = hasattr(obj, 'getInterimFields') \
                           and obj.getInterimFields or []
            if not interim_fields:
                interim_fields = hasattr(obj, 'InterimFields') \
                               and obj.InterimFields or []
            if callable(interim_fields): interim_fields = interim_fields()

            # element css classes
            type_class = 'contenttype-' + plone_utils.normalizeString(obj.portal_type)
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            if item_inactive:
                state_class += ' state-inactive'
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

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
                review_state = review_state,
                # a list of lookups for single-value-select fields
                choices = [],
                state_title = workflow.getTitleForStateOnType(review_state,
                                                        obj.portal_type),
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

            # XXX debug - add history_id column
            if App.config.getConfiguration().debug_mode:
                from Products.CMFEditions.utilities import dereference
                pr = getToolByName(self.context, 'portal_repository')
                o = hasattr(obj, 'getObject') and obj.getObject() or obj
                if pr.isVersionable(o):
                    pa = getToolByName(self.context, 'portal_archivist')
                    history_id = str(dereference(o)[1])
                    version_id = hasattr(o,'version_id') \
                               and str(o.version_id) or None
                    if not 'version_id' in self.columns.keys():
                        self.columns['version_id'] = {'title':'version'}
                        for x in range(len(self.review_states)):
                            if self.review_states[x]['id'] == 'all':
                                self.review_states[x]['columns'].append('version_id')
                    results_dict['version_id'] = '%s/%s' % (version_id, history_id)

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
                    # if it's a HistoryAwareReference pointed at a previous
                    # revision, force (vx/x) into the text.
                    results_dict[key] = value
            results.append(results_dict)

        return results

    def contents_table(self):
        self.filters_in_use = False
        for key in self.columns.keys():
            if key in self.contentFilter.keys():
                self.filters_in_use = True
        table = BikaListingTable(self)
        return table.render()

class BikaListingTable(FolderContentsTable):

    def __init__(self, bika_listing):
        self.context = bika_listing.context
        self.request = bika_listing.request
        self.table = Table(bika_listing)

    def render(self):
        return self.table.render()

class Table(tableview.Table):
    def __init__(self, bika_listing):

        folderitems = bika_listing.folderitems

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
        self.show_filters = bika_listing.show_filters
        self.show_workflow_action_buttons = bika_listing.show_workflow_action_buttons
        self.filters_in_use = bika_listing.filters_in_use
        self.review_states = bika_listing.review_states

    def get_workflow_actions(self):
        """ Compile a list of possible workflow transitions for items
            in this Table.
        """
        workflow = getToolByName(self.context, 'portal_workflow')

        # return empty list if selecting checkboxes are disabled
        if not self.show_select_column:
            return []

        state = self.request.get('review_state', 'all')
        review_state = [i for i in self.review_states if i['id'] == state][0]

        # get all transitions for all items.
        # if there is a review_state['some_state']['transitions'] attribute
        # on the BikaListingView, the list is restricted to these transitions
        transitions = []
        for i, item in enumerate(self.items):
            if not item.has_key('obj'): continue
            obj = hasattr(item['obj'], 'getObject') and \
                item['obj'].getObject() or \
                item['obj']
            for w in workflow.getWorkflowsFor(obj):
                for tid,t in w.transitions.items():
                    if w.isActionSupported(obj, tid):
                        if t not in transitions:
                            if review_state.has_key('transitions') and \
                               tid not in review_state['transitions']:
                                pass
                            else:
                                transitions.append(t)
        return transitions

    render = ViewPageTemplateFile("templates/bika_listing_table.pt")
    batching = ViewPageTemplateFile("templates/bika_listing_batching.pt")
