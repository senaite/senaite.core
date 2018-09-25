# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import cProfile
import json
import os
import time
from functools import wraps

from bika.lims import logger


def returns_json(func):
    """Decorator for functions which return JSON
    """
    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader("Content-Type", "application/json")
        result = func(*args, **kwargs)
        return json.dumps(result)
    return decorator


def profileit(path=None):
    """cProfile decorator to profile a function

    :param path: output file path
    :type path: str
    :return: Function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            if path is not None:
                print prof.print_stats()
                prof.dump_stats(os.path.expanduser(path))
            else:
                print prof.print_stats()
            return retval
        return wrapper
    return inner


def timeit(threshold=0):
    """Decorator to log the execution time of a function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            return_value = func(*args, **kwargs)
            end = time.time()
            duration = float(end-start)
            if duration > threshold:
                logger.info("Execution of '{}{}' took {:2f}s".format(
                    func.__name__, args, duration))
            return return_value
        return wrapper
    return inner
