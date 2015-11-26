from bika.lims.permissions import *
from bika.lims import PMF, logger, bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.utils import getToolByName


class ClientSRTemplatesView(BikaListingView):
    """ Displays the client-specific Sampling Round Templates
    """

    def __init__(self, context, request):
        super(ClientSRTemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SRTemplate',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "srtemplates"
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/srtemplate_big.png"
        self.title = self.context.translate(_("SR Templates"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'Description']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'Description']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddSRTemplate, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=SRTemplate',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientSRTemplatesView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['title'] = obj.Title()
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])

        return items
