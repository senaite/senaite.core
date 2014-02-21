from AccessControl.SecurityInfo import ClassSecurityInfo
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.arpriority import ARPriority
from bika.lims.interfaces import IARPriorities, IARPriority
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zope.interface.declarations import implements

class ARPrioritiesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ARPrioritiesView, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)
        request.set('disable_border', 1)

        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
                'portal_type': 'ARPriority',
                'path': {'query': '/'.join(context.getPhysicalPath())},
                'sort_on':'sortKey',
                }
        self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=ARPriority',
                 'icon': self.portal.absolute_url() + \
                         '/++resource++bika.lims.images/add.png'}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        self.form_id = "arpriorities"

        self.icon = \
            self.portal_url + "/++resource++bika.lims.images/arpriority_big.png"
        self.title = _("Analysis Request Priorities")
        self.description = ""


        self.columns = {
            'title': {'title': _('Priority')},
            'sortKey': {'title': _('Sort Key')},
            'pricePremium': {'title': _('Premium')},
            'isDefault': {'title': _('Default')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['title',
                         'sortKey',
                         'pricePremium',
                         'isDefault',
                         'state_title']},
            {'id':'draft',
             'title': _('Draft'),
             'contentFilter':{'review_state':'draft'},
             'columns': ['title',
                         'sortKey',
                         'pricePremium',
                         'isDefault',
                         ]},
            {'id':'published',
             'title': _('Published'),
             'contentFilter':{'review_state':'published'},
             'columns': ['title',
                         'sortKey',
                         'pricePremium',
                         'isDefault',
                         ]},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])

        return items


schema = ATFolderSchema.copy()
class ARPriorities(ATFolder):
    implements(IARPriorities)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARPriorities, PROJECTNAME)
