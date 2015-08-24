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
from bika.lims.utils import isnumber

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
        self.pagesize = 999999
        self.allow_edit = allow_edit
        self.show_categories = True
        # self.expand_all_categories = False

        self.specsresults = {}
        for specresults in fieldvalue:
            self.specsresults[specresults['keyword']] = specresults

        self.columns = {
            'service': {'title': _('Service'), 'index': 'sortable_title', 'sortable': False},
            'min': {'title': _('Min'), 'sortable': False,},
            'max': {'title': _('Max'), 'sortable': False,},
            'error': {'title': _('Permitted Error %'), 'sortable': False},
            'hidemin': {'title': _('< Min'), 'sortable': False},
            'hidemax': {'title': _('> Max'), 'sortable': False},
            'rangecomment': {'title': _('Range comment'), 'sortable': False, 'toggle': False}
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns': ['service', 'min', 'max', 'error',
                         'hidemin', 'hidemax', 'rangecomment'],
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
                        'error': '',
                        'hidemin': '',
                        'hidemax': '',
                        'rangecomment': ''}

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
                'error': specresults.get('error', ''),
                'min': specresults.get('min', ''),
                'max': specresults.get('max', ''),
                'hidemin': specresults.get('hidemin',''),
                'hidemax': specresults.get('hidemax',''),
                'rangecomment': specresults.get('rangecomment', ''),
                'replace': {},
                'before': {},
                'after': {'service':after_icons,
                          'min':unitspan,
                          'max':unitspan,
                          'error': percspan},
                'choices':{},
                'class': "state-%s" % (state),
                'state_class': "state-%s" % (state),
                'allow_edit': ['min', 'max', 'error', 'hidemin', 'hidemax',
                               'rangecomment'],
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
            consumption. If neither hidemin nor hidemax are specified, only
            services which have float()able entries in result,min and max field
            will be included. If hidemin and/or hidemax specified, results
            might contain empty min and/or max fields.
        """
        value = []
        if 'service' in form:
            for uid, keyword in form['keyword'][0].items():

                hidemin = form['hidemin'][0].get(uid, '') if 'hidemin' in form else ''
                hidemax = form['hidemax'][0].get(uid, '') if 'hidemax' in form else ''
                mins = form['min'][0].get(uid, '') if 'min' in form else ''
                maxs = form['max'][0].get(uid, '') if 'max' in form else ''
                err = form['error'][0].get(uid, '') if 'error' in form else ''
                rangecomment = form['rangecomment'][0].get(uid, '') if 'rangecomment' in form else ''

                if not isnumber(hidemin) and not isnumber(hidemax) and \
                   (not isnumber(mins) or not isnumber(maxs)):
                    # If neither hidemin nor hidemax have been specified,
                    # min and max values are mandatory.
                    continue

                value.append({'keyword': keyword,
                              'uid': uid,
                              'min': mins if isnumber(mins) else '',
                              'max': maxs if isnumber(maxs) else '',
                              'hidemin': hidemin if isnumber(hidemin) else '',
                              'hidemax': hidemax if isnumber(hidemax) else '',
                              'error': err if isnumber(err) else '0',
                              'rangecomment': rangecomment})
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
