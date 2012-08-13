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
        self.catalog = 'bika_setup_catalog'
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
            'getComposite': {'title': _('Composite'),
                             'toggle': True},
            'SampleTypes': {'title': _('Sample Types'),
                            'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'Description', 'getComposite', 'SampleTypes']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 'Description', 'getComposite', 'SampleTypes']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 'Description', 'getComposite', 'SampleTypes']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['SampleTypes'] = ",".join([st.Title() for st in obj.getSampleTypes()])
        return items

schema = ATFolderSchema.copy()

class SamplePoints(ATFolder):
    implements(ISamplePoints)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SamplePoints, PROJECTNAME)

class ajax_SamplePoints(BrowserView):
    """ The autocomplete data source for sample point selection widgets.
        Returns a JSON list of sample point titles.

        Request parameters:

        - sampletype: if specified, it's expected to be the title
          of a SamplePoint object.  Optionally, the string 'Lab: ' might be
          prepended, to distinguish between Lab and Client objects.

        - term: the string which will be searched against all SamplePoint
          titles.

        - _authenticator: The plone.protect authenticator.

    """

    def filter_list(self, items, searchterm):
        if searchterm and len(searchterm) < 3:
            # Items that start with A or AA
            items = [s.getObject()
                     for s in items
                     if s.Title.lower().startswith(searchterm)]
            if not items:
                # or, items that contain A or AA
                items = [s.getObject()
                         for s in items
                         if s.Title.lower().find(searchterm) > -1]
        else:
            # or, items that contain searchterm.
            items = [s.getObject()
                     for s in items
                     if s.Title.lower().find(searchterm) > -1]
        return items

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        term = self.request.get('term', '').lower()
        items = []
        if not term:
            return items
        # Strip "Lab: " from sample point title
        term = term.replace("%s: " % _("Lab"), '')
        sampletype = self.request.get('sampletype', '')
        if sampletype and len(sampletype) > 1:
            st = bsc(portal_type = "SampleType",
                     title = sampletype,
                     inactive_state = 'active')
            if not st:
                return json.dumps([])
            st = st[0].getObject()
            items = [o.UID() for o in st.getSamplePoints()]

        if not items:
            client_items = lab_items = []

            # User (client) sample points
            if self.context.portal_type in ('Client', 'AnalysisRequest'):
                if self.context.portal_type == 'Client':
                    client_path = self.context.getPhysicalPath()
                else:
                    client_path = self.context.aq_parent.getPhysicalPath()
                client_items = list(
                    bsc(portal_type = "SamplePoint",
                        path = {"query": "/".join(client_path), "level" : 0 },
                        inactive_state = 'active',
                        sort_on='sortable_title'))

            # Global (lab) sample points
            lab_path = self.context.bika_setup.bika_samplepoints.getPhysicalPath()
            lab_items = list(
                bsc(portal_type = "SamplePoint",
                    path = {"query": "/".join(lab_path), "level" : 0 },
                    inactive_state = 'active',
                    sort_on='sortable_title'))

            client_items = [callable(s.Title) and s.Title() or s.Title
                     for s in self.filter_list(client_items, term)]
            lab_items = [callable(s.Title) and s.Title() or s.Title
                     for s in self.filter_list(lab_items, term)]
            lab_items = ["%s: %s" % (_("Lab"), i) for i in lab_items]

            items = client_items + lab_items

        return json.dumps(items)
