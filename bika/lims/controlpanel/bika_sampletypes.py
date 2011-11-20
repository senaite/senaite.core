from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import ISampleTypes
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
import json

class SampleTypesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SampleTypesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'SampleType',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'):
                                    "createObject?type_name=SampleType"}
        self.title = _("Sample Types")
        self.icon = "++resource++bika.lims.images/sampletype_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
                   'Title': {'title': _('Sample Type'),
                             'index': 'sortable_title',},
                   'Description': {'title': _('Description'),
                                   'index': 'getDescription'},
                  }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title', 'Description']},
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title', 'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title', 'Description']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
        return items

schema = ATFolderSchema.copy()

class SampleTypes(ATFolder):
    implements(ISampleTypes)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SampleTypes, PROJECTNAME)

class ajax_SampleTypes():
    """ autocomplete data source for sample types field
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = pc(portal_type = "SampleType", sort_on='sortable_title')
        nr_items = len(items)
        items = [s.Title for s in items if s.Title.lower().find(term.lower()) > -1]

        ##XXX why does it return not all values in index?  only those that are 'referenced' by samples?
        #values = pc.Indexes['getSampleTypeTitle'].uniqueValues()
        #items = term and [v for v in values if v.lower().find(term.lower()) > -1]
        ###
        return json.dumps(items)

