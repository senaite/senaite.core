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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.indexer import indexer
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.CatalogTool import sortable_title as plone_sortable_title


@indexer(IBaseObject)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.is_active(instance)


@indexer(IBaseObject)
def sortable_title(instance):
    """Uses the default Plone sortable_text index lower-case
    """
    title = plone_sortable_title(instance)
    if safe_callable(title):
        title = title()
    return title.lower()


def sortable_sortkey_title(instance):
    """Returns a sortable title as a mxin of sortkey + lowercase sortable_title
    """
    title = sortable_title(instance)
    if safe_callable(title):
        title = title()

    sort_key = instance.getSortKey()
    if sort_key is None:
        sort_key = 999999

    return "{:010.3f}{}".format(sort_key, title)
