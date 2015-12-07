from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


class ClientAnalysisProfilesView(BikaListingView):
    """This is displayed in the Profiles client action,
       in the "Analysis Profiles" tab
    """

    def __init__(self, context, request):
        super(ClientAnalysisProfilesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'AnalysisProfile',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisprofiles"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/analysisprofile_big.png"
        self.title = self.context.translate(_("Analysis Profiles"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'getProfileKey': {'title': _('Profile Key')},

        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'Description', 'getProfileKey']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddAnalysisProfile, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=AnalysisProfile',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisProfilesView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])

        return items
