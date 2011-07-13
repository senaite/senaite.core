from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IReferenceDefinitions
from zope.interface.declarations import implements

class ReferenceDefinitionsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'ReferenceDefinition'}
    content_add_actions = {_('Reference Definition'): "createObject?type_name=ReferenceDefinition"}
    title = _("Reference Definitions")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title')},
               'ReferenceDefinitionDescription': {'title': _('Description')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'ReferenceDefinitionDescription'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['ReferenceDefinitionDescription'] = obj.ReferenceDefinitionDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class ReferenceDefinitions(ATFolder):
    implements(IReferenceDefinitions)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ReferenceDefinitions, PROJECTNAME)
