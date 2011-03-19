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
from Products.bika.interfaces.controlpanel import IInstruments
from zope.interface.declarations import implements

class InstrumentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Instrument'}
    content_add_buttons = {'Instrument': "createObject?type_name=Instrument"}
    title = "Instruments"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'Type': {'title': 'Type'},
               'Brand': {'title': 'Brand'},
               'Model': {'title': 'Model'},
               'ExpiryDate': {'title': 'Expiry Date'},
              }
    wflist_states = [
                    {'title_or_id': 'All', 'id':'all',
                     'columns': ['title_or_id', 'Type', 'Brand', 'Model', 'ExpiryDate'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['Type'] = obj.Type
            items[x]['Brand'] = obj.Brand
            items[x]['Model'] = obj.Model
            items[x]['ExpiryDate'] = obj.CalibrationExpiryDate
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class Instruments(ATFolder):
    implements(IInstruments)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Instruments, PROJECTNAME)
