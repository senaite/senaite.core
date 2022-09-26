# -*- coding: utf-8 -*-

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
