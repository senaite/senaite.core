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

# flake8:noqa:F401
from plone.memoize import forever

from senaite.core.catalog.analysis_catalog import \
    CATALOG_ID as ANALYSIS_CATALOG
from senaite.core.catalog.analysis_catalog import AnalysisCatalog
from senaite.core.catalog.auditlog_catalog import \
    CATALOG_ID as AUDITLOG_CATALOG
from senaite.core.catalog.auditlog_catalog import AuditlogCatalog
from senaite.core.catalog.autoimportlog_catalog import \
    CATALOG_ID as AUTOIMPORTLOG_CATALOG
from senaite.core.catalog.autoimportlog_catalog import AutoImportLogCatalog
from senaite.core.catalog.client_catalog import CATALOG_ID as CLIENT_CATALOG
from senaite.core.catalog.client_catalog import ClientCatalog
from senaite.core.catalog.contact_catalog import CATALOG_ID as CONTACT_CATALOG
from senaite.core.catalog.contact_catalog import ContactCatalog
from senaite.core.catalog.label_catalog import CATALOG_ID as LABEL_CATALOG
from senaite.core.catalog.label_catalog import LabelCatalog
from senaite.core.catalog.report_catalog import CATALOG_ID as REPORT_CATALOG
from senaite.core.catalog.report_catalog import ReportCatalog
from senaite.core.catalog.sample_catalog import CATALOG_ID as SAMPLE_CATALOG
from senaite.core.catalog.sample_catalog import SampleCatalog
from senaite.core.catalog.senaite_catalog import CATALOG_ID as SENAITE_CATALOG
from senaite.core.catalog.senaite_catalog import SenaiteCatalog
from senaite.core.catalog.setup_catalog import CATALOG_ID as SETUP_CATALOG
from senaite.core.catalog.setup_catalog import SetupCatalog
from senaite.core.catalog.worksheet_catalog import \
    CATALOG_ID as WORKSHEET_CATALOG
from senaite.core.catalog.worksheet_catalog import WorksheetCatalog
from senaite.core.registry import get_registry_record

CATALOG_MAPPINGS = (
    # portal_type, catalog_ids
    ("ARReport", [REPORT_CATALOG]),
    ("ARTemplate", [SETUP_CATALOG]),
    ("Analysis", [ANALYSIS_CATALOG]),
    ("AnalysisCategory", [SETUP_CATALOG]),
    ("AnalysisProfile", [SETUP_CATALOG]),
    ("AnalysisRequest", [SAMPLE_CATALOG]),
    ("AnalysisService", [SETUP_CATALOG]),
    ("AnalysisSpec", [SETUP_CATALOG]),
    ("Attachment", [SENAITE_CATALOG]),
    ("AttachmentType", [SETUP_CATALOG]),
    ("AutoImportLog", [AUTOIMPORTLOG_CATALOG]),
    ("Batch", [SENAITE_CATALOG]),
    ("BatchLabel", [SETUP_CATALOG]),
    ("Calculation", [SETUP_CATALOG]),
    ("Client", [CLIENT_CATALOG]),
    ("Contact", [CONTACT_CATALOG]),
    ("Container", [SETUP_CATALOG]),
    ("ContainerType", [SETUP_CATALOG]),
    ("Department", [SETUP_CATALOG]),
    ("DuplicateAnalysis", [ANALYSIS_CATALOG]),
    ("Instrument", [SETUP_CATALOG]),
    ("InstrumentCalibration", [SETUP_CATALOG]),
    ("InstrumentCertification", [SETUP_CATALOG]),
    ("InstrumentLocation", [SETUP_CATALOG]),
    ("InstrumentMaintenanceTask", [SETUP_CATALOG]),
    ("InstrumentScheduledTask", [SETUP_CATALOG]),
    ("InstrumentType", [SETUP_CATALOG]),
    ("InstrumentValidation", [SETUP_CATALOG]),
    ("Invoice", [SENAITE_CATALOG]),
    ("LabContact", [CONTACT_CATALOG]),
    ("LabProduct", [SETUP_CATALOG]),
    ("Label", [SETUP_CATALOG]),
    ("Laboratory", [SETUP_CATALOG]),
    ("Manufacturer", [SETUP_CATALOG]),
    ("Method", [SETUP_CATALOG]),
    ("Multifile", [SETUP_CATALOG]),
    ("Preservation", [SETUP_CATALOG]),
    ("Pricelist", [SETUP_CATALOG]),
    ("ReferenceAnalysis", [ANALYSIS_CATALOG]),
    ("ReferenceDefinition", [SETUP_CATALOG]),
    ("ReferenceSample", [SENAITE_CATALOG]),
    ("RejectAnalysis", [ANALYSIS_CATALOG]),
    ("SampleCondition", [SETUP_CATALOG]),
    ("SampleMatrix", [SETUP_CATALOG]),
    ("SamplePoint", [SETUP_CATALOG]),
    ("SamplePreservation", [SETUP_CATALOG]),
    ("SampleType", [SETUP_CATALOG]),
    ("SamplingDeviation", [SETUP_CATALOG]),
    ("StorageLocation", [SETUP_CATALOG]),
    ("SubGroup", [SETUP_CATALOG]),
    ("Supplier", [SETUP_CATALOG]),
    ("SupplierContact", [CONTACT_CATALOG]),
    ("Worksheet", [WORKSHEET_CATALOG]),
    ("WorksheetTemplate", [SETUP_CATALOG]),
)


@forever.memoize
def get_catalogs_by_type(portal_type):
    """Returns the predefined catalogs by type, along with the catalogs that
    are assigned to the given portal type in "catalog_mappings" registry key

    :param portal_type: The portal type to look up
    """
    if not isinstance(portal_type, str):
        raise TypeError("Expected string type, got <%s>" % type(portal_type))
    mapping = dict(CATALOG_MAPPINGS)
    catalogs = mapping.get(portal_type) or []

    registry_mapping = get_registry_record("catalog_mappings")
    if not registry_mapping:
        return catalogs

    # extend with additional catalogs from registry
    additional = registry_mapping.get(portal_type, [])
    for catalog in additional:
        if catalog in catalogs:
            continue
        catalogs.append(catalog)

    return catalogs
