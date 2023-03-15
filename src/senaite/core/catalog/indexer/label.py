# -*- coding: utf-8 -*-

from senaite.core.api import label as label_api
from plone.indexer import indexer
from senaite.core.interfaces import ICanHaveLabels


@indexer(ICanHaveLabels)
def labels(instance):
    """Returns a list of labels for the given instance
    """
    return label_api.get_obj_labels(instance)
