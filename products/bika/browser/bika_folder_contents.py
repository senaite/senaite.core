from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.bika import logger
from plone.app.content.browser import tableview
from plone.app.content.browser.foldercontents import FolderContentsView, \
    FolderContentsTable
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.component._api import getMultiAdapter
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
import urllib
ploneMessageFactory = MessageFactory('plone')

class BikaFolderContentsView(FolderContentsView):
    """
    """

    implements(IFolderContentsView)
    template = ViewPageTemplateFile("templates/bika_folder_contents.pt")
    wflist = ViewPageTemplateFile("templates/wflist.pt")

    contentFilter = {}
    batch = True
    b_size = 20
    full_objects = False
    enable_border = True

    # the draggable bit for re-ordering rows manually
    show_sort_column = False

    # the select All/Batch/None row.
    show_select_row = False

    title = "Folder Contents"
    description = ""

    # setting this to a list of portal_type IDs restricts the Add New... contentactions menu.
    # setting it to empty displays the Plone default list.
    # setting it to None will disable the Add new... menu # XXX ?
    allowed_content_types = []

    # A list of portal_types for 'Add X' buttons above the output
    content_add_buttons = []

    # The fields listed must be in the catalog metadata
    # or folderitems() must be overridden to provide them
    # if they are not in brains.
    columns = [
              {'title': 'Title', 'field':'title_or_id'},
              {'title': 'Size', 'field':'size'},
              {'title': 'Modified', 'field':'modified'},
              {'title': 'State', 'field':'state_title'},
              ]


    # Setting this enables and configures the workflow state selector.
    wflist_states = []

    def __init__(self, context, request):
        super(BikaFolderContentsView, self).__init__(context, request)
        self.context.allowed_content_types = self.allowed_content_types
        self.portal_types = getToolByName(context, 'portal_types')

    def getFolderContents(self):
        """ Lifted from CMFPlone/skins/plone_skins/getFolderContents.py
        """
        context = aq_inner(self.context)

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_membership = getToolByName(context, 'portal_membership')

        if not self.contentFilter.get('sort_on', None):
            self.contentFilter['sort_on'] = 'getObjPositionInParent'

        cur_path = '/'.join(context.getPhysicalPath())
        path = {}
        if self.contentFilter.get('path', None) is None:
            path['query'] = cur_path
            path['depth'] = 1
            self.contentFilter['path'] = path

        show_inactive = portal_membership.checkPermission('Access inactive portal content', context)

        contents = portal_catalog.queryCatalog(self.contentFilter, show_all = 1, show_inactive = show_inactive)

        if self.full_objects:
            contents = [b.getObject() for b in contents]

        if self.batch:
            from Products.CMFPlone.PloneBatch import Batch
            b_start = context.REQUEST.get('b_start', 0)
            batch = Batch(contents, self.b_size, int(b_start), orphan = 0)
            return batch

        return contents

    def folderitems(self):
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
        pagesize = 20
        pagenumber = int(self.request.get('pagenumber', 1))
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        results = []
        for i, obj in enumerate(self.getFolderContents()):
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
            icon = plone_layout.getIcon(obj);
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
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results_dict = dict(
                obj = obj,
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
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state, obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = isExpired(obj),
                links = {},
            )

            # Insert all fields from the schema, if they are in the brains
            for field in obj.schema():
                if not results_dict.get(field):
                    results_dict[field] = getattr(obj, field)

            results.append(results_dict)

        return results

    def __call__(self):
        return self.template()

    def contents_table(self):
        table = BikaFolderContentsTable(aq_inner(self.context),
                                        self.request,
                                        getFolderContents = self.getFolderContents,
                                        folderitems = self.folderitems,
                                        columns = self.columns,
                                        wflist_states = self.wflist_states,
                                        pagesize = self.b_size,
                                        show_sort_column = self.show_sort_column,
                                        show_select_row = self.show_select_row,
                                        view_url = "/@@bika_folder_contents",
                                        )

        return table.render()


class BikaFolderContentsTable(FolderContentsTable):
    """
    """
    implements(IFolderContentsView)

    def __init__(self,
                 context,
                 request,
                 getFolderContents,
                 folderitems,
                 columns,
                 wflist_states,
                 pagesize,
                 show_sort_column,
                 show_select_row,
                 view_url = '/@@bika_folder_contents'):
        self.context = context
        self.request = request
        self.getFolderContents = getFolderContents
        self.items = folderitems() # XXX original buttons() requires this
        url = context.absolute_url()
        self.table = Table(request,
                           url,
                           url + view_url,
                           self.items,
                           columns,
                           wflist_states,
                           show_sort_column = show_sort_column,
                           show_select_row = show_select_row,
                           buttons = self.buttons,
                           pagesize = pagesize)

    def render(self):
        return self.table.render()

class Table(tableview.Table):
    def __init__(self,
                 request,
                 base_url,
                 view_url,
                 items,
                 columns,
                 wflist_states,
                 show_sort_column = False,
                 show_select_row = False,
                 buttons = [],
                 pagesize = 20):

        tableview.Table.__init__(self,
                                 request,
                                 base_url,
                                 view_url,
                                 items,
                                 show_sort_column = show_sort_column,
                                 buttons = [],
                                 pagesize = 20)

        self.columns = columns
        self.show_select_row = show_select_row
        self.wflist_states = wflist_states

    render = ViewPageTemplateFile("templates/table.pt")
    batching = ViewPageTemplateFile("templates/batching.pt")
