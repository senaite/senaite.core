from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IMethods
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class MethodsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Method', 'sort_on': 'sortable_title'}
    content_add_actions = {_('Method'): "createObject?type_name=Method"}
    title = _("Methods")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = True
    show_select_column = True
    pagesize = 20

    columns = {
               'Title': {'title': _('Method')},
               'Description': {'title': _('Description')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['Title', 'Description',],
                     'buttons':[{'cssclass': 'context',
                                 'Title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])


        return items

schema = ATFolderSchema.copy()
class Methods(ATFolder):
    implements(IMethods)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Methods, PROJECTNAME)
