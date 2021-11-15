# -*- coding: utf-8 -*-

from bika.lims.interfaces import IContact
from plone.indexer import indexer


@indexer(IContact)
def sortable_title(instance):
    return instance.getFullname().lower()
