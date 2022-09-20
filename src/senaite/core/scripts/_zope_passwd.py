# -*- coding: utf-8 -*-

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
