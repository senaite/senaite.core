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

import argparse

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from bika.lims import api
from senaite.core import logger
from senaite.core.scripts import parser
from senaite.core.scripts.utils import setup_site
from senaite.core.decorators import retriable

__doc__ = """Reindex objects in SENAITE
"""

parser.description = __doc__
parser.add_argument("-r", "--recursive", default=False,
                    dest="recursive", action="store_true",
                    help="Reindex objects recursively (default: %(default)s)")
parser.add_argument("-p", "--path",
                    dest="path", default=None, type=str,
                    help="Path to reindex (default: %(default)s)")


def recursive_reindex(obj, recursive=False):
    """Reindex object
    """
    if not api.is_object(obj):
        return
    logger.debug("Reindexing %s" % api.get_path(obj))
    obj.reindexObject()
    if recursive and hasattr(aq_base(obj), "objectItems"):
        for child in obj.objectValues():
            recursive_reindex(child, recursive=recursive)


@retriable(sync=True)
def reindex(path, recursive=False):
    """Reindex path
    """
    obj = api.get_object_by_path(path)
    recursive_reindex(obj, recursive=recursive)
    transaction.commit()


def run(app):
    args, _ = parser.parse_known_args()

    site = None
    sid = args.site_id or "senaite"
    site = app.get(sid)
    if site:
        setup_site(site)
    else:
        raise argparse.ArgumentError(
            "No SENAITE site with ID '%s' found" % sid)

    user = app.acl_users.getUser("admin")
    newSecurityManager(None, user.__of__(app.acl_users))

    path = args.path or "/%s" % sid
    recursive = args.recursive
    reindex(path, recursive=recursive)


if __name__ == "__main__":
    run(app) # noqa: F821
