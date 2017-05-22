from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.catalog.catalog_utilities import addZCTextIndex

import traceback
import sys
import transaction


class UpgradeUtils(object):
    def __init__(self, portal):
        self.portal = portal
        self.reindexcatalog = {}
        self.refreshcatalog = []

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
        logger.debug('{} versions: Installed {} - Target {}'
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

        return '{}.{}.{}.{}'.format(
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
            logger.info('Deleted index {} from {}'.format(index, cat.id))
            transaction.commit()
        except:
            logger.error(
                'Unable to delete index {} from {}'.format(index, cat.id))
            raise

    def delColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column not in cat.schema():
            return
        try:
            cat.delColumn(column)
            logger.info('Deleted column {} from {}'.format(column, cat.id))
            transaction.commit()
        except:
            logger.error(
                'Unable to delete column {} from {}'.format(column, cat.id))
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
            logger.info('Added index {} to {}'.format(index, cat.id))
            indexes = self.reindexcatalog.get(cat.id, [])
            indexes.append(index)
            indexes = list(set(indexes))
            self.reindexcatalog[cat.id] = indexes
            transaction.commit()
        except:
            logger.error('Unable to add index {} to {}'.format(index, cat.id))
            raise

    def addColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column in cat.schema():
            return
        try:
            cat.addColumn(column)
            logger.info('Added column {} to {}'.format(column, cat.id))
            if cat.id not in self.refreshcatalog:
                self.refreshcatalog.append(cat.id)
            transaction.commit()
        except:
            logger.error('Unable to add column {} to {}'.format(column, cat.id))
            raise

    def refreshCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        cats = list(set(cats))
        for catalogid in cats:
            try:
                catalog = getToolByName(self.portal, catalogid)
                catalog.refreshCatalog()
                logger.info('Catalog {} refreshed'.format(catalogid))
                transaction.commit()
            except:
                logger.error('Unable to refresh {}'.format(catalogid))
                raise

    def cleanAndRebuildCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        for catid in cats:
            try:
                catalog = getToolByName(self.portal, catid)
                catalog.clearFindAndRebuild()
                logger.info('Catalog {} cleaned and rebuilt'.format(catid))
                transaction.commit()
            except:
                logger.error('Unable to clean and rebuild {}'.format(catid))
                raise
