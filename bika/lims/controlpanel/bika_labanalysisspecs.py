from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import ILabAnalysisSpecs
from zope.interface.declarations import implements

#XXX multiple additions in one add_form.

class LabAnalysisSpecsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabAnalysisSpec'}
    content_add_actions = {_('Analysis Specification'): "createObject?type_name=LabAnalysisSpec"}
    title = _("Analysis Specs")
    description = _("Set up the laboratory analysis service results specifications")
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
               'getSampleType': {'title': _('Sample Type')},
              }
    review_states = [
                     {'title': _('All'), 'id':'all',
                      'columns': ['getSampleType'],
                      'buttons':[{'cssclass': 'context',
                                  'title': _('Delete'),
                                  'url': 'folder_delete:method'},
                                 {'cssclass':'context',
                                  'title': _('Duplicate'),
                                  'url': 'duplicate_labanalysisspec:method',
                                 }
                                ],
                     },
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['getSampleType'] = obj.getSampleType() and obj.getSampleType().Title()
            items[x]['links'] = {'getSampleType': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class LabAnalysisSpecs(ATFolder):
    implements(ILabAnalysisSpecs)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabAnalysisSpecs, PROJECTNAME)
