from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import ISamplePoints
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
import json
import plone

class SamplePointsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SamplePointsView, self).__init__(context, request)
        bsc = getToolByName(context, 'bika_setup_catalog')
        self.contentsMethod = bsc
        self.contentFilter = {'portal_type': 'SamplePoint',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=SamplePoint',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = _("Sample Points")
        self.icon = "++resource++bika.lims.images/samplepoint_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Sample Point'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title', 'Description']},
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
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

class SamplePoints(ATFolder):
    implements(ISamplePoints)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SamplePoints, PROJECTNAME)

class ajax_SamplePoints(BrowserView):
    """ autocomplete data source for sample points field
        return JSON data [string,string]
        if "sampletype" is in the request, it's expected to be a title string
        The objects returned will be filtered by the sampletype's SamplePoints.
        if no items are found, all items are returned.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self, 'bika_setup_catalog')
        term = self.request.get('term', '').lower()

        items = bsc(portal_type = "SamplePoint", sort_on='sortable_title')
        if term and len(term) > 1:
            items = [s.getObject() for s in items if s.Title.lower().find(term) > -1]
        else:
            items = [s.getObject() for s in items]

        sampletype = self.request.get('sampletype', '')
        if sampletype and len(sampletype) > 1:
            st = bsc(portal_type="SampleType",Title=sampletype)
            if not st:
                return json.dumps([])
            st = st[0].getObject()
            new = [s for s in items if s in st.getSamplePoints()]
            if new:
                items = new

        items = [s.Title() for s in items]
        return json.dumps(items)
