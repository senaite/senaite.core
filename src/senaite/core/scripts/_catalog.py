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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.ZCatalog.interfaces import IZCatalog
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core.scripts import parser
from senaite.core.scripts._console import ask
from senaite.core.scripts._console import BaseConsole
from senaite.core.scripts._console import bootstrap
from senaite.core.scripts._console import finish_noninteractive

__doc__ = """Reindex and rebuild SENAITE catalogs interactively.

This opens a controlled console to reindex single catalog indexes or to
clear and rebuild a whole catalog. Each operation is timed and its log
output captured. Nothing is committed automatically: commit or abort the
transaction explicitly when you are done.
"""

parser.description = __doc__
parser.add_argument("--catalog", dest="catalog", default=None, type=str,
                    help="Preselect a catalog id, e.g. senaite_catalog_sample")
parser.add_argument("--indexes", dest="do_indexes", action="store_true",
                    help="List the indexes of the catalog and exit")
parser.add_argument("--reindex", dest="do_reindex", default=None, type=str,
                    nargs="?", const="", metavar="IDX",
                    help="Reindex the given space separated indexes (all if "
                         "none) then exit")
parser.add_argument("--rebuild", dest="do_rebuild", action="store_true",
                    help="Clear and rebuild the catalog then exit")
parser.add_argument("--commit", dest="do_commit", action="store_true",
                    help="Commit the transaction after a non-interactive run")

# Report progress to the log every this many objects during a reindex.
PROGRESS_THRESHOLD = 1000

INTRO = """
SENAITE interactive catalog console
Type 'help' or '?' for the list of commands, 'help <cmd>' for details.
Nothing is committed until you type 'commit'. 'quit' warns if uncommitted.
"""


def get_catalogs(site):
    """Return the catalogs in the site as an ordered list of (id, catalog),
    sorted by id.
    """
    catalogs = []
    for obj in site.objectValues():
        if IZCatalog.providedBy(obj):
            catalogs.append((obj.getId(), obj))
    return sorted(catalogs, key=lambda pair: pair[0])


def catalog_length(catalog):
    """Number of objects indexed in the catalog
    """
    return len(catalog._catalog)


def index_meta_type(catalog, name):
    """The index type (e.g. FieldIndex, KeywordIndex) for an index name
    """
    index = catalog._catalog.getIndex(name)
    return getattr(index, "meta_type", type(index).__name__)


