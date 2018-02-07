# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.interface import implements

from plone.indexer import indexer
from plone.dexterity.content import Item

from bika.lims.interfaces import IClientLicenceType
from bika.lims.interfaces import IBikaSetupCatalog


class ClientLicenceType(Item):
    implements(IClientLicenceType)

    # Bika catalog multiplex for Dexterity contents
    # please see event handlers in bika.lims.subscribers.catalogobject
    _bika_catalogs = [
        "bika_setup_catalog"
    ]

@indexer(IClientLicenceType, IBikaSetupCatalog)
def clientlicencetype_title_indexer(obj):
    if obj.title:
        return obj.title

@indexer(IClientLicenceType, IBikaSetupCatalog)
def clientlicencetype_sortable_title_indexer(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]

