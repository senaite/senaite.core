from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class AnalysisServicesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisRequest'}
    content_add_buttons = ['AnalysisRequest']
    batch = True
    b_size = 100
    full_objects = False

    columns = {
               'title_or_id': {'title': 'Title'},
               'AnalysisCategory': {'title': 'Category'},
               'ReportDrymatter': {'title': 'Report as dry matter'},
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
                     'columns': ['title_or_id', 'AnalysisCategory', 'ReportDryMatter',
                                 'AttachmentOption', 'Unit', 'Price', 'CorporatePrice',
                                 'MaxHoursAllowed', 'DuplicateVariation', 'Calc'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['AnalysisCategory'] = obj.AnalysisCategory().Title()
            items[x]['ReportDryMatter'] = obj.ReportDryMatter()
            items[x]['AttachmentOption'] = \
                obj.Schema()['AttachmentOption'].Vocabulary().getMsgId(obj.AttachmentOption())
            items[x]['Unit'] = obj.Unit()
            items[x]['Price'] = obj.Price()
            items[x]['CorporatePrice'] = obj.CorporatePrice()
            items[x]['MaxHoursAllowed'] = obj.MaxHoursAllowed()
            items[x]['DuplicateVariation'] = obj.DuplicateVariation()
            items[x]['Calc'] = obj.CalculationType().Title()

            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
