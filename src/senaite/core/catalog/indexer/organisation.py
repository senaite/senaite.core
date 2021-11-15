# -*- coding: utf-8 -*-

from bika.lims.interfaces import IOrganisation
from plone.indexer import indexer


@indexer(IOrganisation)
def title(instance):
    """Organisation objects does not use the built-in title, rather it uses
    Name schema field. We need this type-specific index to simulate the default
    behavior for index `title`
    """
    name = getattr(instance, "Name", None)
    return name or ""
