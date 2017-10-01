# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone.jsonapi.core import router

from bika.lims import logger


def add_route(route, endpoint=None, **kw):
    """Add a new JSON API route
    """
    def wrapper(f):
        try:
            router.DefaultRouter.add_url_rule(route,
                                              endpoint=endpoint,
                                              view_func=f,
                                              options=kw)
        except AssertionError, e:
            logger.warn("Failed to register route {}: {}".format(route, e))
        return f
    return wrapper


def url_for(endpoint, default="bika.lims.jsonapi.get", **values):
    """Looks up the API URL for the given endpoint

    :param endpoint: The name of the registered route (aka endpoint)
    :type endpoint: string
    :returns: External URL for this endpoint
    :rtype: string/None
    """

    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except Exception:
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.debug("Could not build API URL for endpoint '%s'. "
                     "No route provider registered?" % endpoint)

        # build generic API URL
        return router.url_for(default, force_external=True, values=values)
