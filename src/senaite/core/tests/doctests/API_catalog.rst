SENAITE Catalog API
-------------------

The mail API provides a simple interface to manage catalogs

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_catalog


Test Setup
..........

Imports:

    >>> from senaite.core.api import catalog as capi

    
Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Get a catalog tool
..................

Catalog objects can be fetched by name or object:

    >>> from senaite.core.catalog import SETUP_CATALOG
    >>> capi.get_catalog(SETUP_CATALOG)
    <SetupCatalog at /plone/senaite_catalog_setup>

    >>> capi.get_catalog(capi.get_catalog(SETUP_CATALOG))
    <SetupCatalog at /plone/senaite_catalog_setup>

Other objects raise an error:

    >>> capi.get_catalog("acl_users")
    Traceback (most recent call last):
    ...
    APIError: No catalog found for 'acl_users'

We can also check if an object is a catalog:

    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> sample_catalog = capi.get_catalog(SAMPLE_CATALOG)

    >>> capi.is_catalog(sample_catalog)
    True

    >>> capi.is_catalog(object())
    False


Catalog indexes
...............

Getting a list of all indexes:

    >>> sample_catalog = capi.get_catalog(SAMPLE_CATALOG)
    >>> indexes = capi.get_indexes(sample_catalog)
    >>> "UID" in indexes
    True

Adding a new index to the catalog:

    >>> IDX = "my_fancy_index"

    >>> capi.add_index(sample_catalog, IDX, "FieldIndex")
    True

    >>> IDX in capi.get_indexes(sample_catalog)
    True

    >>> index = capi.get_index(sample_catalog, IDX)
    >>> index.__class__
    <class 'Products.PluginIndexes.FieldIndex.FieldIndex.FieldIndex'>

Reindexing the new index:

    >>> capi.reindex_index(sample_catalog, IDX)
    True

Removing an index from the catalog:

    >>> capi.del_index(sample_catalog, IDX)
    True

    >>> IDX in capi.get_indexes(sample_catalog)
    False

Adding a `ZCTextIndex` requires a `ZCLexicon` lexicon.
Therefore, `add_zc_text_index` takes care of it:

    >>> LEXICON = "my_fancy_lexicon"

    >>> capi.add_zc_text_index(sample_catalog, IDX, lex_id=LEXICON)
    True

    >>> index = capi.get_index(sample_catalog, IDX)
    >>> index.__class__
    <class 'Products.ZCTextIndex.ZCTextIndex.ZCTextIndex'>

    >>> lexicon = sample_catalog[LEXICON]
    >>> lexicon.__class__
    <class 'Products.ZCTextIndex.ZCTextIndex.PLexicon'>

    >>> capi.del_index(sample_catalog, IDX)
    True


Catalog Columns
...............

Getting a list of all catalog columns

    >>> sample_catalog = capi.get_catalog(SAMPLE_CATALOG)
    >>> columns = capi.get_columns(sample_catalog)
    >>> "getId" in columns
    True

Adding a column to the catalog:

    >>> COLUMN = "my_fancy_column"

    >>> capi.add_column(sample_catalog, COLUMN)
    True

Check if the column exists:

    >>> COLUMN in capi.get_columns(sample_catalog)
    True

Delete the column:

    >>> capi.del_column(sample_catalog, COLUMN)
    True

Check if the column was deleted:

    >>> COLUMN in capi.get_columns(sample_catalog)
    False
