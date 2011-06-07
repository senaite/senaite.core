from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_listing import BikaListingView
from Products.bika.config import PROJECTNAME
from Products.bika import bikaMessageFactory as _
from Products.bika.content.bikaschema import BikaFolderSchema
from Products.bika.interfaces import IHaveNoByline
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import IStandardManufacturers
from zope.interface.declarations import implements

class StandardManufacturersView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'StandardManufacturer'}
    content_add_buttons = {_('Standard Manufacturer'): "createObject?type_name=StandardManufacturer"}
    title = _("Standard Manufacturers")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
     show_select_row = False
    show_select_column = True
   batch = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title')},
               'StandardManufacturerDescription': {'title': _('Description')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'StandardManufacturerDescription'],
                     'buttons': [{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['StandardManufacturerDescription'] = obj.StandardManufacturerDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class StandardManufacturers(ATFolder):
    implements(IStandardManufacturers, IHaveNoByline)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StandardManufacturers, PROJECTNAME)
