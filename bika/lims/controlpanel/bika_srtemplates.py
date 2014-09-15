from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.interfaces import ISRTemplates
from zope.interface.declarations import implements


class TemplatesView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(TemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SRTemplate',
            'sort_order': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0
            },
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.icon = self.portal_url + "/++resource++bika.lims.images/artemplate_big.png"
        self.title = self.context.translate(_("SR Templates"))
        self.description = ""
        self.context_actions = {
            _('Add Template'): {
                'url': 'createObject?type_name=SRTemplate',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }

        self.columns = {
            'Title': {
                'title': _('Template'),
                'index': 'sortable_title'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description'
            },
        }

        self.review_states = [{
            'id':'default',
            'title': _('Default'),
            'contentFilter': {},
            'columns': ['Title', 'Description']
        }]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for item in items:
            if not item.has_key('obj'): continue
            obj = item['obj']
            title_link = "<a href='%s'>%s</a>" % (item['url'], item['title'])
            item['replace']['Title'] = title_link
        return items


schema = ATFolderSchema.copy()


class SRTemplates(ATFolder):
    implements(ISRTemplates)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SRTemplates, PROJECTNAME)
