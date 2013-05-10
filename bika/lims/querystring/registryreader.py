from plone.app.querystring.interfaces import IQuerystringRegistryReader
from bika.lims.querystring.querybuilder import RegistryConfiguration
from plone.app.querystring.registryreader import \
    QuerystringRegistryReader as _QuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implements


_p = MessageFactory('plone')


class QuerystringRegistryReader(_QuerystringRegistryReader):

    implements(IQuerystringRegistryReader)
    prefix = 'bika.lims.bika_catalog_query'

    def __call__(self):
        """Return the registry configuration in JSON format"""
        registry = getUtility(IRegistry)
        # First grab the base config, so we can use the operations
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = "plone.app.querystring.operation"
        op_config = registryreader.parseRegistry()
        # Then combine our fields
        registryreader = IQuerystringRegistryReader(registry)
        registryreader.prefix = self.prefix
        config = registryreader.parseRegistry()
        config = registryreader.getVocabularyValues(config)
        config.update(op_config)
        registryreader.mapOperations(config)
        registryreader.mapSortableIndexes(config)
        return {
            'indexes': config.get(self.prefix + '.field'),
            'sortable_indexes': config.get('sortable'),
        }


_p = MessageFactory('plone')


class QueryRegistryConfiguration(RegistryConfiguration):
    prefix = 'bika.lims.bika_catalog_query'

