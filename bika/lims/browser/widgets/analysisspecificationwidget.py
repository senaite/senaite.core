from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from zope.i18n.locales import locales
from operator import itemgetter
import json

class AnalysisSpecificationView(BikaListingView):
    """ bika listing to display Analysis Services (AS) table for an
        Analysis Specification.
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'review_state' : 'impossible_state'}
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 1000
        self.allow_edit = allow_edit

        self.specsresults = {}
        for specresults in fieldvalue:
            self.specsresults[specresults['keyword']] = specresults

        self.columns = {
            'service': {'title': _('Service'), 'index': 'sortable_title', 'sortable': False},
            'min': {'title': _('Min'), 'sortable': False,},
            'max': {'title': _('Max'), 'sortable': False,},
            'error': {'title': _('Permitted Error %'), 'sortable': False},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns': ['service', 'min', 'max', 'error'],
             },
        ]


    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.categories = []

        # Check edition permissions
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        # Analysis Services retrieval and custom item creation
        items = []
        workflow = getToolByName(self.context, 'portal_workflow')
        services = bsc(portal_type = "AnalysisService",
                       sort_on = "sortable_title")
        for service in services:
            service = service.getObject();
            cat = service.getCategoryTitle()
            if cat not in self.categories:
                self.categories.append(cat)
            if service.getKeyword() in self.specsresults:
                specresults = self.specsresults[service.getKeyword()]
            else:
                specresults = {'keyword': service.getKeyword(),
                        'min': '',
                        'max': '',
                        'error': ''}

            after_icons = ' <span class="discreet">(%s)</span>&nbsp;&nbsp;' % service.getKeyword()
            if service.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Accredited"))
            if service.getReportDryMatter():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/dry.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Can be reported as dry matter"))
            if service.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Attachment required"))
            if service.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _('Attachment not permitted'))

            # TRICK for AS keyword retrieval on form POST
            after_icons += '<input type="hidden" name="keyword.%s:records"\
            value="%s"></input>' % (service.UID(), service.getKeyword())

            state = workflow.getInfoFor(service, 'inactive_state', '')
            unit = service.getUnit()
            unitspan = unit and \
                "<span class='discreet'>%s</span>" % service.getUnit() or ''
            percspan = "<span class='discreet'>%</span>";

            item = {
                'obj': service,
                'id': service.getId(),
                'uid': service.UID(),
                'keyword': service.getKeyword(),
                'title': service.Title(),
                'category': cat,
                'selected': service.getKeyword() in self.specsresults.keys(),
                'type_class': 'contenttype-ReferenceResult',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'service': service.Title(),
                'error': specresults['error'],
                'min': specresults['min'],
                'max': specresults['max'],
                'replace': {},
                'before': {},
                'after': {'service':after_icons,
                          'min':unitspan,
                          'max':unitspan,
                          'error': percspan},
                'choices':{},
                'class': "state-%s" % (state),
                'state_class': "state-%s" % (state),
                'allow_edit': ['min', 'max', 'error'],
            }
            items.append(item)

        self.categories.sort()
        for i in range(len(items)):
            items[i]['table_row_class'] = "even"

        return items

class AnalysisSpecificationWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisspecificationwidget",
        #'helper_js': ("bika_widgets/analysisspecificationwidget.js",),
        #'helper_css': ("bika_widgets/analysisspecificationwidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None, emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for AnalysisSpecsResultsField
            consumption.  Only services which have float()able entries in
            result,min and max field will be included.
        """
        value = []
        if 'service' in form:
            for uid, keyword in form['keyword'][0].items():
                try:
                    float(form['min'][0][uid])
                    float(form['max'][0][uid])
                except:
                    continue
                value.append({'keyword':keyword,
                              'uid':uid,
                              'min':form['min'][0][uid],
                              'max':form['max'][0][uid],
                              'error':form['error'][0][uid]})
        return value, {}

    security.declarePublic('AnalysisSpecificationResults')
    def AnalysisSpecificationResults(self, field, allow_edit = False):
        """ Prints a bika listing with categorized services.
            field contains the archetypes field with a list of services in it
        """
        fieldvalue = getattr(field, field.accessor)()
        view = AnalysisSpecificationView(self,
                                            self.REQUEST,
                                            fieldvalue = fieldvalue,
                                            allow_edit = allow_edit)
        return view.contents_table(table_only = True)

registerWidget(AnalysisSpecificationWidget,
               title = 'Analysis Specification Results',
               description = ('Analysis Specification Results'))
