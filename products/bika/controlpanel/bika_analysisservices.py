from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import IAnalysisServices
from zope.interface.declarations import implements

class AnalysisServicesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisService'}
    content_add_buttons = {'Analysis Service': "createObject?type_name=AnalysisService"}
    title = "Analysis Services"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'CategoryName': {'title': 'Category'},
               'ReportDryMatter': {'title': 'Report as dry matter'},
               'AttachmentOption': {'title': 'Attachments'},
               'Unit': {'title': 'Unit'},
               'Price': {'title': 'Price excluding VAT'},
               'CorporatePrice': {'title': 'Corporate price excluding VAT'},
               'MaxHoursAllowed': {'title': 'Maximum Hours Allowed'},
               'DuplicateVariation': {'title': 'Duplicate Variation'},
               'Calc': {'title': 'Calc'},
              }
    wflist_states = [
                     {'title_or_id': 'All', 'id':'all',
                      'columns': ['title_or_id', 'CategoryName', 'ReportDryMatter',
                                  'AttachmentOption', 'Unit', 'Price', 'CorporatePrice',
                                  'MaxHoursAllowed', 'DuplicateVariation', 'Calc',
                                 ],
                      'buttons':[BikaFolderContentsView.default_buttons['delete'],
                                 {'cssclass':'context',
                                  'title': 'Duplicate',
                                  'url': 'duplicate_services:method', # XXX Duplicate Analysis Service
                                 }
                                ],
                     },
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        out = []
        for x in range(len(items)):
            # XXX some extra objects in items: {path: xxx}.
            try: obj = items[x]['obj'].getObject()
            except KeyError: continue
            items[x]['CategoryName'] = obj.getCategoryName()
            items[x]['ReportDryMatter'] = obj.ReportDryMatter
            items[x]['AttachmentOption'] = \
                obj.Schema()['AttachmentOption'].Vocabulary().getValue(obj.AttachmentOption)
            items[x]['Unit'] = obj.Unit
            items[x]['Price'] = obj.Price
            items[x]['CorporatePrice'] = obj.CorporatePrice
            items[x]['MaxHoursAllowed'] = obj.MaxHoursAllowed
            items[x]['DuplicateVariation'] = obj.DuplicateVariation
            calc = obj.getCalculationType()
            items[x]['Calc'] = calc and calc.Title() or ''
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}
            out.append(items[x])
        return out

schema = ATFolderSchema.copy()
class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisServices, PROJECTNAME)
