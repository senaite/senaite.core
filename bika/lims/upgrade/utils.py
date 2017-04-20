
from Products.CMFCore.utils import getToolByName
from bika.lims import logger

import traceback
import sys
import transaction


class UpgradeUtils(object):

    def __init__(self, portal):
        self.portal = portal
        self.reindexcatalog = {}
        self.refreshcatalog = []

    def delIndexAndColumn(self, catalog, index):
        self.delIndex(catalog, index)
        self.delColumn(catalog, index)

    def addIndexAndColumn(self, catalog, index, indextype):
        self.addIndex(catalog, index, indextype)
        self.addColumn(catalog, index)

    def reindexAndRefresh(self):
        self.reindexCatalogs()
        self.refreshCatalogs()

    def _getCatalog(self, catalog):
        if isinstance(catalog, str):
            return getToolByName(self.portal, catalog)
        return catalog

    def delIndex(self, catalog, index):
        cat = self._getCatalog(catalog)
        if index not in cat.indexes():
            return
        try:
            cat.delIndex(index)
            logger.info('Deleted index {0} from catalog {1}'.format(
                        index, cat.id))
            transaction.commit()
        except:
            logger.error(
                'Unable to delete index {0} from catalog {1}'.format(
                    index, cat.id))

    def delColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column not in cat.schema():
            return
        try:
            cat.delColumn(column)
            logger.info('Deleted column {0} from catalog {1} deleted.'.format(
                        column, cat.id))
            transaction.commit()
        except:
            logger.error(
                'Unable to delete column {0} from catalog {1}'.format(
                    column, cat.id))

    def addIndex(self, catalog, index, indextype):
        cat = self._getCatalog(catalog)
        if index in cat.indexes():
            return
        try:
            cat.addIndex(index, indextype)
            logger.info('Catalog index %s added.' % index)
            indexes = self.reindexcatalog.get(cat.id, [])
            indexes.append(index)
            indexes = list(set(indexes))
            self.reindexcatalog[cat.id] = indexes
            transaction.commit()
        except:
            logger.error(
                'Unable to add index {0} to catalog {1}'.format(
                    index, cat.id))

    def addColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column in cat.schema():
            return
        try:
            cat.addColumn(column)
            logger.info('Added column {0} to catalog {1}'.format(
                column, cat.id))
            if cat.id not in self.refreshcatalog:
                self.refreshcatalog.append(cat.id)
            transaction.commit()
        except:
            logger.error(
                'Unable to add column {0} to catalog {1}'.format(
                    column, cat.id))

    def refreshCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        cats = list(set(cats))
        for catalogid in cats:
            try:
                catalog = getToolByName(self.portal, catalogid)
                catalog.refreshCatalog()
                logger.info('Catalog {0} refreshed'.format(catalogid))
                transaction.commit()
            except:
                logger.error('Unable to refresh catalog {0}'.format(catalogid))

    def cleanAndRebuildCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        for catid in cats:
            try:
                catalog = getToolByName(self.portal, catid)
                catalog.clearFindAndRebuild()
                logger.info('Catalog {0} cleaned and rebuilt'.format(catid))
                transaction.commit()
            except:
                logger.error('Unable to clean and rebuild catalog {0}'.format(
                            catid))
