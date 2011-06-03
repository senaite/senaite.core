from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_listing import BikaListingView
from Products.bika.config import PROJECTNAME
from Products.bika import bikaMessageFactory as _
from Products.bika.content.bikaschema import BikaFolderSchema
from ZODB.POSException import ConflictError
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import IWorksheetTemplates
from zope.interface.declarations import implements

class WorksheetTemplatesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'WorksheetTemplate'}
    content_add_buttons = {_('Worksheet Template'): "createObject?type_name=WorksheetTemplate"}
    title = _("Worksheet Templates")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = True
    show_select_column = False
    batch = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title')},
               'WorksheetTemplateDescription': {'title': _('Description')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'WorksheetTemplateDescription'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['WorksheetTemplateDescription'] = obj.WorksheetTemplateDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class WorksheetTemplates(ATFolder):
    implements(IWorksheetTemplates)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(WorksheetTemplates, PROJECTNAME)
