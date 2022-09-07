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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

# BBB Imports
from senaite.core.catalog import AUDITLOG_CATALOG as CATALOG_AUDITLOG
from senaite.core.catalog import SAMPLE_CATALOG as CATALOG_ANALYSIS_REQUEST_LISTING
from senaite.core.catalog import ANALYSIS_CATALOG as CATALOG_ANALYSIS_LISTING
from senaite.core.catalog import AUTOIMPORTLOG_CATALOG as CATALOG_AUTOIMPORTLOGS_LISTING
from senaite.core.catalog import SENAITE_CATALOG as BIKA_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG as CATALOG_WORKSHEET_LISTING
from senaite.core.catalog import REPORT_CATALOG as CATALOG_REPORT_LISTING
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import SETUP_CATALOG as CATALOG_SETUP

# Catalog classes
from .auditlog_catalog import AuditLogCatalog
from .bika_catalog import BikaCatalog
from .bikasetup_catalog import BikaSetupCatalog
from .analysis_catalog import BikaAnalysisCatalog
from .analysisrequest_catalog import BikaCatalogAnalysisRequestListing
from .autoimportlogs_catalog import BikaCatalogAutoImportLogsListing
from .worksheet_catalog import BikaCatalogWorksheetListing
from .report_catalog import BikaCatalogReport