class CatalogConsole(BaseConsole):
    """Interactive console to reindex and rebuild SENAITE catalogs
    """

    intro = INTRO
    tool_name = "catalog"

    def __init__(self, app, site, verbose=False):
        self.catalog_id = None
        self.catalog = None
        BaseConsole.__init__(self, app, site, verbose=verbose)

    # -- hooks -----------------------------------------------------------

    def context_label(self):
        return self.catalog_id or "no catalog"

    def on_site_changed(self):
        self.catalog_id = None
        self.catalog = None

    def scoped_help(self):
        if self.catalog is None:
            return None
        return ("catalog '%s'" % self.catalog_id,
                ["indexes", "reindex", "rebuild"])

    # -- helpers ---------------------------------------------------------

    def _require_catalog(self):
        return self._require_selection(
            self.catalog,
            "No catalog selected. Use 'select <catalog_id>' (see 'catalogs').")

    def _known_indexes(self):
        return list(self.catalog.indexes())

    def _validate_indexes(self, names):
        """Split requested index names into known and unknown
        """
        known = set(self._known_indexes())
        valid = [name for name in names if name in known]
        unknown = [name for name in names if name not in known]
        return valid, unknown

    def _reindex(self, idxs):
        """Reindex the given indexes (or all when empty) of the selected
        catalog across every cataloged object, without clearing it.
        """
        handler = ZLogHandler(PROGRESS_THRESHOLD)
        names = idxs or self._known_indexes()
        self.catalog.reindexIndex(names, self.site.REQUEST, handler)

    def _rebuild(self):
        """Clear and rebuild the selected catalog
        """
        self.catalog.clearFindAndRebuild()

    # -- catalog commands ------------------------------------------------

    def do_catalogs(self, arg):
        """catalogs -- list the catalogs in the site with their object count
        """
        for cid, catalog in get_catalogs(self.site):
            marker = "*" if cid == self.catalog_id else " "
            print(" %s %-32s %8d objects"
                  % (marker, cid, catalog_length(catalog)))

    def do_select(self, arg):
        """select <catalog_id> -- choose the catalog to work on
        (e.g. select senaite_catalog_sample)
        """
        cid = arg.strip()
        if not cid:
            print("Usage: select <catalog_id>")
            return
        catalog = dict(get_catalogs(self.site)).get(cid)
        if catalog is None:
            print("Unknown catalog '%s'. See 'catalogs'." % cid)
            return
        self.catalog_id = cid
        self.catalog = catalog
        print("Selected %s (%d objects, %d indexes, %d metadata columns)"
              % (cid, catalog_length(catalog), len(catalog.indexes()),
                 len(catalog.schema())))
        self._update_prompt()

    def do_indexes(self, arg):
        """indexes -- list the indexes of the selected catalog and their
        types
        """
        if not self._require_catalog():
            return
        names = sorted(self._known_indexes())
        for name in names:
            print("  %-32s %s" % (name, index_meta_type(self.catalog, name)))
        print("%d indexes, %d metadata columns"
              % (len(names), len(self.catalog.schema())))

    def do_reindex(self, arg):
        """reindex [<idx> ...] -- reindex the given indexes of the selected
        catalog, or all indexes when none are given. This rebuilds index
        entries over every cataloged object without clearing the catalog.
        """
        if not self._require_catalog():
            return
        requested = arg.split()
        valid, unknown = self._validate_indexes(requested)
        if unknown:
            print("Unknown index(es): %s" % ", ".join(unknown))
            print("See 'indexes' for the valid names.")
            return
        target = valid or self._known_indexes()
        desc = "reindex %s [%s]" % (self.catalog_id, ", ".join(target))
        self._execute(desc, lambda: self._reindex(valid))

    def do_rebuild(self, arg):
        """rebuild -- clear and rebuild the selected catalog. This empties
        the catalog and re-indexes every mapped object, so it is the heavy,
        destructive option. You are asked to confirm first.
        """
        if not self._require_catalog():
            return
        count = catalog_length(self.catalog)
        print("This clears and rebuilds '%s' (%d objects). It can take a "
              "while." % (self.catalog_id, count))
        if not ask("Proceed with clear and rebuild?"):
            return
        desc = "rebuild %s" % self.catalog_id
        self._execute(desc, self._rebuild)


def run_noninteractive(console, args):
    """Handle --indexes / --reindex / --rebuild one-shot invocations
    """
    if not args.catalog:
        print("--indexes/--reindex/--rebuild require --catalog <catalog_id>")
        return
    console.do_select(args.catalog)
    if console.catalog is None:
        return
    if args.do_indexes:
        console.do_indexes("")
        return
    if args.do_reindex is not None:
        console.do_reindex(args.do_reindex)
    elif args.do_rebuild:
        # bypass the interactive confirm: passing --rebuild is the intent
        desc = "rebuild %s" % console.catalog_id
        console._execute(desc, console._rebuild)
    else:
        return
    finish_noninteractive(console, args.do_commit)


def run(app):
    args, _ = parser.parse_known_args()
    site = bootstrap(app, args)
    console = CatalogConsole(app, site, verbose=args.verbose)

    if args.do_indexes or args.do_reindex is not None or args.do_rebuild:
        run_noninteractive(console, args)
        return

    if args.catalog:
        console.do_select(args.catalog)
    console.cmdloop()


if __name__ == "__main__":
    run(app)  # noqa: F821
