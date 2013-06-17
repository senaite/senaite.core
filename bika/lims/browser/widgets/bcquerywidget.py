from AccessControl import ClassSecurityInfo
from archetypes.querywidget.widget import QueryWidget as _QueryWidget
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from Products.Archetypes.Registry import registerWidget
from zope.component import getMultiAdapter
from zope.component import getUtility


class BCQueryWidget(_QueryWidget):

    _properties = _QueryWidget._properties.copy()
    _properties.update({
        'macro': 'querywidget',
        'helper_css': ('++resource++archetypes.querywidget.querywidget.css',),
        'helper_js': ('++resource++bika.lims.js/querywidget.js',
                      '@@datepickerconfig'),
        'catalog_name': 'bika_catalog',
        'registry_prefix': '',
    })

    security = ClassSecurityInfo()

    def getConfig(self):
        """get the config"""
        registry = getUtility(IRegistry)
        prefix = self.registry_prefix
        if prefix:
            # First grab the base config's operations
            registryreader = IQuerystringRegistryReader(registry)
            registryreader.prefix = "plone.app.querystring.operation"
            plone_config = registryreader.parseRegistry()
            # then merge custom fields
            registryreader = IQuerystringRegistryReader(registry)
            registryreader.prefix = prefix
            config = registryreader.parseRegistry()
            config = registryreader.getVocabularyValues(config)
            config.update(plone_config)
            config = registryreader.mapOperations(config)
            config = registryreader.mapSortableIndexes(config)
            config = {
                'indexes': config.get(prefix + '.field'),
                'sortable_indexes': config.get('sortable'),
            }
        else:
            # First grab the base config's operations
            registryreader = IQuerystringRegistryReader(registry)
            registryreader.prefix = "plone.app.querystring"
            config = registryreader()

        # Group indices by "group", order alphabetically
        groupedIndexes = {}
        for indexName in config['indexes']:
            index = config['indexes'][indexName]
            if index['enabled']:
                group = index['group']
                if group not in groupedIndexes:
                    groupedIndexes[group] = []
                groupedIndexes[group].append((index['title'], indexName))

        # Sort each index list
        [a.sort() for a in groupedIndexes.values()]

        config['groupedIndexes'] = groupedIndexes
        return config

    def SearchResults(self, request, context, accessor):
        """search results"""

        options = dict(original_context=context)
        res = getMultiAdapter((accessor(), request),
                              name='display_query_results')
        return res(**options)

registerWidget(BCQueryWidget, title='Query',
               description=('Field for storing a query'))
