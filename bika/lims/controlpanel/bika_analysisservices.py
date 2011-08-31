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
from operator import itemgetter

class AnalysisServicesView(BikaListingView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(AnalysisServicesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Analysis Service'):
                                    "createObject?type_name=AnalysisService"}
        self.title = _("Analysis Services")
        self.show_editable_border = False
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Service')},
            'getKeyword': {'title': _('Keyword')},
            'CategoryName': {'title': _('Category')},
            'Unit': {'title': _('Unit')},
            'Price': {'title': _('Price')},
            'MaxTimeAllowed': {'title': _('Max Time')},
            'DuplicateVariation': {'title': _('Dup Var')},
            'Calculation': {'title': _('Calculation')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title',
                         'getKeyword',
                         'CategoryName',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             },
        ]


    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['CategoryName'] = obj.getCategoryName()
            items[x]['Unit'] = obj.Unit
            items[x]['Price'] = "%s.%02d" % (obj.Price)
            maxtime = obj.MaxTimeAllowed
            items[x]['MaxTimeAllowed'] = 'days' in maxtime and maxtime['days'] \
                 and "%s%s"%(maxtime['days'], _('D')) or ""
            items[x]['MaxTimeAllowed'] += 'hours' in maxtime and maxtime['hours'] \
                 and "%s%s"%(maxtime['hours'], _('H')) or ""
            items[x]['MaxTimeAllowed'] += 'minutes' in maxtime and maxtime['minutes'] \
                 and "%s%s"%(maxtime['minutes'], _('M')) \
                 or not (('hours' in maxtime and maxtime['hours'])) \
                 and '0%s'%(_('M')) \
                 or ''

            if obj.DuplicateVariation is not None:
                items[x]['DuplicateVariation'] = "%s.%02d" % (obj.DuplicateVariation)
            else: items[x]['DuplicateVariation'] = ""
            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title() or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img src='++resource++bika.lims.images/accredited.png' title='Accredited'>"
            if obj.getReportDryMatter():
                after_icons += "<img src='++resource++bika.lims.images/dry.png' title='Can be reported as dry matter'>"
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img src='++resource++bika.lims.images/attach_reqd.png' title='Attachment required'>"
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img src='++resource++bika.lims.images/attach_no.png' title='Attachment not permitted'>"
            if after_icons:
                items[x]['after']['Title'] = after_icons

        return items

schema = ATFolderSchema.copy()
class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisServices, PROJECTNAME)
