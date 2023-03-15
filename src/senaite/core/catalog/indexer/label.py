# -*- coding: utf-8 -*-

from bika.lims import api
from plone.indexer import indexer
from senaite.core.api import label as label_api
from senaite.core.interfaces import IHaveLabels


@indexer(IHaveLabels)
def labels(instance):
    """Returns a list of labels for the given instance
    """
    labels = label_api.get_obj_labels(instance)
    return map(api.safe_unicode, labels)
