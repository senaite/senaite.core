from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IAnalysisSpecs
from zope.interface.declarations import implements
from plone.app.layout.globals.interfaces import IViewView
from operator import itemgetter
  
class AnalysisSpecsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisSpecsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisSpec',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'):
                                    "createObject?type_name=AnalysisSpec"}
        self.icon = "++resource++bika.lims.images/analysisspec_big.png"
        self.title = _("Analysis Specs")
        self.description = _("Set up the laboratory analysis service results specifications")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'getSampleType': {'title': _('Sample Type')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['getSampleType']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['getSampleType']},
            {'title': _('Dormant'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['getSampleType']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['getSampleType'] = obj.getSampleType() and obj.getSampleType().Title()
            items[x]['replace']['getSampleType'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getSampleType'])


        return items

schema = ATFolderSchema.copy()
class AnalysisSpecs(ATFolder):
    implements(IAnalysisSpecs)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisSpecs, PROJECTNAME)
