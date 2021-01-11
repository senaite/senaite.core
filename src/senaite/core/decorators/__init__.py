# -*- coding: utf-8 -*-

from functools import wraps

import transaction
from senaite.core import logger


def readonly_transaction(func):
    """Decorator to doom the current transaction

    https://transaction.readthedocs.io/en/latest/doom.html#dooming-transactions
    """
    @wraps(func)
    def decorator(self, *args, **kwargs):
        logger.info("*** READONLY TRANSACTION: '{}.{}' ***".
                    format(self.__class__.__name__, self.__name__))
        tx = transaction.get()
        tx.doom()
        return func(self, *args, **kwargs)
    return decorator
