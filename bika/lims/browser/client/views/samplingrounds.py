from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.utils import getToolByName
from bika.lims.controlpanel.bika_samplingrounds import SamplingRoundsView


class ClientSamplingRoundsView(SamplingRoundsView):
    """This is displayed in the "Sampling Rounds" tab on each client
    """

    def __init__(self, context, request):
        super(ClientSamplingRoundsView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'SamplingRound',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.title = self.context.translate(_("Client Sampling Rounds"))
        self.context_actions = {
            _('Add'): {'url': '++add++SamplingRound',  # To work with dexterity
                       'icon': '++resource++bika.lims.images/add.png'}}
        self.column = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description')},
            'num_sample_points': {'title': _('Number of sampling points'),
                                  'index': 'sortable_title',
                                  'sortable': True},
            'num_containers': {'title': _('Number of containers'),
                               'index': 'sortable_title',
                               'sortable': True},
        }

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return super(ClientSamplingRoundsView, self).__call__()

    def folderitems(self, full_objects=True):
        items = BikaListingView.folderitems(self, full_objects)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['title'] = obj.Title()
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])
        return items
