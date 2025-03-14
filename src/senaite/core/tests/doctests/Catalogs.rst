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

    >>> from senaite.core.catalog import flush_catalogs_cache
    >>> from senaite.core.catalog import get_catalogs_by_type
    >>> from senaite.core.catalog import set_catalogs
    >>> from senaite.core.catalog import ANALYSIS_CATALOG
    >>> from senaite.core.catalog import AUDITLOG_CATALOG
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.registry import get_registry_record
    >>> from senaite.core.registry import set_registry_record
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


Get catalogs by type
....................

The `archetype_tool` only gives us the catalogs for `Archetype`-based types.
The function `get_catalogs_by_type` allows us to overcome this problem, but
with the following considerations:

- `auditlog_catalog` is skipped, cause the cataloguing of objects into
  that catalog is automatically handled by the multiplexer functionality.

- Likewise, `uid_catalog` is a special catalog where all AT contents, plus those
  DX contents implementing the `Referenceable` behavior are catalogued.

As a result, `get_catalogs_by_type` returns the catalogs despite the *nature*
of the type (`Archetype` or `Dexterity`) but only those that are specific for
the given portal type. Nothing less, nothing more:

    >>> get_catalogs_by_type("Analysis")
    ['senaite_catalog_analysis']

    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']


Set catalogs programmatically
.............................

We can even add catalogs for a given portal type programmatically, with ease.

    >>> set_catalogs("Analysis", ["portal_catalog"])
    >>> get_catalogs_by_type("Analysis")
    ['senaite_catalog_analysis', 'portal_catalog']

Again, this works for both AT and DX:

    >>> set_catalogs("SampleType", ["portal_catalog"])
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup', 'portal_catalog']

We can replace the catalogs if we use a tuple instead of a list:

    >>> set_catalogs("Analysis", tuple(["senaite_catalog_analysis"]))
    >>> get_catalogs_by_type("Analysis")
    ['senaite_catalog_analysis']

    >>> set_catalogs("SampleType", tuple(["senaite_catalog_setup"]))
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']

If the given type is from `senaite.core` we cannot remove default catalogs
though:

    >>> set_catalogs("SampleType", tuple(["portal_catalog"]))
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup', 'portal_catalog']

Even when using an empty tuple:

    >>> set_catalogs("SampleType", tuple())
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']


Flush catalogs mapping cache
............................

To speed up the process of retrieval of catalogs, the output of the function
`get_catalogs_by_type` is forever memoized. This means that if we manually
update the value of the registry record that stores the catalog mappings,
changes won't take effect until restart:

    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']

    >>> mappings = get_registry_record("catalog_mappings") or {}
    >>> mappings["SampleType"] = ["portal_catalog"]
    >>> set_registry_record("catalog_mappings", mappings)

    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']

To prevent this to happen, we can flush the cache for the given type:

    >>> flush_catalogs_cache("SampleType")
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup', 'portal_catalog']

    >>> mappings["SampleType"] = []
    >>> set_registry_record("catalog_mappings", mappings)
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup', 'portal_catalog']

    >>> flush_catalogs_cache("SampleType")
    >>> get_catalogs_by_type("SampleType")
    ['senaite_catalog_setup']
