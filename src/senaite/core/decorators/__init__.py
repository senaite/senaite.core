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

from functools import wraps

import transaction
from bika.lims import api
from senaite.core import logger
from ZODB.POSException import ConflictError


def readonly_transaction(func):
    """Decorator to doom the current transaction

    https://transaction.readthedocs.io/en/latest/doom.html#dooming-transactions
    """
    @wraps(func)
    def decorator(self, *args, **kwargs):
        logger.info("*** READONLY TRANSACTION: '{}.{}' ***".
                    format(self.__class__.__name__, func.__name__))
        tx = transaction.get()
        tx.doom()
        return func(self, *args, **kwargs)
    return decorator


def retriable(count=3, sync=False, reraise=True, on_retry_exhausted=None):
    """Retries DB commits
    """

    def decorator(func):
        def wrapped(*args, **kwargs):
            retried = 0
            if sync:
                try:
                    api.get_portal()._p_jar.sync()
                except Exception:
                    pass
            while retried < count:
                try:
                    return func(*args, **kwargs)
                except ConflictError:
                    retried += 1
                    logger.warn("DB ConflictError: Retrying %s/%s"
                                % (retried, count))
                    try:
                        api.get_portal()._p_jar.sync()
                    except Exception:
                        if retried >= count:
                            if on_retry_exhausted is not None:
                                on_retry_exhausted(*args, **kwargs)
                            if reraise:
                                raise
        return wrapped
    return decorator
