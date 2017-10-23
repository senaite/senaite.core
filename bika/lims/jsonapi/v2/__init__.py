# -*- coding: utf-8 -*-

import pkgutil

from bika.lims import logger
from bika.lims.jsonapi.v2 import routes
from bika.lims.jsonapi import add_route as add_bika_route

__version__ = 2
__date__ = "2017-05-13"

BASE_URL = "/v2"


def add_route(route, endpoint=None, **kw):
    """Add a new v2 JSON API route
    """

    # ensure correct amout of slashes
    def apiurl(route):
        return '/'.join(s.strip('/') for s in ["", BASE_URL, route])

    return add_bika_route(apiurl(route), endpoint, **kw)


prefix = routes.__name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(
        routes.__path__, prefix):
    module = __import__(modname, fromlist="dummy")
    logger.info("INITIALIZED BIKA JSON API V2 ROUTE ---> %s" % module.__name__)
