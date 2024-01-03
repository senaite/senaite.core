# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

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


class ILabelCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite label catalog
    """


class IClientCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite client catalog
    """


class IContactCatalog(ISenaiteCatalogObject):
    """Marker interface for Senaite contact catalog
    """
