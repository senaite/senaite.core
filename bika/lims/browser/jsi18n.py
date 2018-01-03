# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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

        _catalog = {}
        for mo_path in td._catalogs[language]:
            catalog = td._data[mo_path]._catalog
            if catalog is None:
                td._data[mo_path].reload()
                catalog = td._data[mo_path]._catalog
            catalog = catalog._catalog
            for key, val in catalog.iteritems():
                if key and val:
                    _catalog[key] = val
        return _catalog
