from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import ManageBika
from types import StringType
from zope.site.hooks import getSite

class ServicesView(BikaListingView):
    """ bika listing to display a list of services.
    field must be a <reference field> containing <AnalysisService> objects.
    """
    def __init__(self, context, request, field=None, category=None):
        BikaListingView.__init__(self, context, request)
        if field:
            self.selected = [o.UID() for o in getattr(field, field.accessor)()]
        else:
            self.selected = []
        self.category = category if category else None
        self.context_actions = {}
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'review_state': 'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 999999
        self.form_id = 'serviceswidget'

        self.show_categories = False
        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = 'getCategoryTitle'
            self.ajax_categories_url = context.absolute_url() + \
                                       "/ajax_services_expand_category"

        self.columns = {
            'Service': {'title': _('Service')},
            'Keyword': {'title': _('Keyword'),
                        'index': 'getKeyword'},
            'Method': {'title': _('Method')},
            'Calculation': {'title': _('Calculation')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['Service',
                        'Keyword',
                        'Method',
                        'Calculation', ]
            },
        ]

    def folderitems(self):
        checkPermission = self.context.portal_membership.checkPermission
        catalog = getToolByName(self.context, self.catalog)
        contentFilter = {'portal_type': 'AnalysisService',
                         'inactive_state': 'active',
                         'sort_on': 'sortable_title'}
        if self.ajax_categories and self.category:
             contentFilter[self.category_index] = self.category
        services = catalog(contentFilter)
        items = []
        for service in services:
            service = service.getObject()
            cat = service.getCategoryTitle()
            if cat not in self.categories:
                self.categories.append(cat)
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            service_title = service.Title()
            calculation = service.getCalculation()
            method = service.getMethod()

            item = {
                'obj': service,
                'Keyword': service.getKeyword(),
                'Method': method and method.Title() or '',
                'Calculation': calculation and calculation.Title() or '',
                'id': service.getId(),
                'uid': service.UID(),
                'title': service_title,
                'category': cat,
                'selected': service.UID() in self.selected,
                'type_class': 'contenttype-AnalysisService',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'Service': service_title,
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
                'required': [],
            }
            if checkPermission(ManageBika, service):
                item['replace']['Service'] = "<a href='%s'>%s</a>" % \
                    (service.absolute_url(), service_title)
            else:
                item['replace']['Service'] = "<span class='service_title'>%s</span>" % \
                    service_title
            items.append(item)


        self.categories.sort()

        return items

class ServicesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/serviceswidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic('getServices')
    def Services(self, field, show_select_column=True):
        """ Prints a bika listing with categorized services.
            field contains the archetypes field with a list of services in it
        """
        services = ServicesView(self, self.REQUEST, field)
        services.show_select_column = show_select_column
        return services.contents_table(table_only=True)

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        service_uids = form.get('uids', [])
        return service_uids, {}


registerWidget(ServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               )

class AJAXCategoryExpand(BrowserView):

    def __call__(self):
        if 'ajax_category_expand' in self.request.keys():
            cat = self.request.get('cat')
            asv = ServicesView(self.context, self.request, category=cat)
            return asv.rendered_items()
