from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IAnalysisServices
from zope.interface.declarations import implements
from operator import itemgetter

class AnalysisServicesView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(AnalysisServicesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'):
                                    "createObject?type_name=AnalysisService"}
        self.icon = "++resource++bika.lims.images/service_big.png"
        self.title = _("Analysis Services")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Service')},
            'Keyword': {'title': _('Keyword')},
            'CategoryName': {'title': _('Category')},
            'Department': {'title': _('Department')},
            'Instrument': {'title': _('Instrument')},
            'Unit': {'title': _('Unit')},
            'Price': {'title': _('Price')},
            'MaxTimeAllowed': {'title': _('Max Time')},
            'DuplicateVariation': {'title': _('Dup Var')},
            'Calculation': {'title': _('Calculation')},
        }

        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title',
                         'Keyword',
                         'CategoryName',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             },
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title',
                         'Keyword',
                         'CategoryName',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             },
            {'title': _('Dormant'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title',
                         'Keyword',
                         'CategoryName',
                         'Department',
                         'Instrument',
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
            obj = items[x]['obj']
            items[x]['Keyword'] = obj.getKeyword()
            items[x]['CategoryName'] = obj.getCategoryName()
            items[x]['Instrument'] = obj.getInstrument() and obj.getInstrument().Title() or ' '
            items[x]['Department'] = obj.getDepartment() and obj.getDepartment().Title() or ' '
            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()
            items[x]['Unit'] = obj.Unit
            items[x]['Price'] = "%s.%02d" % (obj.Price)
            maxtime = obj.MaxTimeAllowed

            maxtime = obj.MaxTimeAllowed
            maxtime_string = ""
            for field in ('days','hours', 'minutes'):
                if field in maxtime:
                    try:
                        val = int(maxtime[field])
                        if val > 0:
                            maxtime_string += "%s%s "%(val, _(field[0]))
                    except: pass
            items[x]['MaxTimeAllowed'] = maxtime_string

            if obj.DuplicateVariation is not None:
                items[x]['DuplicateVariation'] = "%s.%02d" % (obj.DuplicateVariation)
            else: items[x]['DuplicateVariation'] = ""
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
            items[x]['replace']['Calculation'] = calculation and "<a href='%s'>%s</a>" % \
                 (calculation.absolute_url() + "/edit", calculation.Title()) or ''

        return items

schema = ATFolderSchema.copy()
class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisServices, PROJECTNAME)
