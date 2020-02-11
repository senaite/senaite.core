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

from plone.memoize import ram
from zope.component import queryUtility
from zope.i18n.interfaces import ITranslationDomain
from jarn.jsi18n.view import i18njs as BaseView
from jarn.jsi18n.view import _cache_key


class i18njs(BaseView):

    @ram.cache(_cache_key)
    def _gettext_catalog(self, domain, language):
        """
        Overrides jarn.jsi18n.view.jsi18n
        See:
            https://github.com/collective/jarn.jsi18n/issues/1
            https://github.com/collective/jarn.jsi18n/pull/2

        :param domain: translation domain
        :param language: iso code for language
        :return: dict, with the translations for the domain and language
        """
        td = queryUtility(ITranslationDomain, domain)
        if td is None or language not in td._catalogs:
            return

        # N.B. Multiple PO files might be registered for one language, where
        # usually the one at position 0 is the custom catalog with the
        # overriding terms in it. Therefore, we need to reverse the order, so
        # that the custom catalog wins.
        _catalog = {}
        for mo_path in reversed(td._catalogs[language]):
            catalog = td._data[mo_path]._catalog
            if catalog is None:
                td._data[mo_path].reload()
                catalog = td._data[mo_path]._catalog
            catalog = catalog._catalog
            for key, val in catalog.iteritems():
                if key and val:
                    _catalog[key] = val
        return _catalog
