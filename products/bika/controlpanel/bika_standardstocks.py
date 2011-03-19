from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import IStandardStocks
from zope.interface.declarations import implements

class StandardStocksView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'StandardStock'}
    content_add_buttons = {'Standard Stock': "createObject?type_name=StandardStock"}
    title = "Standard Stocks"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'StandardStockDescription': {'title': 'Description'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'StandardStockDescription'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['StandardStockDescription'] = obj.StandardStockDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class StandardStocks(ATFolder):
    implements(IStandardStocks)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StandardStocks, PROJECTNAME)
