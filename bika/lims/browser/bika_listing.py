""" Display lists of items in tables.
"""
from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.component._api import getMultiAdapter
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
import json
import urllib

class BikaListingView(FolderContentsView):
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
    # just set pagesize high to disable batching.
    pagesize = 50

##     The keys of the columns dictionary must all exist in all
##     items returned by subclassing view's .foldercontents.
##
##     possible column dictionary keys are:
##
##     - "allow_edit": boolean
##       if View.allow_edit is also True, this field is made editable
##
##     - "type": string
##       possible values: "str", "bool"
##
##     - "show_icon": string
##       possible values: "before" or "after".
##       Displays the content type icon in this column, either before
##       or after the field contents.

    columns = {
           'obj_type': {'title': _('Type'),
                        'show_icon': "before"},
           'id': {'title': _('ID')},
           'title_or_id': {'title': _('Title')},
           'modified': {'title': _('Last modified')},
           'state_title': {'title': _('State')},
    }

    # with just one review_state, the selector won't show.
    review_states = [
        {'id':'all',
         'title': _('All'),
         'columns':['obj_type',
                    'id',
                    'title_or_id',
                    'modified',
                    'state_title']
         },
    ]

    def __init__(self, context, request):
        super(BikaListingView, self).__init__(context, request)
        if self.show_editable_border: request.set('enable_border', 1)      # XXX
        if not self.show_editable_border: request.set('disable_border', 1) # XXX
        # contentsMethod may return a list of brains or a list of objects.
        self.contentsMethod = self.context.getFolderContents

    def __call__(self):
        form = self.request.form
        pc = getToolByName(self.context, 'portal_catalog')
        wf = getToolByName(self.context, 'portal_workflow')

        # inserted before ajax form submit by bika_listing.js when review_state radio is clicked
        if form.has_key('review_state_clicked'):
            # modify contentFilter with review_state radio value
            if form.has_key("review_state"):
                if self.request['review_state'] == 'all':
                    if self.contentFilter.has_key('review_state'):
                        del(self.contentFilter['review_state'])
                else:
                    self.contentFilter['review_state'] = form['review_state']

            return self.contents_table()

        # bika_listing.js submits this when the user pressed enter in a filter input
        if form.has_key('filter_input_keypress'):
            # modify contentFilter with text filters if specified
            for key, value in form.items():
                if key.endswith("column-filter-input") and value:
                    self.contentFilter[key.split("-")[1]] = value
            return self.contents_table()

        if form.has_key('clear_filters'):
            for key in self.columns.keys():
                if self.contentFilter.has_key(key):
                    del self.contentFilter[key]
            return self.contents_table()

        # workflow transition action was submitted
        if form.has_key('transition_action_submitted'):
            action = form['transition_action']
            for path in form['paths']:
                item_id = path.split("/")[-1]
                item_path = path.replace("/" + item_id, '')
                item = pc(id = item_id, path = {'query':item_path, 'depth':1})[0].getObject()
                wf.doActionFor(item, action)

            # subclass form_submit is only called for transition actions
            if hasattr(self, 'form_submit'):
                self.form_submit(form)

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
        portal_workflow = getToolByName(context, 'portal_workflow')
        site_properties = portal_properties.site_properties

        browser_default = plone_utils.browserDefault(context)

        show_all = self.request.get('show_all', '').lower() == 'true'
        pagenumber = int(self.request.get('pagenumber', 1) or 1)
        pagesize = self.pagesize
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        results = []
        for i, obj in enumerate(self.contentsMethod(self.contentFilter)):
            # we still don't know if it's a brain or an object
            path = hasattr(obj, 'getPath') and obj.getPath() or \
                 "/".join(obj.getPhysicalPath())

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

            review_state = hasattr(obj, 'review_state') and obj.review_state or None
            if not review_state:
                try:
                    review_state = portal_workflow.getInfoFor(obj, 'review_state')
                except:
                    review_state = ''

            url = hasattr(obj, 'getURL') and obj.getURL() or \
                "/".join(obj.getPhysicalPath())

            relative_url = hasattr(obj, 'getURL') and obj.getURL(relative=True) or \
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

            modified = plone_view.toLocalizedTime(obj.ModificationDate, long_format = 1)

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            # Check for InterimFields attribute on our object,
            interim_fields = hasattr(obj, 'getInterimFields') and obj.getInterimFields or []
            if not interim_fields:
                interim_fields = hasattr(obj, 'InterimFields') and obj.InterimFields or []
            if callable(interim_fields): interim_fields = interim_fields()

            # element css classes
            type_class = 'contenttype-' + plone_utils.normalizeString(obj.portal_type)
            state_class = 'state-' + plone_utils.normalizeString(review_state)
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
                fti = fti,
                interim_fields = interim_fields,
                item_data = json.dumps(interim_fields),
                url = url,
                url_href_title = url_href_title,
                obj_type = obj.Type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                review_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                                     obj.portal_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                relative_url = relative_url,
                view_url = url,
                table_row_class = table_row_class,
            )

            # look through self.columns for object attribute names (the column key),
            # and try get them from the brain/object.
            for key in self.columns.keys():
                if hasattr(obj, key):
                    value = getattr(obj, key)
                    # if it's callable call it.
                    if callable(value):
                        value = value()
                    # if the key is already in the results dict
                    # then we don't replace it's value
                    if not results_dict.has_key(key):
                        results_dict[key] = value

            results.append(results_dict)

        return results

    def contents_table(self):
        # discover if filters are enabled for any of our column keys
        self.filters_in_use = False
        for key in self.columns.keys():
            if key in self.contentFilter.keys():
                self.filters_in_use = True

        # all these variables are defined by the subclass, but actually required
        # by the table, so we pass them around wholesale.
        table = BikaListingTable(aq_inner(self.context),
                                 self.request,
                                 folderitems = self.folderitems,
                                 columns = self.columns,
                                 review_states = self.review_states,
                                 pagesize = self.pagesize,
                                 show_sort_column = self.show_sort_column,
                                 show_select_row = self.show_select_row,
                                 show_select_column = self.show_select_column,
                                 show_filters = self.show_filters,
                                 filters_in_use = self.filters_in_use)
        return table.render()

