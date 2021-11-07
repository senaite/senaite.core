# -*- coding: utf-8 -*-

from zope.interface import Interface


class ISenaiteCatalog(Interface):
    """Marker interface for Senaite catalog objects
    """


class ISampleCatalog(ISenaiteCatalog):
    """Marker interface for Senaite sample catalog
    """


class ISetupCatalog(ISenaiteCatalog):
    """Marker interface for Senaite setup catalog
    """


class IAnalysisCatalog(ISenaiteCatalog):
    """Marker interface for Senaite analysis catalog
    """


class IAuditlogCatalog(ISenaiteCatalog):
    """Marker interface for Senaite auditlog catalog
    """


class IAutoImportLogCatalog(ISenaiteCatalog):
    """Marker interface for Senaite auto import log catalog
    """
