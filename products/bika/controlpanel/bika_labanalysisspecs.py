from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import ILabAnalysisSpecs
from zope.interface.declarations import implements

#XXX multiple additions in one add_form.

class LabAnalysisSpecsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabAnalysisSpec'}
    content_add_buttons = {'Analysis Specification': "createObject?type_name=LabAnalysisSpec"}
    title = "Analysis Specs"
    description = "Set up the laboratory analysis service results specifications"
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'SampleType': {'title': 'SampleType'},
              }
    wflist_states = [
                     {'title': 'All', 'id':'all',
                      'columns': ['SampleType'],
                      'buttons':[BikaFolderContentsView.default_buttons['delete'],
                                 {'cssclass':'context',
                                  'title': 'Duplicate',
                                  'url': 'duplicate_labanalysisspec:method', # XXX Duplicate LabAnalysisSpec
                                 }
                                ],
                     },
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()

            st = obj.getSampleType()
            if st: items[x]['SampleType'] = st.Title()
            else: items[x]['SampleType'] = "None"

            items[x]['links'] = {'SampleType': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class LabAnalysisSpecs(ATFolder):
    implements(ILabAnalysisSpecs)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabAnalysisSpecs, PROJECTNAME)
