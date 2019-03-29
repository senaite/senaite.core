# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.interfaces import IBaseObject
from bika.lims import api
from plone.indexer import indexer


@indexer(IBaseObject)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.is_active(instance)
