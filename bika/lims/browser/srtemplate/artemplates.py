from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName


class AnalysisRequestTemplatesView(BikaListingView):
    """ BIKA listing to display ARTemplates for an SRTemplate.
    """

    def __init__(self, context, request):
        super(AnalysisRequestTemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
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
        self.pagesize = 50
        self.title = self.context.translate(_("AR Templates"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/artemplate_big.png"
        self.form_id = "artemplates"
        self.columns = {
            'title': {
                'title': _('AR Template Title'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'SamplePoint': {
                'title': _('Sample Point'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'SampleType': {
                'title': _('Sample Type'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'Composite': {
                'title': _('Composite Y/N'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'ContainerTitle': {
                'title': _('Container Title'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'ContainerVolume': {
                'title': _('Container Volume'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'Preservation': {
                'title': _('Preservation'),
                'index': 'sortable_title',
                'sortable': True,
            },
            'Sampler': {
                'title': _('Sampler'),
                'sortable': True,
            },
            'PreparationMethod': {
                'title': _('Preservation Method'),
                'index': 'sortable_title',
                'sortable': True,
            },
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title',
                         'SamplePoint',
                         'SampleType',
                         'Composite',
                         'ContainerTitle',
                         'ContainerVolume',
                         'Preservation',
                         #'Sampler',
                         'PreparationMethod']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title',
                         'SamplePoint',
                         'SampleType',
                         'Composite',
                         'ContainerTitle',
                         'ContainerVolume',
                         'Preservation',
                         #'Sampler',
                         'PreparationMethod']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title',
                         'SamplePoint',
                         'SampleType',
                         'Composite',
                         'ContainerTitle',
                         'ContainerVolume',
                         'Preservation',
                         #'Sampler',
                         'PreparationMethod']},
        ]

    def contentsMethod(self, contentFilter):
        return self.context.getARTemplates()

    def _buildFromPerPartition(self, item, partition):
        """
        This function will get the partition info and then it'll write the container and preservation data
        to the dictionary 'item'
        :param item: a dict which contains the ARTeplate data columns
        :param partition: a dict with some partition info
        :return: the item dict with the partition's data
        """
        uc = getToolByName(self, 'uid_catalog')
        container = uc(UID=partition.get('container_uid', ''))
        preservation = uc(UID=partition.get('preservation_uid', ''))
        if container:
            container = container[0].getObject()
            item['ContainerTitle'] = container.title
            item['replace']['ContainerTitle'] = "<a href='%s'>%s</a>" % \
                                                (container.absolute_url(), item['ContainerTitle'])
            item['ContainerVolume'] = container.getCapacity()
        else:
            item['ContainerTitle'] = ''
            item['ContainerVolume'] = ''
        if preservation:
            preservation = preservation[0].getObject()
            item['Preservation'] = preservation.title
            item['replace']['Preservation'] = "<a href='%s'>%s</a>" % \
                                              (preservation.absolute_url(), item['Preservation'])
        else:
            item['Preservation'] = ''
        item['PreparationMethod'] = ''
        return item

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        new_items = []
        for item in items:
            if not item.has_key('obj'): continue
            obj = item['obj']
            # Updating some ARTemplate columns
            title_link = "<a href='%s'>%s</a>" % (item['url'], item['title'])
            item['replace']['title'] = title_link
            if obj.getSamplePoint():
                item['SamplePoint'] = obj.getSamplePoint().title
                item['replace']['SamplePoint'] = "<a href='%s'>%s</a>" % \
                    (obj.getSamplePoint().absolute_url(), item['SamplePoint'])
            else:
                item['SamplePoint'] = ''
            if obj.getSamplePoint():
                item['SamplePoint'] = obj.getSamplePoint().title
                item['replace']['SamplePoint'] = "<a href='%s'>%s</a>" % \
                    (obj.getSamplePoint().absolute_url(), item['SamplePoint'])
            else:
                item['SamplePoint'] = ''
            if obj.getSampleType():
                item['SampleType'] = obj.getSampleType().title
                item['replace']['SampleType'] = "<a href='%s'>%s</a>" % \
                    (obj.getSampleType().absolute_url(), item['SampleType'])
            else:
                item['SampleType'] = ''
            item['Composite'] = obj.getComposite()
            img_url = '<img src="'+self.portal_url+'/++resource++bika.lims.images/ok.png"/>'
            item['replace']['Composite'] = img_url if obj.getComposite() else ' '

            partitions = obj.getPartitions()
            for partition in partitions:
                c_item = item.copy()
                # We ave to make a copy of 'replace' because it's a reference to a dict object
                c_item['replace'] = item['replace'].copy()
                # Adding the partition info
                c_item = self._buildFromPerPartition(c_item, partition)
                # Adding the ARTemplate item to the future list to display
                new_items.append(c_item)
        return new_items
