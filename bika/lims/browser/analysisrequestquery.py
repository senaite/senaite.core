from archetypes.querywidget.views import WidgetTraverse
from bika.lims.querystring.querybuilder import QueryBuilder
from bika.lims.querystring.querybuilder import RegistryConfiguration
from bika.lims.querystring.registryreader import QuerystringRegistryReader
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implements


_p = MessageFactory('plone')


class AnalysisRequestQuerystringRegistryReader(QuerystringRegistryReader):
    implements(IQuerystringRegistryReader)
    prefix = 'bika.lims.analysisrequestquery'


class AnalysisRequestQueryRegistryConfiguration(RegistryConfiguration):
    prefix = 'bika.lims.analysisrequestquery'


class AnalysisRequestQueryBuilder(QueryBuilder):
    catalog_name = 'bika_catalog'
    contentFilter = {'portal_type': 'AnalysisRequest'}


class AnalysisRequestQueryWidgetTraverse(WidgetTraverse):

    def getConfig(self):
        """get the config"""
        registry = getUtility(IRegistry)
        # First grab the base config, so we can use the operations
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "plone.app.querystring.operation"
        op_config = registryreader.parseRegistry()
        # Then combine our fields
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "bika.lims.analysisrequestquery"
        config = registryreader.parseRegistry()
        config = registryreader.getVocabularyValues(config)
        config.update(op_config)
        registryreader.mapOperations(config)
        registryreader.mapSortableIndexes(config)
        config = {
            'indexes': config.get('bika.lims.analysisrequestquery.field'),
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


class MultiSelectWidget(AnalysisRequestQueryWidgetTraverse):

    def getValues(self, index=None):
        config = self.getConfig()
        if not index:
            index = self.request.form.get('index')
        values = None
        if index is not None:
            values = config['indexes'][index]['values']
        return values
