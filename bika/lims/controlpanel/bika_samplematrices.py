from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISampleMatrices
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.permissions import AddSampleMatrix, ManageBika
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class SampleMatricesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SampleMatricesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'SampleMatrix',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'): {
            'url': 'createObject?type_name=SampleMatrix',
            'icon': '++resource++bika.lims.images/add.png'
        }}
        self.title = _("Sample Matrices")
        self.icon = "++resource++bika.lims.images/samplematrix_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Sample Matrix'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions':[{'id':'empty'},],
             'columns': ['Title', 'Description']},
        ]

    def folderitems(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManageBika, self.context):
            del self.review_states[0]['transitions']
            self.show_select_column = True
            self.review_states.append(
                {'id':'active',
                 'title': _('Active'),
                 'contentFilter': {'inactive_state': 'active'},
                 'transitions': [{'id':'deactivate'}, ],
                 'columns': ['Title', 'Description']})
            self.review_states.append(
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['Title', 'Description']})

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class SampleMatrices(ATFolder):
    implements(ISampleMatrices)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SampleMatrices, PROJECTNAME)
