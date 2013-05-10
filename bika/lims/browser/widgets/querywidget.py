from AccessControl import ClassSecurityInfo
from archetypes.querywidget.views import WidgetTraverse as _WidgetTraverse
from archetypes.querywidget.widget import QueryWidget as _QueryWidget
from bika.lims.querystring.querybuilder import QueryBuilder
from bika.lims.querystring.querybuilder import RegistryConfiguration
from archetypes.querywidget.views import \
    MultiSelectWidget as _MultiSelectWidget
from bika.lims.querystring.registryreader import QuerystringRegistryReader
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.permissions import ModifyPortalContent, View
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

_p = MessageFactory('plone')


class QueryWidget(_QueryWidget):

    _properties = _QueryWidget._properties.copy()
    _properties.update({
        'macro': 'bika_widgets/querywidget',
        'helper_css': ('++resource++archetypes.querywidget.querywidget.css',),
        'helper_js': ('++resource++bika.lims.js/querywidget.js',
                      '@@datepickerconfig'),
        'catalog_name': 'portal_catalog',
        'registry_prefix': None,
    })

    security = ClassSecurityInfo()

    def getConfig(self):
        """get the config"""
        registry = getUtility(IRegistry)
        prefix = self.registry_prefix
        if prefix is not None:
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

registerWidget(QueryWidget, title='Query',
               description=('Field for storing a query'))


class WidgetTraverse(_WidgetTraverse):

    def getConfig(self):
        """get the config"""
        registry = getUtility(IRegistry)
        # First grab the base config, so we can use the operations
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "plone.app.querystring.operation"
        op_config = registryreader.parseRegistry()
        # Then combine our fields
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "bika.lims.bika_catalog_query"
        config = registryreader.parseRegistry()
        config = registryreader.getVocabularyValues(config)
        config.update(op_config)
        registryreader.mapOperations(config)
        registryreader.mapSortableIndexes(config)
        config = {
            'indexes': config.get('bika.lims.bika_catalog_query.field'),
            'sortable_indexes': config.get('sortable'),
        }
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


class MultiSelectWidget(WidgetTraverse):

    def getValues(self, index=None):
        config = self.getConfig()
        if not index:
            index = self.request.form.get('index')
        values = None
        if index is not None:
            values = config['indexes'][index]['values']
        return values

    def getSortedValuesKeys(self, values):
        # do a lowercase sort of the keys
        return sorted(values.iterkeys(), key = lambda x : x.lower())
