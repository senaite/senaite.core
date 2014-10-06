from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IMethods
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.permissions import AddMethod, ManageBika
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class MethodsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(MethodsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Method',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Methods"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/method_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Method'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'Instrument': {'title': _('Instrument'),
                             'toggle': True},
            'Calculation': {'title': _('Calculation'),
                             'toggle': True},
            'ManualEntry': {'title': _('Manual entry'),
                             'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 
                         'Description', 
                         'Instrument',
                         'Calculation',
                         'ManualEntry']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 
                         'Description', 
                         'Instrument',
                         'Calculation',
                         'ManualEntry']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 
                         'Description', 
                         'Instrument',
                         'Calculation',
                         'ManualEntry']},
        ]



    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddMethod, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Method',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if not mtool.checkPermission(ManageBika, self.context):
            self.show_select_column = False
            self.review_states = [
                {'id':'default',
                 'title': _('All'),
                 'contentFilter':{},
                 'columns': ['Title', 
                             'Description',
                             'Instrument',
                             'Calculation',
                             'ManualEntry']}
            ]
        return super(MethodsView, self).__call__()

    def folderitems(self):

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            
            if obj.getInstruments():
                if len(obj.getInstruments()) > 1:
                    InstrumentLine = str()
                    urlStr = str()
                    for token in obj.getInstruments():
                        InstrumentLine += token.Title() + ", "
                        urlStr += "<a href='%s'>%s</a>" % (token.absolute_url(),token.Title())
                    items[x]['replace']['Instrument'] = urlStr

                else:
                    items[x]['Instrument'] = obj.getInstruments()[0].Title()
                    items[x]['replace']['Instrument'] = "<a href='%s'>%s</a>" % \
                        (obj.getInstruments()[0].absolute_url(), items[x]['Instrument'])
            else:
                items[x]['Instrument'] = ''

            if obj.getCalculation():
                items[x]['Calculation'] = obj.getCalculation().Title()
                items[x]['replace']['Calculation'] = "<a href='%s'>%s</a>" % \
                    (obj.getCalculation().absolute_url(), items[x]['Calculation'])
            else:
                items[x]['Calculation'] = ''
            
            img_url = '<img src="'+self.portal_url+'/++resource++bika.lims.images/ok.png"/>'
            items[x]['ManualEntry'] = obj.isManualEntryOfResults()
            items[x]['replace']['ManualEntry'] = img_url if obj.isManualEntryOfResults() else ' '

        return items

schema = ATFolderSchema.copy()
class Methods(ATFolder):
    implements(IMethods)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Methods, PROJECTNAME)
