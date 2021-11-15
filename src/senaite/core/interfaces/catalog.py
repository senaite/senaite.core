# -*- coding: utf-8 -*-

from zope.interface import Interface


class ISenaiteCatalogObject(Interface):
    """Marker interface for Senaite catalog objects
    """


class ISampleCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite sample catalog
    """


class ISetupCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite setup catalog
    """


class IAnalysisCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite analysis catalog
    """


class IAuditlogCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite auditlog catalog
    """


class IAutoImportLogCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite auto import log catalog
    """


class ISenaiteCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite catalog
    """


class IWorksheetCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite worksheet catalog
    """


class IReportCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite report catalog
    """