class BikaListingTable(FolderContentsTable):
    def __init__(self,
                 context,
                 request,
                 folderitems,
                 columns,
                 review_states,
                 pagesize,
                 show_sort_column,
                 show_select_row,
                 show_select_column,
                 show_filters,
                 filters_in_use):
        self.context = context
        self.request = request
        url = context.absolute_url()
        self.table = Table(context,
                           request,
                           url,
                           url + "/view",
                           folderitems(),
                           columns,
                           review_states,
                           show_sort_column = show_sort_column,
                           show_select_row = show_select_row,
                           show_select_column = show_select_column,
                           show_filters = show_filters,
                           filters_in_use = filters_in_use,
                           pagesize = pagesize)

    def render(self):
        return self.table.render()

class Table(tableview.Table):
    def __init__(self,
                 context,
                 request,
                 base_url,
                 view_url,
                 items,
                 columns,
                 review_states,
                 show_sort_column,
                 show_select_row,
                 show_select_column,
                 show_filters,
                 filters_in_use,
                 pagesize):

        tableview.Table.__init__(self,
                                 request,
                                 base_url,
                                 view_url,
                                 items,
                                 show_select_column = show_select_column,
                                 show_sort_column = show_sort_column,
                                 pagesize = pagesize)

        self.context = context
        self.request = request
        self.columns = columns
        self.show_sort_column = show_sort_column
        self.show_select_row = show_select_row
        self.show_select_column = show_select_column
        self.show_filters = show_filters
        self.filters_in_use = filters_in_use
        self.review_states = review_states

    render = ViewPageTemplateFile("templates/bika_listing_table.pt")
    batching = ViewPageTemplateFile("templates/bika_listing_batching.pt")
