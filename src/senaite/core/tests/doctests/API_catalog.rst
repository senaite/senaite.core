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


Searchable Text Querystring
---------------------------

https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html#boolean-expressions

Searching for a single word:

    >>> capi.to_searchable_text_qs("sample")
    u'sample*'

Without wildcard:

    >>> capi.to_searchable_text_qs("sample", wildcard=False)
    u'sample'

Wildcards at the beginning of the searchterms are not supported:

    >>> capi.to_searchable_text_qs("?H2O")
    u'H2O*'

    >>> capi.to_searchable_text_qs("*H2O")
    u'H2O*'

Wildcards at the end of the searchterms are retained:

    >>> capi.to_searchable_text_qs("H2O?")
    u'H2O?'

    >>> capi.to_searchable_text_qs("H2O*")
    u'H2O*'

If the search contains only a single character, it needs to be a word:

    >>> capi.to_searchable_text_qs("W")
    u'W*'

    >>> capi.to_searchable_text_qs("$")
    u''

Searching for a unicode word:

    >>> capi.to_searchable_text_qs("AäOöUüZ")
    u'A\xe4O\xf6U\xfcZ*'

Searching for multiple unicode words:

    >>> capi.to_searchable_text_qs("Ä Ö Ü")
    u'\xc4* AND \xd6* AND \xdc*'

Searching for a concatenated word:

    >>> capi.to_searchable_text_qs("H2O-0001")
    u'H2O-0001*'

Searching for two words:

    >>> capi.to_searchable_text_qs("Fresh Funky")
    u'Fresh* AND Funky*'

Tricky query strings (with and/or in words or in between):

    >>> capi.to_searchable_text_qs("Fresh and Funky Oranges from Andorra")
    u'Fresh* AND Funky* AND Oranges* AND from* AND Andorra*'

Search with special characters:

    >>> capi.to_searchable_text_qs("H2O_0001")
    u'H2O_0001*'

    >>> capi.to_searchable_text_qs("H2O.0001")
    u'H2O.0001*'

    >>> capi.to_searchable_text_qs("H2O<>0001")
    u'H2O<>0001*'

    >>> capi.to_searchable_text_qs("H2O:0001")
    u'H2O:0001*'

    >>> capi.to_searchable_text_qs("H2O/0001")
    u'H2O/0001*'

    >>> capi.to_searchable_text_qs("'H2O-0001'")
    u'H2O-0001*'

    >>> capi.to_searchable_text_qs("\'H2O-0001\'")
    u'H2O-0001*'

    >>> capi.to_searchable_text_qs("(H2O-0001)*")
    u'H2O-0001*'

    >>> capi.to_searchable_text_qs("****([H2O-0001])****")
    u'H2O-0001*'

    >>> capi.to_searchable_text_qs("********************")
    u''

    >>> capi.to_searchable_text_qs("*H2O*")
    u'H2O*'

    >>> capi.to_searchable_text_qs("And the question is AND OR maybe NOT AND")
    u'the* AND question* AND is* AND OR maybe* AND NOT*'

    >>> capi.to_searchable_text_qs("AND OR")
    u''

    >>> capi.to_searchable_text_qs("H2O NOT 11")
    u'H2O* AND NOT* AND 11*'


Loading the object of a catalog entry
.....................................

`get_loaded_object` returns the object of a catalog entry with its stored
state loaded:

    >>> brain = capi.get_catalog(SETUP_CATALOG).searchAll()[0]
    >>> obj = capi.get_loaded_object(brain)
    >>> obj == brain.getObject()
    True

The stored state of an object can be damaged, so that loading it fails. The
catalog entry still returns the object, as an unloaded ghost, and the error
only shows when the first attribute is read. `get_loaded_object` loads the
state, logs the object and returns `None` instead:

    >>> class StoredObject(object):
    ...     def __init__(self, error=None):
    ...         self.error = error
    ...     def _p_activate(self):
    ...         if self.error:
    ...             raise self.error

    >>> class Brain(object):
    ...     def __init__(self, obj):
    ...         self.obj = obj
    ...     def getObject(self):
    ...         if self.obj is None:
    ...             raise KeyError("W-0001")
    ...         return self.obj
    ...     def getPath(self):
    ...         return "/plone/clients/client-1/W-0001"

    >>> damaged = AttributeError("'dict' object has no attribute 'append'")
    >>> capi.get_loaded_object(Brain(StoredObject(damaged))) is None
    True

    >>> from ZODB.POSException import POSKeyError
    >>> capi.get_loaded_object(Brain(StoredObject(POSKeyError("0x01")))) is None
    True

The objects that could not be loaded in the current request are listed,
with the reason:

    >>> capi.get_damaged_objects()
    [('/plone/clients/client-1/W-0001', "AttributeError: 'dict' object has no attribute 'append'"), ('/plone/clients/client-1/W-0001', "POSKeyError: '0x01'")]

An object that is gone, the catalog entry is stale, returns `None` as well,
without a log entry:

    >>> capi.get_loaded_object(Brain(None)) is None
    True

A conflict is no damage, the transaction has to be retried, so it is
raised:

    >>> from ZODB.POSException import ReadConflictError
    >>> capi.get_loaded_object(Brain(StoredObject(ReadConflictError())))
    Traceback (most recent call last):
    ...
    ReadConflictError: database read conflict error

An upgrade step anyone may run gets the object without checking the
permissions of the current user:

    >>> from plone.app.testing import logout
    >>> from plone.app.testing import login
    >>> from plone.app.testing import TEST_USER_NAME
    >>> logout()
    >>> capi.get_loaded_object(brain)
    Traceback (most recent call last):
    ...
    Unauthorized: ...

    >>> capi.get_loaded_object(brain, unrestricted=True) == obj
    True
    >>> login(portal, TEST_USER_NAME)


Damaged objects in an upgrade step
..................................

Every upgrade step of senaite.core lists the objects it skipped because they
cannot be loaded, when it is done. The list starts empty with each step:

    >>> import logging
    >>> from senaite.core import logger
    >>> from senaite.core.events import AfterUpgradeStepEvent
    >>> from senaite.core.events import BeforeUpgradeStepEvent
    >>> from zope.event import notify

    >>> class Messages(logging.Handler):
    ...     def __init__(self):
    ...         logging.Handler.__init__(self)
    ...         self.messages = []
    ...     def emit(self, record):
    ...         self.messages.append(record.getMessage())
    >>> messages = Messages()
    >>> logger.addHandler(messages)

    >>> notify(BeforeUpgradeStepEvent(portal))
    >>> capi.get_damaged_objects()
    []

    >>> capi.get_loaded_object(Brain(StoredObject(damaged))) is None
    True

    >>> del messages.messages[:]
    >>> notify(AfterUpgradeStepEvent(portal))
    >>> for message in messages.messages:
    ...     print(message)
    The upgrade step skipped 1 objects that cannot be loaded:
      /plone/clients/client-1/W-0001 (AttributeError: 'dict' object has no attribute 'append')

    >>> capi.get_damaged_objects()
    []

A step without damaged objects lists nothing:

    >>> notify(BeforeUpgradeStepEvent(portal))
    >>> del messages.messages[:]
    >>> notify(AfterUpgradeStepEvent(portal))
    >>> messages.messages
    []

    >>> logger.removeHandler(messages)
