# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from .analysisrequest_catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from .analysis_catalog import CATALOG_ANALYSIS_LISTING
from .autoimportlogs_catalog import CATALOG_AUTOIMPORTLOGS_LISTING
from .worksheet_catalog import CATALOG_WORKSHEET_LISTING
from .report_catalog import CATALOG_REPORT_LISTING
# Catalog classes
from .bika_catalog import BikaCatalog
from .bikasetup_catalog import BikaSetupCatalog
from .analysis_catalog import BikaAnalysisCatalog
from .analysisrequest_catalog import BikaCatalogAnalysisRequestListing
from .autoimportlogs_catalog import BikaCatalogAutoImportLogsListing
from .worksheet_catalog import BikaCatalogWorksheetListing
from .report_catalog import BikaCatalogReport
# Catalog public functions
from .catalog_utilities import getCatalogDefinitions
from .catalog_utilities import setup_catalogs
from .catalog_utilities import getCatalog

# --Some important information:--
#
# - CatalogTool module. Here we can find the default indexes that plone
#  expects from its acatlogs. Be aware that if any of those indexes and
#  columns are missing, some specific queries or actions over the acatalog
#  might fail:
# https://github.com/plone/Products.CMFPlone/blob/4.3.x/Products/CMFPlone/CatalogTool.py
#
# - Here we have the portal_catalog definition, we can take some tips from its
# index definitions:
# https://github.com/plone/Products.CMFPlone/blob/4.2.x/Products/CMFPlone/profiles/default/catalog.xml
# and
# https://github.com/plone/Products.CMFPlone/blob/4.2.x/Products/CMFPlone/catalog.zcml
