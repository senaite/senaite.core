# -*- coding: utf-8 -*-

import json
import time
from functools import wraps

from bika.lims import logger
from bika.lims.utils import t
from zope.i18nmessageid import Message
from DateTime import DateTime
from bika.lims import api


def returns_safe_json(func):
    """Returns a safe JSON string
    """
    @wraps(func)
    def wrapper(*args, **kw):
        def default(obj):
            """This function handles unhashable objects
            """
            # Convert `DateTime` objects to ISO8601 format
            if isinstance(obj, DateTime):
                obj = obj.ISO8601()
            # Convert objects and brains to UIDs
            if api.is_object(obj):
                obj = api.get_uid(obj)
            if isinstance(obj, basestring):
                return obj
            return str(obj)

        data = func(*args, **kw)
        return json.dumps(data, default=default)
    return wrapper


def set_application_json_header(func):
    """Returns a safe JSON string
    """
    @wraps(func)
    def wrapper(*args, **kw):
        # set the content type header
        request = api.get_request()
        request.response.setHeader("Content-Type", "application/json")
        return func(*args, **kw)
    return wrapper


def translate(func):
    """Translate i18n `Message` objects in data structures

    N.B. This is needed because only page templates translate i18n Message
            objects directly on rendering, but not when they are used in a JS
            application.
    """
    @wraps(func)
    def wrapper(*args, **kw):
        def translate_thing(thing):
            # Deconstruct lists
            if isinstance(thing, list):
                return map(translate_thing, thing)
            # Deconstruct dictionaries
            if isinstance(thing, dict):
                for key, value in thing.items():
                    thing[key] = translate_thing(value)
            # Translate i18n Message strings
            if isinstance(thing, Message):
                return t(thing)
            return thing
        data = func(*args, **kw)
        return translate_thing(data)
    return wrapper


def inject_runtime(func):
    """Measure runtime of the decorated function and inject it into the
    returning dictionary
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        # inject the runtime into the returning dictionary
        result.update(dict(_runtime=duration))
        logger.info("Execution of '{}' took {:2f}s".format(
            func.__name__, duration))
        return result
    return wrapper
