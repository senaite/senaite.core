from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_listing import BikaListingView
from Products.bika.config import PROJECTNAME
from Products.bika import bikaMessageFactory as _
from Products.bika.interfaces import IHaveNoByline
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import ISamplePoints
from zope.interface.declarations import implements

class SamplePointsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'SamplePoint'}
    content_add_buttons = {_('Sample Point'): "createObject?type_name=SamplePoint"}
    title = _("Sample Points")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title'), 'icon':'samplepoint.png'},
               'SamplePointDescription': {'title': _('Description')},
              }
    review_states = [
                    {'title_or_id': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'SamplePointDescription'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['SamplePointDescription'] = obj.SamplePointDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class SamplePoints(ATFolder):
    implements(ISamplePoints, IHaveNoByline)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SamplePoints, PROJECTNAME)
