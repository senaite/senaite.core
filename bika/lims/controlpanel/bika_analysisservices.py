from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IAnalysisServices
from zope.interface.declarations import implements

class AnalysisServicesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisService'}
    content_add_actions = {_('Analysis Service'): "createObject?type_name=AnalysisService"}
    title = _("Analysis Services")
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 50

    columns = {
               'title_or_id': {'title': _('Title')},
               'CategoryName': {'title': _('Category')},
               'ReportDryMatter': {'title': _('Report as dry matter')},
               'AttachmentOption': {'title': _('Attachments')},
               'Unit': {'title': _('Unit')},
               'Price': {'title': _('Price excluding VAT')},
               'CorporatePrice': {'title': _('Corporate price excluding VAT')},
               'MaxHoursAllowed': {'title': _('Maximum Hours Allowed')},
               'DuplicateVariation': {'title': _('Duplicate Variation')},
               'Calculation': {'title': _('Calculation')},
              }
    review_states = [
                     {'title_or_id': _('All'), 'id':'all',
                      'columns': ['title_or_id',
                                  'CategoryName',
                                  'ReportDryMatter',
                                  'AttachmentOption',
                                  'Unit',
                                  'Price',
                                  'CorporatePrice',
                                  'MaxHoursAllowed',
                                  'DuplicateVariation',
                                  'Calculation',
                                 ],
                     },
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        out = []
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['CategoryName'] = obj.getCategoryName()
            items[x]['ReportDryMatter'] = obj.ReportDryMatter
            items[x]['AttachmentOption'] = \
                obj.Schema()['AttachmentOption'].Vocabulary().getValue(obj.AttachmentOption)
            items[x]['Unit'] = obj.Unit
            items[x]['Price'] = "%s.%02d" % (obj.Price)
            items[x]['CorporatePrice'] = "%s.%02d" % (obj.CorporatePrice)
            items[x]['MaxHoursAllowed'] = obj.MaxHoursAllowed
            if obj.DuplicateVariation is not None:
                items[x]['DuplicateVariation'] = "%s.%02d" % (obj.DuplicateVariation)
            else: items[x]['DuplicateVariation'] = ""
            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title() or ''
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
