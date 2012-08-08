from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IContainers
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class ContainersView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ContainersView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Container',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Container',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = _("Containers")
        self.icon = "++resource++bika.lims.images/container_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Container'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'ContainerType': {'title': _('Container Type'),
                              'toggle': True},
            'Capacity': {'title': _('Capacity'),
                         'toggle': True},
            'Pre-preserved': {'title': _('Pre-preserved'),
                             'toggle': True},
        }

        self.review_states = [ # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'inactive_state':'active'},
             'title': _('Active'),
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['ContainerType'] = obj.getContainerType() and obj.getContainerType().Title() or ''
            items[x]['Capacity'] = obj.getCapacity() and "%s" % \
                (obj.getCapacity()) or ''
            pre = obj.getPrePreserved()
            pres = obj.getPreservation()
            items[x]['Pre-preserved'] = ''
            items[x]['after']['Pre-preserved'] = pre \
                and "<a href='%s'>%s</a>" % (pres.absolute_url(), pres.Title()) \
                or ''

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class Containers(ATFolder):
    implements(IContainers)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Containers, PROJECTNAME)
