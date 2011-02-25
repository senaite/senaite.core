from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika import logger
from zope.interface.declarations import implements

class AnalysisServicesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisService'}
    content_add_buttons = ['AnalysisService']
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
                                 'MaxHoursAllowed', 'DuplicateVariation', 'Calc'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        out = []
        for x in range(len(items)):
            # XXX some extra objects in items: {path: xxx}.  where from?  what are they?
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
