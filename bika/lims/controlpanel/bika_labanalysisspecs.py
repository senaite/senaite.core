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

#XXX multiple additions in one add_form.

class AnalysisSpecsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisSpec'}
    content_add_actions = {_('Analysis Specification'): "createObject?type_name=AnalysisSpec"}
    title = _("Analysis Specs")
    description = _("Set up the laboratory analysis service results specifications")
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'getSampleType': {'title': _('Sample Type')},
              }
    review_states = [
                     {'title': _('All'), 'id':'all',
                      'columns': ['getSampleType'],
                     },
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['getSampleType'] = obj.getSampleType() and obj.getSampleType().Title()
            items[x]['links'] = {'getSampleType': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class AnalysisSpecs(ATFolder):
    implements(IAnalysisSpecs)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisSpecs, PROJECTNAME)
