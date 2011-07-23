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
from bika.lims.interfaces import IAttachmentTypes
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class AttachmentTypesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AttachmentType'}
    content_add_actions = {_('Attachment Type'): "createObject?type_name=AttachmentType"}
    title = _("Attachment Types")
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title')},
               'AttachmentTypeDescription': {'title': _('Description')},
              }
    review_states = [
                    {'title_or_id': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'AttachmentTypeDescription'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class AttachmentTypes(ATFolder):
    implements(IAttachmentTypes)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AttachmentTypes, PROJECTNAME)
