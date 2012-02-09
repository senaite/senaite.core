from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
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
        bsc = getToolByName(context, 'bika_setup_catalog')
        self.contentsMethod = bsc
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url':'createObject?type_name=AnalysisService',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = "++resource++bika.lims.images/analysisservice_big.png"
        self.title = _("Analysis Services")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 1000

        self.columns = {
            'Title': {'title': _('Service'), 'sortable':False},
            'Keyword': {'title': _('Keyword'), 'sortable':False, 'toggle': True},
            'Department': {'title': _('Department'), 'sortable':False, 'toggle': False},
            'Instrument': {'title': _('Instrument'), 'sortable':False, 'toggle': True},
            'Unit': {'title': _('Unit'), 'sortable':False, 'toggle': True},
            'Price': {'title': _('Price'), 'sortable':False, 'toggle': True},
            'MaxTimeAllowed': {'title': _('Max Time'), 'sortable':False, 'toggle': False},
            'DuplicateVariation': {'title': _('Dup Var'), 'sortable':False, 'toggle': False},
            'Calculation': {'title': _('Calculation'), 'sortable':False, 'toggle': True},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title',
                         'Keyword',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             },
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Keyword',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             },
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Keyword',
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
        self.categories = []

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Keyword'] = obj.getKeyword()
            items[x]['Category'] = obj.getCategoryTitle()
            items[x]['category'] = items[x]['Category']
            if items[x]['Category'] not in self.categories:
                self.categories.append(items[x]['Category'])
            items[x]['Instrument'] = obj.getInstrument() and obj.getInstrument().Title() or ' '
            items[x]['Department'] = obj.getDepartment() and obj.getDepartment().Title() or ' '
            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()
            items[x]['Unit'] = obj.getUnit() and obj.getUnit() or ''
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
                after_icons += "<img src='++resource++bika.lims.images/accredited.png' title='%s'>"%(_("Accredited"))
            if obj.getReportDryMatter():
                after_icons += "<img src='++resource++bika.lims.images/dry.png' title='%s'>"%(_("Can be reported as dry matter"))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img src='++resource++bika.lims.images/attach_reqd.png' title='%s'>"%(_("Attachment required"))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img src='++resource++bika.lims.images/attach_no.png' title='%s'>"%(_('Attachment not permitted'))
            if after_icons:
                items[x]['after']['Title'] = after_icons
            items[x]['replace']['Calculation'] = calculation and "<a href='%s'>%s</a>" % \
                 (calculation.absolute_url() + "/edit", calculation.Title()) or ''

        return items

schema = ATFolderSchema.copy()
class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisServices, PROJECTNAME)
