# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import cProfile
import json
import os
from functools import wraps


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
