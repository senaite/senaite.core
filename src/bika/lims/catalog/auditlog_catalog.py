# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IAuditLogCatalog
from zope.interface import implements
from senaite.core.catalog import AUDITLOG_CATALOG as CATALOG_AUDITLOG  # noqa


class AuditLogCatalog(BaseCatalog):
    implements(IAuditLogCatalog)


InitializeClass(AuditLogCatalog)
