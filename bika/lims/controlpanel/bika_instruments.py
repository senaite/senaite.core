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
from bika.lims.interfaces import IInstruments
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class InstrumentsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Instrument', 'sort_on': 'sortable_title'}
    content_add_actions = {_('Instrument'): "createObject?type_name=Instrument"}
    title = _("Instruments")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'Title': {'title': _('Instrument')},
               'Type': {'title': _('Type')},
               'Brand': {'title': _('Brand')},
               'Model': {'title': _('Model')},
               'ExpiryDate': {'title': _('Expiry Date')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['Title', 'Type', 'Brand', 'Model', 'ExpiryDate'],
                     'buttons':[{'cssclass': 'context',
                                 'Title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        out = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['Type'] = obj.Type
            items[x]['Brand'] = obj.Brand
            items[x]['Model'] = obj.Model
            items[x]['ExpiryDate'] = obj.CalibrationExpiryDate
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

            out.append(items[x])

        out = sorted(out, key=itemgetter('Title'))
        for i in range(len(out)):
            out[i]['table_row_class'] = ((i + 1) % 2 == 0) and "draggable even" or "draggable odd"
        return out

schema = ATFolderSchema.copy()
class Instruments(ATFolder):
    implements(IInstruments)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Instruments, PROJECTNAME)
