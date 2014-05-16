from AccessControl import ClassSecurityInfo
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales
from zope.interface import implements

class ARAddAnalysesView(BikaListingView):
    """ bika listing to display Analyses table for AR Add.
    """
    template = ViewPageTemplateFile("templates/add_analyses.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(ARAddAnalysesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active',}
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.pagesize = 1000
        self.allow_edit = False
        self.show_categories = True
        self.expand_all_categories = False
        self.form_id = "analyses"

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
            'Partition': {'title': _('Partition'),
                          'sortable': False,},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Price',
                         'Partition',
                         ],
             'transitions': [],
             'custom_actions': [
                 {'id': 'save_analyses_button',
                  'title': _('Save analyses'),
                  'url': ''},
              ],
             },
        ]

        self.fieldvalue = [] #fieldvalue
        self.selected = [] #[x['service_uid'] for x in fieldvalue]

    def __call__(self):
        """ return analyses table
        """
        return self.contents_table(table_only = False)

    def folderitems(self):
        self.categories = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        items = BikaListingView.folderitems(self)

        part_ids = ['part-1']
        for s in self.fieldvalue:
            if s['partition'] not in part_ids:
                part_ids.append(s['partition'])
        partitions = [{'ResultValue':p, 'ResultText':p} for p in part_ids]

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            analyses = dict([(a['service_uid'], a)
                             for a in self.fieldvalue])

            items[x]['selected'] = items[x]['uid'] in analyses.keys()

            items[x]['class']['Title'] = 'service_title'

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['Price'] = "%s %s" % (symbol, obj.getPrice())
            items[x]['class']['Price'] = 'nowrap'
            items[x]['allow_edit'] = ['Partition']
            if not items[x]['selected']:
                items[x]['edit_condition'] = {'Partition':False}

            items[x]['required'].append('Partition')
            items[x]['choices']['Partition'] = partitions

            if obj.UID() in self.selected:
                items[x]['Partition'] = analyses[obj.UID()]['partition']
            else:
                items[x]['Partition'] = ''

            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Accredited"))
            if obj.getReportDryMatter():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/dry.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Can be reported as dry matter"))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Attachment required"))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _('Attachment not permitted'))
            if after_icons:
                items[x]['after']['Title'] = after_icons
        self.categories.sort()
        return items

