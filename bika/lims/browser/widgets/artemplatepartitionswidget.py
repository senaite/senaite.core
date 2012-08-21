# ../../skins/bika/bika_widgets/artemplatepartitionswidget.pt
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from operator import itemgetter
import json

class ARTemplatePartitionsView(BikaListingView):
    """ bika listing to display Partition table for an ARTemplate.
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'review_state': 'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = False
        self.pagesize = 1000
        self.allow_edit = allow_edit
        self.form_id = "partitions"

        self.columns = {
            'part_id': {'title': _('Partition'),
                        'sortable': False,},
            'container_uid': {'title': _('Container'),
                              'sortable': False,},
            'preservation_uid': {'title': _('Preservation'),
                                 'sortable': False,},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [{'id':'empty'}], # none
             'columns':['part_id', 'container_uid', 'preservation_uid'],
            },
        ]

        self.fieldvalue = fieldvalue

    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        containers = [({'ResultValue':o.UID, 'ResultText':o.title})
                      for o in bsc(portal_type="Container",
                                   inactive_state="active")]
        preservations = [({'ResultValue':o.UID, 'ResultText':o.title})
                         for o in bsc(portal_type="Preservation",
                                      inactive_state="active")]
        items = []
        for part in self.fieldvalue:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                # it's a template, there is no 'object', 'uid' etc.
                # so things get a little frayed over here.
                'obj': part,
                'uid': part['part_id'],
                'id': part['part_id'],
                'part_id': part['part_id'],
                'container_uid': part['container_uid'],
                'preservation_uid': part['preservation_uid'],
                'type_class': 'contenttype-ARTemplate',
                'url': self.context.absolute_url(),
                'relative_url': self.context.absolute_url(),
                'view_url': self.context.absolute_url(),
                'result': '',
                'error': '',
                'replace': {},
                'before': {},
                'after': {},
                'choices':{'container_uid':containers,
                           'preservation_uid':preservations},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': ['container_uid', 'preservation_uid'],
            }

            items.append(item)
        items = sorted(items, key = itemgetter('part_id'))
        return items

class ARTemplatePartitionsWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/artemplatepartitionswidget",
        'helper_js': ("bika_widgets/artemplatepartitionswidget.js",),
        'helper_css': ("bika_widgets/artemplatepartitionswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for ARTemplate/Partitions field
            consumption.
        """
        value = []
        if 'part_id' in form:
            for part_id in form['part_id'][0].keys():
                value.append({
                    'part_id': part_id,
                    'preservation_uid': form['preservation_uid'][0][part_id],
                    'container_uid': form['container_uid'][0][part_id],
                })
        if value:
            return value, {}

    security.declarePublic('Partitions')
    def Partitions(self, field, allow_edit = False):
        """ Print partitions table
        """
        fieldvalue = getattr(field, field.accessor)()
        view = ARTemplatePartitionsView(self,
                                        self.REQUEST,
                                        fieldvalue = fieldvalue,
                                        allow_edit = allow_edit)
        return view.contents_table(table_only = True)

registerWidget(ARTemplatePartitionsWidget,
               title = 'AR Template Partition Layout',
               description = ('AR Template Partition Layout'),
               )
