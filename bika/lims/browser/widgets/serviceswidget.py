from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from bika.lims.browser.bika_listing import BikaListingView
from Products.Archetypes.Widget import TypesWidget
from bika.lims import bikaMessageFactory as _
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName

from archetypes.referencebrowserwidget import utils
from bika.lims.config import POINTS_OF_CAPTURE
from types import StringType
from zope.site.hooks import getSite

class ServicesView(BikaListingView):
    """ bika listing to display a list of services.
    field must be a <reference field> containing <AnalysisService> objects.
    """
    def __init__(self, context, request, field):
        BikaListingView.__init__(self, context, request)
        self.selected = [o.UID() for o in getattr(field, field.accessor)()]
        self.content_add_actions = {}
        self.contentFilter = {'review_state': 'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 1000

        self.columns = {
            'Service': {'title': _('Service')},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': [],
             'columns':['Service'],
            },
        ]

    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.categories = []
        services = bsc(portal_type = 'AnalysisService',
                       inactive_state = 'active',
                       sort_on = 'sortable_title')
        items = []
        for service in services:
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
                'selected': service.UID in self.selected,
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
            }
            items.append(item)

        self.categories.sort()

        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "draggable even" or "draggable odd"

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
        services.select_checkbox_name = field.getName()
        return services.contents_table(table_only=True)

registerWidget(ServicesWidget,
               title = 'Analysis Services',
               description = ('Categorised AnalysisService selector.'),
               )

#registerPropertyType('default_search_index', 'string', ServicesWidget)
