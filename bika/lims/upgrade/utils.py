
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ProgressHandler import ZLogHandler
from bika.lims import logger
from bika.lims.catalog.catalog_utilities import addZCTextIndex
# Interesting page for logging indexing process and others:
# https://github.com/plone/Products.ZCatalog/tree/master/src/Products/ZCatalog
# and
# https://github.com/plone/Products.CMFPlone/blob/master/Products/CMFPlone/CatalogTool.py
import traceback
import sys
import transaction


class UpgradeUtils(object):

    def __init__(self, portal, pgthreshold=100):
        self.portal = portal
        self.reindexcatalog = {}
        self.refreshcatalog = []
        self.pgthreshold = pgthreshold

    def getInstalledVersion(self, product):
        qi = self.portal.portal_quickinstaller
        info = qi.upgradeInfo(product)
        return info['installedVersion']

    def isOlderVersion(self, product, version):
        # If the version to upgrade is lower than te actual version of the
        # product, skip the step to prevent out-of-date upgrade
        # Since there are heteregeneous names of versioning before v3.2.0, we
        # need to convert the version string to numbers, format and compare
        iver = self.getInstalledVersion(product)
        iver = self.normalizeVersion(iver)
        nver = self.normalizeVersion(version)
        logger.debug('{0} versions: Installed {1} - Target {2}'
                     .format(product, nver, iver))
        return nver < iver

    def normalizeVersion(self, version):
        ver = version.replace('.', '')
        major = ver[0] if len(ver) >= 1 else '0'
        minor = ver[1] if len(ver) >= 2 else '0'
        rev = ver[2:] if len(ver) >= 3 else '0'
        patch = 0
        if len(rev) == 5:
            patch = rev[1:]
            rev = rev[:1]
        elif len(rev) > 2:
            patch = rev[2:]
            rev = rev[:2]

        return '{0}.{1}.{2}.{3}'.format(
                '{:02d}'.format(int(major)),
                '{:02d}'.format(int(minor)),
                '{:02d}'.format(int(rev)),
                '{:04d}'.format(int(patch)))

    def delIndexAndColumn(self, catalog, index):
        self.delIndex(catalog, index)
        self.delColumn(catalog, index)

    def addIndexAndColumn(self, catalog, index, indextype):
        self.addIndex(catalog, index, indextype)
        self.addColumn(catalog, index)

    def reindexAndRefresh(self):
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
            raise

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
            raise

    def addIndex(self, catalog, index, indextype):
        cat = self._getCatalog(catalog)
        if index in cat.indexes():
            return
        try:
            if indextype == 'ZCTextIndex':
                addZCTextIndex(cat, index)
            else:
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
            raise

    def addColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column in cat.schema():
            return
        try:
            cat.addColumn(column)
            logger.info('Added column {0} to catalog {1}'.format(
                column, cat.id))
            if cat.id not in self.refreshcatalog:
                logger.info("{} to refresh because col {} added".format(
                    catalog, column
                ))
                self.refreshcatalog.append(cat.id)
            transaction.commit()
        except:
            logger.error(
                'Unable to add column {0} to catalog {1}'.format(
                    column, cat.id))
            raise

    def refreshCatalogs(self):
        """
        It reindexes the modified catalogs but, while cleanAndRebuildCatalogs
        recatalogs all objects in the database, this method only reindexes over
        the already cataloged objects.

        If a metacolumn is added it refreshes the catalog, if only a new index
        is added, it reindexes only those new indexes.
        """
        to_refresh = self.refreshcatalog[:]
        to_reindex = self.reindexcatalog.keys()
        to_reindex = to_reindex[:]
        done = []
        # Start reindexing the catalogs with new columns
        for catalog_to_refresh in to_refresh:
            try:
                logger.info(
                    'Catalog {0} refreshing started'.format(catalog_to_refresh))
                catalog = getToolByName(self.portal, catalog_to_refresh)
                handler = ZLogHandler(self.pgthreshold)
                catalog.refreshCatalog(pghandler=handler)
                logger.info('Catalog {0} refreshed'.format(catalog_to_refresh))
                transaction.commit()
            except:
                logger.error(
                    'Unable to refresh catalog {0}'.format(catalog_to_refresh))
                raise
            done.append(catalog_to_refresh)
        # Now the catalogs which only need reindxing
        for catalog_to_reindex in to_reindex:
            if catalog_to_reindex in done:
                continue
            try:
                logger.info(
                    'Catalog {0} reindexing started'.format(catalog_to_reindex))
                catalog = getToolByName(
                    self.portal, catalog_to_reindex)
                indexes = self.reindexcatalog[catalog_to_reindex]
                handler = ZLogHandler(self.pgthreshold)
                catalog.reindexIndex(indexes, None, pghandler=handler)
                logger.info('Catalog {0} reindexed'.format(catalog_to_reindex))
                transaction.commit()
            except:
                logger.error(
                    'Unable to reindex catalog {0}'
                    .format(catalog_to_reindex))
                raise
            done.append(catalog_to_reindex)

    def cleanAndRebuildCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        for catid in cats:
            try:
                catalog = getToolByName(self.portal, catid)
                # manage_catalogRebuild does the same as clearFindAndRebuild
                # but it alse loggs cpu and time.
                catalog.manage_catalogRebuild()
                logger.info('Catalog {0} cleaned and rebuilt'.format(catid))
                transaction.commit()
            except:
                logger.error('Unable to clean and rebuild catalog {0}'.format(
                            catid))
                raise
