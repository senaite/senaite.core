Catalog console
---------------

`senaite-catalog` reindexes single catalog indexes or clears and rebuilds
a whole catalog. It operates on the index and metadata layer of a catalog.
To reindex a single content object by path instead, use the `reindex`
script.

Start it against a stopped instance, optionally preselecting a catalog:

.. code-block:: console

   $ bin/instance stop
   $ bin/senaite-catalog
   $ bin/senaite-catalog --catalog senaite_catalog_sample

Commands
~~~~~~~~

.. code-block:: text

   catalogs             List the catalogs in the site with their object
                        count.
   select <catalog_id>  Choose the catalog to work on.
   indexes              List the indexes of the selected catalog and their
                        types, plus the metadata column count.
   reindex [<idx> ...]  Reindex the given indexes, or all indexes when none
                        are given. Rebuilds the index entries over every
                        cataloged object without clearing the catalog.
   rebuild              Clear and rebuild the selected catalog. Empties it
                        and re-indexes every mapped object. This is the
                        heavy, destructive option and asks to confirm first.

Reindex and rebuild
~~~~~~~~~~~~~~~~~~~~~

Reindex a couple of indexes after a change, review, then commit:

.. code-block:: text

   (catalog) select senaite_catalog_sample
   Selected senaite_catalog_sample (65 objects, 40 indexes, 30 columns)

   (catalog* senaite_catalog_sample) reindex review_state getId
   OK   reindex senaite_catalog_sample [review_state, getId]  (0.12s, ...)

   (catalog* senaite_catalog_sample) commit
   Transaction committed.

`reindex` with no index names reindexes every index of the catalog and
does not touch the metadata. `rebuild` clears the catalog and re-indexes
all mapped objects, which is the option to reach for when a catalog is
inconsistent rather than merely stale. Both are timed and their progress
captured, so `history` and `log` report what happened.

Non-interactive use
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   # list the indexes of a catalog and exit
   $ bin/senaite-catalog --catalog senaite_catalog_sample --indexes

   # reindex specific indexes and commit
   $ bin/senaite-catalog --catalog senaite_catalog_sample \
         --reindex "review_state getId" --commit

   # reindex every index and commit
   $ bin/senaite-catalog --catalog senaite_catalog_sample --reindex --commit

   # clear and rebuild a catalog and commit (no interactive confirm)
   $ bin/senaite-catalog --catalog senaite_catalog_sample --rebuild --commit

Without `--commit` the transaction is left uncommitted and you are
reminded to re-run with `--commit` to persist it.
