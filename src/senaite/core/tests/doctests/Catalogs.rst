Catalogs
--------

SENAITE comes with several catalogs to index specific objects.
For Archetype objects, the catalog mapping is done in `archetype_tool`.


Running this test from the buildout directory::

    bin/test test_textual_doctests -t Catalogs


Test Setup
..........

Needed Imports::

    >>> from bika.lims import api

    >>> from senaite.core.catalog import ANALYSIS_CATALOG
    >>> from senaite.core.catalog import AUDITLOG_CATALOG
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.setuphandlers import CATALOG_MAPPINGS


Variables::

    >>> portal = self.portal
    >>> request = self.request
    >>> archetype_tool = api.get_tool("archetype_tool")


Catalog Mappings
................

Catalogs should be mapped according to the catalog mappings:

    >>> passed = {}

    >>> for mapping in CATALOG_MAPPINGS:
    ...     portal_type, catalogs = mapping
    ...     mapped = archetype_tool.catalog_map.get(portal_type)
    ...     passed[portal_type] = set(catalogs).issubset(mapped)

    >>> all(passed.values())
    True


Sample Catalog
..............

Samples should be registered in the sample catalog:

    >>> catmap = archetype_tool.catalog_map.get("AnalysisRequest")

    >>> len(catmap)
    2

    >>> SAMPLE_CATALOG in catmap
    True

    >>> AUDITLOG_CATALOG in catmap
    True


Analysis Catalog
................

Analyses should be registered in the analysis catalog:

    >>> catmap = archetype_tool.catalog_map.get("Analysis")

    >>> len(catmap)
    2

    >>> ANALYSIS_CATALOG in catmap
    True

    >>> AUDITLOG_CATALOG in catmap
    True
