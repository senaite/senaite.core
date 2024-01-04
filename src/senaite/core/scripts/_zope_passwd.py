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

import transaction
from senaite.core import logger
from senaite.core.scripts import parser

__doc__ = """Change the password of a ZOPE emergency user or creates a new user
if the specified user was not found in the database.
"""

parser.description = __doc__
parser.add_argument("-u", "--user",
                    dest="user", default="admin", type=str,
                    help="Emergency user name (default: %(default)s)")
parser.add_argument("-p", "--password",
                    dest="password", default="admin", type=str,
                    help="Password to set (default: %(default)s)")


def run(app):
    args, _ = parser.parse_known_args()
    user = args.user
    password = args.password
    users = app.acl_users.users
    try:
        users.updateUserPassword(user, password)
        logger.debug("Password changed for user %s" % user)
    except KeyError:
        users.addUser(user, user, password)
        logger.debug("New user %s created changed for user %s" % user)
    transaction.commit()


if __name__ == "__main__":
    run(app) # noqa: F821
