# coding=utf-8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.utils import getToolByName


class ServicesView(BikaListingView):
    """ This table displays a list of services for the adding controls / blanks.
        Services which have analyses in this worksheet are selected, and their
        categories are expanded by default
    """
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'review_state':'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.context.absolute_url()
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 999999
        self.show_workflow_action_buttons = False
        self.show_categories=context.bika_setup.getCategoriseAnalysisServices()
        self.expand_all_categories=True

        self.columns = {
            'Service': {'title': _('Service'),
                        'sortable': False},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [],
             'columns':['Service'],
            },
        ]

    def folderitems(self):
        ws_services = []
        for analysis in self.context.getAnalyses():
            service_uid = analysis.getService().UID()
            if service_uid not in ws_services:
                ws_services.append(service_uid)
        self.categories = []
        catalog = getToolByName(self, self.catalog)
        services = catalog(portal_type = "AnalysisService",
                           inactive_state = "active",
                           sort_on = 'sortable_title')
        items = []
        for service in services:
            # if the service has dependencies, it can't have reference analyses
            calculation = service.getObject().getCalculation()
            if calculation and calculation.getDependentServices():
                continue
            cat = service.getCategoryTitle
            if cat not in self.categories:
                self.categories.append(cat)
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': service,
                'id': service.id,
                'uid': service.UID,
                'title': service.Title,
                'category': cat,
                'selected': service.UID in ws_services,
                'type_class': 'contenttype-AnalysisService',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'Service': service.Title,
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
                'required': [],
            }
            items.append(item)

        self.categories.sort(lambda x, y: cmp(x.lower(), y.lower()))

        return items
