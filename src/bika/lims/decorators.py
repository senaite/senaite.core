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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import cProfile
import json
import os
import threading
import time
from functools import wraps

from bika.lims import api
from bika.lims import logger
from senaite.core.supermodel.interfaces import ISuperModel
from zope.component import queryAdapter


def XXX_REMOVEME(func):
    """Decorator for dead code removal
    """
    @wraps(func)
    def decorator(self, *args, **kwargs):
        msg = "~~~~~~~ XXX REMOVEME marked method called: {}.{}".format(
            self.__class__.__name__, func.func_name)
        raise RuntimeError(msg)
        return func(self, *args, **kwargs)
    return decorator


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


def returns_super_model(func):
    """Decorator to return standard content objects as SuperModels
    """
    def to_super_model(obj):
        # avoid circular imports
        from senaite.core.supermodel import SuperModel

        # Object is already a SuperModel
        if isinstance(obj, SuperModel):
            return obj

        # Only portal objects are supported
        if not api.is_object(obj):
            raise TypeError("Expected a portal object, got '{}'"
                            .format(type(obj)))

        # Wrap the object into a specific Publication Object Adapter
        uid = api.get_uid(obj)
        portal_type = api.get_portal_type(obj)

        adapter = queryAdapter(uid, ISuperModel, name=portal_type)
        if adapter is None:
            return SuperModel(uid)
        return adapter

    @wraps(func)
    def wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        if isinstance(obj, (list, tuple)):
            return map(to_super_model, obj)
        return to_super_model(obj)

    return wrapper


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


def timeit(threshold=0, show_args=False):
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
                if show_args:
                    logger.info("Execution of '{}{}' took {:2f}s".format(
                        func.__name__, args, duration))
                else:
                    logger.info("Execution of '{}' took {:2f}s".format(
                        func.__name__, duration))
            return return_value
        return wrapper
    return inner


def synchronized(max_connections=2, verbose=0):
    """Synchronize function call via semaphore
    """
    semaphore = threading.BoundedSemaphore(max_connections, verbose=verbose)

    def inner(func):
        logger.debug("Semaphore for {} -> {}".format(func, semaphore))
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info("==> {}::Acquire Semaphore ...".format(
                    func.__name__))
                semaphore.acquire()
                return func(*args, **kwargs)
            finally:
                logger.info("<== {}::Release Semaphore ...".format(
                    func.__name__))
                semaphore.release()

        return wrapper
    return inner
