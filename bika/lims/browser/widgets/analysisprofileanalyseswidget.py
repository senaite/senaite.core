# ../../skins/bika/bika_widgets/analysisprofileanalyseswidget.pt
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from zope.i18n.locales import locales
from operator import itemgetter
import json

class AnalysisProfileAnalysesView(BikaListingView):
    """ bika listing to display Analyses table for an Analysis Profile.
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        super(AnalysisProfileAnalysesView, self).__init__(context, request)
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
        self.show_categories = True
        self.expand_all_categories = True
        self.pagesize = 999999
        self.allow_edit = allow_edit
        self.form_id = "analyses"
        self.profile = None

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Price',
                         ],
             'transitions': [{'id':'empty'}, ], # none
             },
        ]

        self.fieldvalue = fieldvalue
        self.selected = [x.UID() for x in fieldvalue]

        if self.aq_parent.portal_type == 'AnalysisProfile':
            # Custom settings for the Analysis Services assigned to
            # the Analysis Profile
            # https://jira.bikalabs.com/browse/LIMS-1324
            self.profile = self.aq_parent
            self.columns['Hidden'] = {'title': _('Hidden'),
                                      'sortable': False,
                                      'type': 'boolean'}
            self.review_states[0]['columns'].insert(1, 'Hidden')


    def folderitems(self):
        self.categories = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            analyses = [a.UID() for a in self.fieldvalue]

            items[x]['selected'] = items[x]['uid'] in analyses

            items[x]['class']['Title'] = 'service_title'

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['Price'] = "%s %s" % (symbol, obj.getPrice())
            items[x]['class']['Price'] = 'nowrap'

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

            if self.profile:
                # Display analyses for this Analysis Service in results?
                ser = self.profile.getAnalysisServiceSettings(obj.UID())
                items[x]['allow_edit'] = ['Hidden', ]
                items[x]['Hidden'] = ser.get('hidden', obj.getHidden())

        self.categories.sort()
        return items

class AnalysisProfileAnalysesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisprofileanalyseswidget",
        'helper_js': ("bika_widgets/analysisprofileanalyseswidget.js",),
        'helper_css': ("bika_widgets/analysisprofileanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for AnalysisProfile/Analyses field
            consumption.
        """
        bsc = getToolByName(instance, 'bika_setup_catalog')
        value = []
        service_uids = form.get('uids', None)

        if instance.portal_type == 'AnalysisProfile':
            # Hidden analyses?
            outs = []
            hiddenans = form.get('Hidden', {})
            if service_uids:
                for uid in service_uids:
                    hidden = hiddenans.get(uid, '')
                    hidden = True if hidden == 'on' else False
                    outs.append({'uid':uid, 'hidden':hidden})
            instance.setAnalysisServicesSettings(outs)

        return service_uids, {}

    security.declarePublic('Analyses')
    def Analyses(self, field, allow_edit = False):
        """ Print analyses table
        """
        fieldvalue = getattr(field, field.accessor)()
        view = AnalysisProfileAnalysesView(self,
                                      self.REQUEST,
                                      fieldvalue = fieldvalue,
                                      allow_edit = allow_edit)
        return view.contents_table(table_only = True)

registerWidget(AnalysisProfileAnalysesWidget,
               title = 'Analysis Profile Analyses selector',
               description = ('Analysis Profile Analyses selector'),
               )
