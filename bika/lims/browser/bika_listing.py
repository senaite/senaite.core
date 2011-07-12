from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, \
    FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims import bikaMessageFactory as _
from zope.component._api import getMultiAdapter
from zope.i18n import translate
from Products.Five.browser import BrowserView
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
import urllib

ploneMessageFactory = MessageFactory('plone')

class BikaListingView(FolderContentsView):
    template = ViewPageTemplateFile("templates/bika_listing.pt")

    title = ""
    description = ""
    contentFilter = {}
    content_add_actions = {}
    show_editable_border = True
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = False
    # batch is actually the batch itself; it's set to true here to make some bits of TAL happy.
    batch = True
    pagesize = 20

    def __init__(self, context, request):
        super(BikaListingView, self).__init__(context, request)
        if self.show_editable_border: request.set('enable_border', 1)
        if not self.show_editable_border: request.set('disable_border', 1)
        self.portal_types = getToolByName(context, 'portal_types')
        self.contentsMethod = self.context.getFolderContents


    def __call__(self):
        form = self.request.form
        pc = getToolByName(self.context, 'portal_catalog')
        wf = getToolByName(self.context, 'portal_workflow')

        # inserted by jquery when review_state radio is clicked
        if form.has_key('review_state_clicked'):
            # modify contentFilter with review_state radio value
            if form.has_key("review_state"):
                if self.request['review_state'] == 'all':
                    if self.contentFilter.has_key('review_state'):
                        del(self.contentFilter['review_state'])
                else:
                    self.contentFilter['review_state'] = form['review_state']
            return self.contents_table()

        # inserted by jquery when filter input keypress is accepted
        if form.has_key('filter_input_keypress'):
            # modify contentFilter with text filters if specified
            for key, value in form.items():
                if key.endswith("column-filter-input") and value:
                    self.contentFilter[key.split("-")[1]] = value
            return self.contents_table()

        # inserted by jquery [clear filters] item is clicked
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
                #try: # XXX in our folder views at the moment, we don't allow mixed types for submit?
                wf.doActionFor(item, action)
                #except:
                    # Since we could theoritically end up with items of mixed status selected,
                    # it can occur quite easily that the workflow_action doesn't work for some
                    # objects but we need to keep on going.
                    #pass

            # subclass form_submit is only called for transition actions
            if hasattr(self, 'form_submit'):
                self.form_submit(form)

        return self.template()

    def folderitems(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name = u'plone')
        plone_layout = getMultiAdapter((context, self.request), name = u'plone_layout')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties

        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = plone_utils.browserDefault(context)

        show_all = self.request.get('show_all', '').lower() == 'true'
        pagesize = self.pagesize
        pagenumber = int(self.request.get('pagenumber', 1) or 1)
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        results = []
        for i, obj in enumerate(self.contentsMethod(self.contentFilter)):
            path = obj.getPath or "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not show_all and not start <= i < end:
                results.append(dict(path = path))
                continue

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            icon = plone_layout.getIcon(obj)
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative = True)

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context = self.request),
                                          safe_unicode(obj.Description))

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format = 1)

            obj_type = obj.Type
            if obj.portal_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results_dict = dict(
                brain = obj,
                url = url,
                url_href_title = url_href_title,
                id = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = safe_unicode(pretty_title_or_id(plone_utils, obj)),
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                review_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = isExpired(obj),
            )
            # Insert all fields from the schema, if they are in the brains
            # XXX LIMIT TO ONLY NECESSARY VALUES (columns displayed)

            for field in obj.schema():
                if not results_dict.get(field):
                    results_dict[field] = getattr(obj, field)

            results.append(results_dict)

        return results

    def contents_table(self):
        # discover if filters are enabled in contentFilter
        self.filters_in_use = False
        for key in self.columns.keys():
            if key in self.contentFilter.keys():
                self.filters_in_use = True
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
