from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IReferenceDefinitions
from zope.interface.declarations import implements
from operator import itemgetter

class ReferenceDefinitionsView(BikaListingView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ReferenceDefinitionsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ReferenceDefinition',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Reference Definition'):
                                    "createObject?type_name=ReferenceDefinition"}
        self.title = _("Reference Definitions")
        self.description = _("ReferenceDefinition represents a Reference Definition "
                             "or sample type used for quality control testing")
        self.show_editable_border = False
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Title')},
            'Description': {'title': _('Description')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title', 'Description']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title', 'Description']},
            {'title': _('Inactive'), 'id':'inactive',
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

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous_small.png' title='Hazardous'>"
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['Title'], after_icons)

        return items

schema = ATFolderSchema.copy()
class ReferenceDefinitions(ATFolder):
    implements(IReferenceDefinitions)
    schema = schema
    displayContentsTab = False

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ReferenceDefinitions, PROJECTNAME)
