from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IAnalysisServices
from bika.lims.idserver import renameAfterCreation
from zope.interface.declarations import implements
from operator import itemgetter
import plone.protect

class AnalysisServicesWorkflowAction(WorkflowAction):
    """ Workflow actions taken in Analysis Services page
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        uc = getToolByName(self.context, 'uid_catalog')
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == 'duplicate':
            selected_services = WorkflowAction._get_selected_items(self)

            ## Create a copy of the selected services
            folder = self.context.bika_setup.bika_analysisservices
            created = []
            for service in selected_services.values():
                _id = folder.invokeFactory('AnalysisService', id = 'tmp')
                folder[_id].setTitle('%s (copy)' % service.Title())
                _id = renameAfterCreation(folder[_id])
                folder[_id].unmarkCreationFlag()

                folder[_id].edit(
                    Accredited = service.getAccredited(),
                    AttachmentOption = service.getAttachmentOption(),
                    BulkPrice = service.getBulkPrice(),
                    Calculation = service.getCalculation(),
                    Category = service.getCategory(),
                    Container = service.getContainer(),
                    Department = service.getDepartment(),
                    description = service.Description(),
                    DuplicateVariation = service.getDuplicateVariation(),
                    Instrument = service.getInstrument(),
                    InterimFields = service.getInterimFields(),
                    MaxTimeAllowed = service.getMaxTimeAllowed(),
                    Method = service.getMethod(),
                    PartitionSetup = service.getPartitionSetup(),
                    PointOfCapture = service.getPointOfCapture(),
                    Precision = service.getPrecision(),
                    Preservation = service.getPreservation(),
                    Price = service.getPrice(),
                    ReportDryMatter = service.getReportDryMatter(),
                    ResultOptions = service.getResultOptions(),
                    Separate = service.getSeparate(),
                    Uncertainties = service.getUncertainties(),
                    Unit = service.getUnit(),
                    VAT = service.getVAT(),
                )
                folder[_id].reindexObject()
                created.append(_id)

            if len(created) > 1:
                message = self.context.translate(
                    _('Services ${services} were successfully created.',
                      mapping = {'services': ', '.join(created)}))
                self.destination_url = \
                    self.request.get_header("referer",
                                            self.context.absolute_url())
            else:
                message = self.context.translate(
                    _('Analysis request ${service} was successfully created.',
                    mapping = {'service': ', '.join(created)}))
                self.destination_url = folder[_id].absolute_url() + "/base_edit"

            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.destination_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


class AnalysisServicesView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        """
        """

        super(AnalysisServicesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url':'createObject?type_name=AnalysisService',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisservice_big.png"
        self.title = _("Analysis Services")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25

        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.pagesize = 1000 # hide batching controls
            self.show_categories=True,
            self.expand_all_categories=False

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title'},
            'Keyword': {'title': _('Keyword'),
                        'index': 'getKeyword'},
            'Category': {'title': _('Category')},
            'Method': {'title': _('Method'),
                       'toggle': False},
            'Department': {'title': _('Department'),
                           'toggle': False},
            'Instrument': {'title': _('Instrument')},
            'Unit': {'title': _('Unit')},
            'Price': {'title': _('Price')},
            'MaxTimeAllowed': {'title': _('Max Time'),
                               'toggle': False},
            'DuplicateVariation': {'title': _('Dup Var'),
                                   'toggle': False},
            'Calculation': {'title': _('Calculation')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Method',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions':[{'id': 'duplicate', 'title': _('Duplicate')}, ]
             },
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Method',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions':[{'id': 'duplicate', 'title': _('Duplicate')}, ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Keyword',
                         'Category',
                         'Method',
                         'Department',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions':[{'id': 'duplicate', 'title': _('Duplicate')}, ]
             },
        ]

    def folderitems(self):

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Keyword'] = obj.getKeyword()
            cat = obj.getCategoryTitle()
            items[x]['Category'] = cat # Category is for display column value
            if self.do_cats:
                items[x]['category'] = cat # category is for bika_listing to groups entries
                if cat not in self.categories:
                    self.categories.append(cat)

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

            instrument = obj.getInstrument()
            items[x]['Instrument'] = instrument and instrument.Title() or ''
            items[x]['replace']['Instrument'] = instrument and "<a href='%s'>%s</a>" % \
                 (instrument.absolute_url() + "/edit", instrument.Title()) or ''

            items[x]['Department'] = obj.getDepartment() and obj.getDepartment().Title() or ''

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()
            items[x]['replace']['Calculation'] = calculation and "<a href='%s'>%s</a>" % \
                 (calculation.absolute_url() + "/edit", calculation.Title()) or ''

            items[x]['Unit'] = obj.getUnit() and obj.getUnit() or ''
            items[x]['Price'] = "%s.%02d" % (obj.Price)

            method = obj.getMethod()
            items[x]['Method'] = method and method.Title() or ''
            items[x]['replace']['Method'] = method and "<a href='%s'>%s</a>" % \
                 (method.absolute_url(), method.Title()) or ''

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

        self.categories.sort()
        return items

schema = ATFolderSchema.copy()
class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisServices, PROJECTNAME)
